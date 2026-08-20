import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.db.dependencies import get_db
from app.models.pantry_item import PantryItem
from app.models.user import User
from app.schemas.pantry import (
    PantryItemCreate,
    PantryItemResponse,
    PantryItemUpdate,
)
from app.services.redis_service import delete_cache

logger = logging.getLogger("pantrypilot.pantry")

router = APIRouter(
    prefix="/pantry",
    tags=["Pantry"]
)


def invalidate_user_recommendation_cache(user_id: int):
    cache_key = f"user:{user_id}:recommendations"
    delete_cache(cache_key)
    print(f"[CACHE INVALIDATED] Recommendation cache cleared for user {user_id}")
    logger.info(f"[CACHE INVALIDATED] Recommendation cache cleared for user {user_id}")


@router.post(
    "",
    response_model=PantryItemResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_pantry_item(
    item: PantryItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_item = PantryItem(
        **item.model_dump(),
        user_id=current_user.id,
    )

    db.add(db_item)
    db.commit()
    db.refresh(db_item)

    # Invalidate Redis recommendation cache on pantry change
    invalidate_user_recommendation_cache(current_user.id)

    return db_item


@router.post(
    "/batch",
    response_model=list[PantryItemResponse],
    status_code=status.HTTP_201_CREATED,
)
def create_pantry_items_batch(
    items: list[PantryItemCreate],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_items = []
    for item in items:
        db_item = PantryItem(
            **item.model_dump(),
            user_id=current_user.id,
        )
        db.add(db_item)
        db_items.append(db_item)

    db.commit()
    for db_item in db_items:
        db.refresh(db_item)

    # Invalidate Redis recommendation cache on batch pantry change
    invalidate_user_recommendation_cache(current_user.id)

    return db_items


@router.get(
    "",
    response_model=list[PantryItemResponse],
)
def get_pantry_items(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return db.query(PantryItem).filter(
        PantryItem.user_id == current_user.id
    ).all()


@router.get(
    "/{item_id}",
    response_model=PantryItemResponse,
)
def get_pantry_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    item = db.query(PantryItem).filter(
        PantryItem.id == item_id,
        PantryItem.user_id == current_user.id,
    ).first()

    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pantry item not found",
        )

    return item


@router.patch(
    "/{item_id}",
    response_model=PantryItemResponse,
)
def update_pantry_item(
    item_id: int,
    item_data: PantryItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    item = db.query(PantryItem).filter(
        PantryItem.id == item_id,
        PantryItem.user_id == current_user.id,
    ).first()

    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pantry item not found",
        )

    update_data = item_data.model_dump(
        exclude_unset=True
    )

    for key, value in update_data.items():
        setattr(item, key, value)

    db.commit()
    db.refresh(item)

    # Invalidate Redis recommendation cache on pantry update
    invalidate_user_recommendation_cache(current_user.id)

    return item


@router.delete(
    "/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_pantry_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    item = db.query(PantryItem).filter(
        PantryItem.id == item_id,
        PantryItem.user_id == current_user.id,
    ).first()

    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pantry item not found",
        )

    db.delete(item)
    db.commit()

    # Invalidate Redis recommendation cache on pantry deletion
    invalidate_user_recommendation_cache(current_user.id)