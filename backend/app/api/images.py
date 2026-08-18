import uuid

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    UploadFile,
    status,
)
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.db.dependencies import get_db
from app.models.image import FoodImage
from app.models.user import User
from app.services.storage import (
    upload_image,
    download_image,
)

from app.services.vision_service import detect_food


router = APIRouter(
    prefix="/images",
    tags=["Images"],
)


ALLOWED_CONTENT_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
}

MAX_FILE_SIZE = 10 * 1024 * 1024


@router.post(
    "/upload",
    status_code=status.HTTP_201_CREATED,
)
async def upload_food_image(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only JPEG, PNG, and WebP images are allowed",
        )

    file_data = await file.read()

    if len(file_data) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File size must be less than 10 MB",
        )

    unique_id = uuid.uuid4().hex

    object_name = (
        f"users/{current_user.id}/"
        f"images/{unique_id}_{file.filename}"
    )

    upload_image(
        file_data=file_data,
        object_name=object_name,
        content_type=file.content_type,
    )

    image = FoodImage(
        user_id=current_user.id,
        filename=file.filename,
        storage_key=object_name,
        content_type=file.content_type,
        status="uploaded",
    )

    db.add(image)
    db.commit()
    db.refresh(image)

    return {
        "id": image.id,
        "filename": image.filename,
        "status": image.status,
    }
    
    
@router.post(
    "/{image_id}/detect",
)
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
        image_bytes = download_image(
            image.storage_key
        )

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
        )