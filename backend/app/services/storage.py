from io import BytesIO
from minio import Minio

from app.core.config import settings


client = Minio(
    settings.MINIO_ENDPOINT,
    access_key=settings.MINIO_ACCESS_KEY,
    secret_key=settings.MINIO_SECRET_KEY,
    secure=False,
)

BUCKET_NAME = settings.MINIO_BUCKET_NAME


def ensure_bucket_exists():
    try:
        if not client.bucket_exists(BUCKET_NAME):
            client.make_bucket(BUCKET_NAME)
    except Exception as exc:
        raise RuntimeError(
            f"Could not ensure MinIO bucket '{BUCKET_NAME}' exists: {exc}"
        ) from exc


def upload_image(
    file_data: bytes,
    object_name: str,
    content_type: str,
):
    ensure_bucket_exists()
    file_stream = BytesIO(file_data)

    client.put_object(
        bucket_name=BUCKET_NAME,
        object_name=object_name,
        data=file_stream,
        length=len(file_data),
        content_type=content_type,
    )


def download_image(
    object_name: str,
) -> bytes:
    response = client.get_object(
        BUCKET_NAME,
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
    try:
        client.remove_object(
            BUCKET_NAME,
            object_name,
        )
    except Exception:
        pass