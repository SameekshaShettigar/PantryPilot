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
    Returns the secure HTTPS CDN URL or storage key.
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
        
        # Clean public_id formatting for Cloudinary compatibility
        clean_public_id = object_name.rsplit(".", 1)[0] if "." in object_name else object_name
        
        res = cloudinary.uploader.upload(
            file_data,
            public_id=clean_public_id,
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
    Handles Cloudinary URLs, MinIO keys, and falls back gracefully on 404s.
    """
    if is_cloudinary_enabled():
        # 1. If object_name is already a full HTTPS URL, fetch directly
        if object_name.startswith("http://") or object_name.startswith("https://"):
            try:
                res = requests.get(object_name, timeout=10)
                if res.status_code == 200:
                    return res.content
            except Exception:
                pass

        # 2. Try fetching from Cloudinary constructed URLs
        clean_name = object_name.strip("/")
        candidate_urls = [
            f"https://res.cloudinary.com/{settings.CLOUDINARY_CLOUD_NAME}/image/upload/{clean_name}",
            f"https://res.cloudinary.com/{settings.CLOUDINARY_CLOUD_NAME}/image/upload/v1/{clean_name}",
        ]

        for url in candidate_urls:
            try:
                res = requests.get(url, timeout=10)
                if res.status_code == 200:
                    return res.content
            except Exception:
                pass

        # 3. Graceful Fallback: Valid 1x1 JPEG byte stream to prevent 500 crash on legacy 404 records
        return b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00`\x00`\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.' \",#\x1c\x1c(7),01444\x1f'9=82<.342\xff\xc0\x00\x0b\x08\x00\x01\x00\x01\x01\x01\x11\x00\xff\xc4\x00\x1f\x00\x00\x01\x05\x01\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\xff\xda\x00\x08\x01\x01\x00\x00?\x00\xbf\x00\xff\xd9"
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
            if "cloudinary.com" in object_name:
                pub_id = object_name.split("/upload/")[-1].rsplit(".", 1)[0]
                if "/v" in pub_id:
                    pub_id = pub_id.split("/", 1)[-1]
            else:
                pub_id = object_name.rsplit(".", 1)[0] if "." in object_name else object_name
            cloudinary.uploader.destroy(pub_id)
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