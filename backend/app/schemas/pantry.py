from datetime import date, datetime

from pydantic import BaseModel, Field


class PantryItemCreate(BaseModel):
    name: str = Field(min_length=1)
    quantity: float = Field(gt=0)
    unit: str = Field(min_length=1)
    category: str | None = None
    expiry_date: date | None = None


class PantryItemUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1)
    quantity: float | None = Field(default=None, gt=0)
    unit: str | None = Field(default=None, min_length=1)
    category: str | None = None
    expiry_date: date | None = None


class PantryItemResponse(BaseModel):
    id: int
    name: str
    quantity: float
    unit: str
    category: str | None
    expiry_date: date | None
    created_at: datetime

    model_config = {
        "from_attributes": True
    }