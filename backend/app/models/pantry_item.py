from sqlalchemy import Column, Date, DateTime, Float, Integer, String
from sqlalchemy.sql import func

from app.db.database import Base


class PantryItem(Base):
    __tablename__ = "pantry_items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    quantity = Column(Float, nullable=False)
    unit = Column(String, nullable=False)
    category = Column(String, nullable=True)
    expiry_date = Column(Date, nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )