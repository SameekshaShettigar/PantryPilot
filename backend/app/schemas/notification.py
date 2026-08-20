from datetime import datetime
from pydantic import BaseModel


class NotificationResponse(BaseModel):
    id: int
    user_id: int
    pantry_item_id: int | None = None
    message: str
    notification_type: str
    is_read: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class NotificationUpdate(BaseModel):
    is_read: bool | None = None


class NotificationCountResponse(BaseModel):
    unread_count: int
