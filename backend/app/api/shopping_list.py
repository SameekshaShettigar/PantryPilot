from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.db.dependencies import get_db
from app.models.shopping_list import ShoppingListItem
from app.models.user import User
from app.schemas.shopping_list import (
    ShoppingListItemBatchCreate,
    ShoppingListItemCreate,
    ShoppingListItemResponse,
    ShoppingListItemUpdate,
)


router = APIRouter(
    prefix="/shopping-list",
    tags=["Shopping List"],
)


@router.get("", response_model=list[ShoppingListItemResponse])
def get_shopping_list(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items = (
        db.query(ShoppingListItem)
        .filter(ShoppingListItem.user_id == current_user.id)
        .order_by(ShoppingListItem.is_completed.asc(), ShoppingListItem.id.desc())
        .all()
    )
    return items


@router.post(
    "",
    response_model=ShoppingListItemResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_shopping_list_item(
    item_data: ShoppingListItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_item = ShoppingListItem(
        **item_data.model_dump(),
        user_id=current_user.id,
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


@router.post(
    "/batch",
    response_model=list[ShoppingListItemResponse],
    status_code=status.HTTP_201_CREATED,
)
def create_shopping_list_batch(
    batch_data: ShoppingListItemBatchCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    created_items = []
    for item_data in batch_data.items:
        db_item = ShoppingListItem(
            **item_data.model_dump(),
            user_id=current_user.id,
        )
        db.add(db_item)
        created_items.append(db_item)

    db.commit()
    for db_item in created_items:
        db.refresh(db_item)

    return created_items


@router.patch("/{item_id}", response_model=ShoppingListItemResponse)
def update_shopping_list_item(
    item_id: int,
    item_data: ShoppingListItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    item = (
        db.query(ShoppingListItem)
        .filter(
            ShoppingListItem.id == item_id,
            ShoppingListItem.user_id == current_user.id,
        )
        .first()
    )

    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shopping list item not found",
        )

    update_dict = item_data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(item, key, value)

    db.commit()
    db.refresh(item)
    return item


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_shopping_list_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    item = (
        db.query(ShoppingListItem)
        .filter(
            ShoppingListItem.id == item_id,
            ShoppingListItem.user_id == current_user.id,
        )
        .first()
    )

    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shopping list item not found",
        )

    db.delete(item)
    db.commit()
