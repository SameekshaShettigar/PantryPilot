from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.database import Base


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    pantry_item_id = Column(
        Integer,
        ForeignKey("pantry_items.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )

    message = Column(String(500), nullable=False)

    notification_type = Column(
        String(50),
        nullable=False,
        default="warning",  # warning, urgent, critical
    )

    is_read = Column(
        Boolean,
        default=False,
        nullable=False,
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    user = relationship("User")
    pantry_item = relationship("PantryItem")
