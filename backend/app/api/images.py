import mimetypes
import uuid

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    Response,
    UploadFile,
    status,
)
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.db.dependencies import get_db
from app.models.image import FoodImage
from app.models.user import User
from app.services.storage import (
    delete_image,
    download_image,
    upload_image,
)
from app.services.vision_service import detect_food


router = APIRouter(
    prefix="/images",
    tags=["Images"],
)


ALLOWED_CONTENT_TYPES = {
    "image/jpeg",
    "image/jpg",
    "image/pjpeg",
    "image/png",
    "image/x-png",
    "image/webp",
    "image/gif",
}

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


@router.post(
    "/upload",
    status_code=status.HTTP_201_CREATED,
)
async def upload_food_image(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    content_type = file.content_type

    if not content_type or content_type not in ALLOWED_CONTENT_TYPES:
        guessed_type, _ = mimetypes.guess_type(file.filename or "")
        if guessed_type and guessed_type in ALLOWED_CONTENT_TYPES:
            content_type = guessed_type

    if not content_type or content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only JPEG, PNG, WebP, and GIF images are allowed",
        )

    file_data = await file.read()

    if len(file_data) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty",
        )

    if len(file_data) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File size must be less than 10 MB",
        )

    unique_id = uuid.uuid4().hex
    safe_filename = file.filename or "image.jpg"

    object_name = (
        f"users/{current_user.id}/"
        f"images/{unique_id}_{safe_filename}"
    )

    try:
        stored_key = upload_image(
            file_data=file_data,
            object_name=object_name,
            content_type=content_type,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Image upload storage failed: {str(exc)}",
        ) from exc

    image = FoodImage(
        user_id=current_user.id,
        filename=safe_filename,
        storage_key=stored_key or object_name,
        content_type=content_type,
        status="uploaded",
    )

    db.add(image)
    db.commit()
    db.refresh(image)

    return {
        "id": image.id,
        "filename": image.filename,
        "status": image.status,
        "storage_key": image.storage_key,
        "content_type": image.content_type,
        "created_at": image.created_at,
    }


@router.get("")
def list_images(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    images = db.query(FoodImage).filter(
        FoodImage.user_id == current_user.id
    ).all()
    return images


@router.get("/{image_id}")
def get_image_details(
    image_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    image = db.query(FoodImage).filter(
        FoodImage.id == image_id,
        FoodImage.user_id == current_user.id,
    ).first()

    if image is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found",
        )

    return image


@router.get("/{image_id}/content")
def get_image_content(
    image_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    image = db.query(FoodImage).filter(
        FoodImage.id == image_id,
        FoodImage.user_id == current_user.id,
    ).first()

    if image is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found",
        )

    try:
        image_bytes = download_image(image.storage_key)
        return Response(
            content=image_bytes,
            media_type=image.content_type,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve image content: {str(exc)}",
        ) from exc


@router.delete("/{image_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user_image(
    image_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    image = db.query(FoodImage).filter(
        FoodImage.id == image_id,
        FoodImage.user_id == current_user.id,
    ).first()

    if image is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found",
        )

    delete_image(image.storage_key)
    db.delete(image)
    db.commit()


@router.post("/{image_id}/detect")
def detect_food_items(
    image_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    image = db.query(FoodImage).filter(
        FoodImage.id == image_id,
        FoodImage.user_id == current_user.id,
    ).first()

    if image is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found",
        )

    try:
        image_bytes = download_image(image.storage_key)
        result = detect_food(
            image_bytes=image_bytes,
            mime_type=image.content_type,
        )

        image.status = "processed"
        db.commit()

        return {
            "image_id": image.id,
            "status": "processed",
            "items": [
                item.model_dump()
                for item in result.items
            ],
        }

    except Exception as exc:
        image.status = "failed"
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Food detection failed: {str(exc)}",
        ) from exc