from datetime import datetime
from pydantic import BaseModel, Field


class ShoppingListItemCreate(BaseModel):
    name: str = Field(min_length=1)
    quantity: str | None = None
    unit: str | None = None
    category: str | None = "Other"


class ShoppingListItemBatchCreate(BaseModel):
    items: list[ShoppingListItemCreate] = Field(min_items=1)


class ShoppingListItemUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1)
    quantity: str | None = None
    unit: str | None = None
    category: str | None = None
    is_completed: bool | None = None


class ShoppingListItemResponse(BaseModel):
    id: int
    user_id: int
    name: str
    quantity: str | None = None
    unit: str | None = None
    category: str | None = "Other"
    is_completed: bool
    created_at: datetime

    model_config = {"from_attributes": True}
