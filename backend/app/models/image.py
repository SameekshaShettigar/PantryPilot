from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.sql import func

from app.db.database import Base


class FoodImage(Base):
    __tablename__ = "food_images"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    filename = Column(
        String,
        nullable=False,
    )

    storage_key = Column(
        String,
        nullable=False,
    )

    status = Column(
        String,
        nullable=False,
        default="uploaded",
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )