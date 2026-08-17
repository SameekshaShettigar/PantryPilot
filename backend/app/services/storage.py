from io import BytesIO

from minio import Minio


MINIO_ENDPOINT = "localhost:9010"
MINIO_ACCESS_KEY = "minioadmin"
MINIO_SECRET_KEY = "minioadmin"

BUCKET_NAME = "pantrypilot-images"


client = Minio(
    MINIO_ENDPOINT,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=False,
)


def upload_image(
    file_data: bytes,
    object_name: str,
    content_type: str,
):
    file_stream = BytesIO(file_data)

    client.put_object(
        bucket_name=BUCKET_NAME,
        object_name=object_name,
        data=file_stream,
        length=len(file_data),
        content_type=content_type,
    )