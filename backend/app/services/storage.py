from io import BytesIO
import requests

from app.core.config import settings

# MinIO client instance (loaded lazily when Cloudinary is disabled)
_minio_client = None


def get_minio_client():
    global _minio_client
    if _minio_client is None:
        from minio import Minio

        _minio_client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=False,
        )
    return _minio_client


def is_cloudinary_enabled() -> bool:
    """Returns True if Cloudinary environment variables are configured."""
    return bool(
        settings.CLOUDINARY_CLOUD_NAME
        and settings.CLOUDINARY_API_KEY
        and settings.CLOUDINARY_API_SECRET
    )


def ensure_bucket_exists():
    if is_cloudinary_enabled():
        return
    client = get_minio_client()
    try:
        if not client.bucket_exists(settings.MINIO_BUCKET_NAME):
            client.make_bucket(settings.MINIO_BUCKET_NAME)
    except Exception as exc:
        raise RuntimeError(
            f"Could not ensure MinIO bucket '{settings.MINIO_BUCKET_NAME}' exists: {exc}"
        ) from exc


def upload_image(
    file_data: bytes,
    object_name: str,
    content_type: str,
) -> str:
    """
    Uploads an image to Cloudinary (in production) or MinIO (in local dev).
    Returns the storage key or secure HTTPS URL.
    """
    if is_cloudinary_enabled():
        import cloudinary
        import cloudinary.uploader

        cloudinary.config(
            cloud_name=settings.CLOUDINARY_CLOUD_NAME,
            api_key=settings.CLOUDINARY_API_KEY,
            api_secret=settings.CLOUDINARY_API_SECRET,
            secure=True,
        )
        res = cloudinary.uploader.upload(
            file_data,
            public_id=object_name,
            overwrite=True,
            resource_type="image",
        )
        return res.get("secure_url", object_name)
    else:
        ensure_bucket_exists()
        file_stream = BytesIO(file_data)
        client = get_minio_client()
        client.put_object(
            bucket_name=settings.MINIO_BUCKET_NAME,
            object_name=object_name,
            data=file_stream,
            length=len(file_data),
            content_type=content_type,
        )
        return object_name


def download_image(
    object_name: str,
) -> bytes:
    """
    Downloads image raw bytes for Gemini Vision processing.
    """
    if is_cloudinary_enabled():
        if object_name.startswith("http://") or object_name.startswith("https://"):
            url = object_name
        else:
            url = f"https://res.cloudinary.com/{settings.CLOUDINARY_CLOUD_NAME}/image/upload/{object_name}"
        res = requests.get(url)
        res.raise_for_status()
        return res.content
    else:
        client = get_minio_client()
        response = client.get_object(
            settings.MINIO_BUCKET_NAME,
            object_name,
        )
        try:
            return response.read()
        finally:
            response.close()
            response.release_conn()


def delete_image(
    object_name: str,
):
    """
    Deletes an image from Cloudinary or MinIO.
    """
    if is_cloudinary_enabled():
        import cloudinary
        import cloudinary.uploader

        cloudinary.config(
            cloud_name=settings.CLOUDINARY_CLOUD_NAME,
            api_key=settings.CLOUDINARY_API_KEY,
            api_secret=settings.CLOUDINARY_API_SECRET,
            secure=True,
        )
        try:
            cloudinary.uploader.destroy(object_name)
        except Exception:
            pass
    else:
        client = get_minio_client()
        try:
            client.remove_object(
                settings.MINIO_BUCKET_NAME,
                object_name,
            )
        except Exception:
            pass