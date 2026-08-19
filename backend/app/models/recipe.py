from sqlalchemy import Column, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.db.database import Base


class Recipe(Base):
    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    cooking_time = Column(Integer, nullable=True)  # Minutes
    difficulty = Column(String(50), nullable=True)  # easy, medium, hard
    instructions = Column(Text, nullable=False)

    ingredients = relationship(
        "RecipeIngredient",
        back_populates="recipe",
        cascade="all, delete-orphan",
    )


class RecipeIngredient(Base):
    __tablename__ = "recipe_ingredients"

    id = Column(Integer, primary_key=True, index=True)
    recipe_id = Column(
        Integer,
        ForeignKey("recipes.id", ondelete="CASCADE"),
        nullable=False,
    )
    name = Column(String(200), nullable=False)
    quantity = Column(Float, nullable=True)
    unit = Column(String(50), nullable=True)

    recipe = relationship(
        "Recipe",
        back_populates="ingredients",
    )
