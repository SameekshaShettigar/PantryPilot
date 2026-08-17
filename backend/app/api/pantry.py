from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.auth import get_current_user
from app.models.user import User

from app.db.dependencies import get_db
from app.models.pantry_item import PantryItem
from app.schemas.pantry import (
    PantryItemCreate,
    PantryItemResponse,
    PantryItemUpdate,
)


router = APIRouter(
    prefix="/pantry",
    tags=["Pantry"]
)

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

    return db_item



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