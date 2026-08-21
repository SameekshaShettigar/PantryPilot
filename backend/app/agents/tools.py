from datetime import date, timedelta
from typing import Any
from sqlalchemy.orm import Session

from app.models.pantry_item import PantryItem
from app.models.recipe import Recipe
from app.models.shopping_list import ShoppingListItem
from app.services.recipe_engine import rank_recipes_for_pantry
from app.services.recipe_generation_service import generate_recipe_from_pantry
from app.services.redis_service import delete_cache


def tool_get_pantry_items(db: Session, user_id: int) -> list[dict[str, Any]]:
    """
    Fetches all items currently stored in the user's kitchen pantry.
    """
    items = db.query(PantryItem).filter(PantryItem.user_id == user_id).all()
    return [
        {
            "id": i.id,
            "name": i.name,
            "quantity": i.quantity,
            "unit": i.unit,
            "category": i.category,
            "expiry_date": i.expiry_date.isoformat() if i.expiry_date else None,
        }
        for i in items
    ]


def tool_get_expiring_items(db: Session, user_id: int, days: int = 3) -> list[dict[str, Any]]:
    """
    Fetches pantry items that are expiring within the specified number of days (default 3 days).
    """
    today = date.today()
    threshold = today + timedelta(days=days)

    items = (
        db.query(PantryItem)
        .filter(
            PantryItem.user_id == user_id,
            PantryItem.expiry_date.isnot(None),
            PantryItem.expiry_date <= threshold,
        )
        .all()
    )

    result = []
    for i in items:
        days_left = (i.expiry_date - today).days
        result.append(
            {
                "id": i.id,
                "name": i.name,
                "quantity": i.quantity,
                "unit": i.unit,
                "category": i.category,
                "expiry_date": i.expiry_date.isoformat(),
                "days_remaining": days_left,
                "status": "expired" if days_left < 0 else "expiring_soon",
            }
        )
    return result


def tool_add_pantry_item(
    db: Session,
    user_id: int,
    name: str,
    quantity: float = 1.0,
    unit: str = "pieces",
    category: str = "Other",
    expiry_date: str | None = None,
) -> dict[str, Any]:
    """
    Adds a new ingredient/item to the user's pantry.
    """
    parsed_date = None
    if expiry_date:
        try:
            parsed_date = date.fromisoformat(expiry_date)
        except ValueError:
            pass

    new_item = PantryItem(
        user_id=user_id,
        name=name,
        quantity=quantity,
        unit=unit,
        category=category,
        expiry_date=parsed_date,
    )
    db.add(new_item)
    db.commit()
    db.refresh(new_item)

    # Invalidate recommendation cache
    delete_cache(f"user:{user_id}:recommendations")

    return {
        "success": True,
        "message": f"Added {name} to pantry",
        "item": {
            "id": new_item.id,
            "name": new_item.name,
            "quantity": new_item.quantity,
            "unit": new_item.unit,
        },
    }


def tool_get_recipe_recommendations(db: Session, user_id: int) -> list[dict[str, Any]]:
    """
    Recommends recipes from the catalog based on available pantry items and expiring ingredients.
    """
    pantry_items = db.query(PantryItem).filter(PantryItem.user_id == user_id).all()
    recipes = db.query(Recipe).all()

    ranked = rank_recipes_for_pantry(recipes=recipes, pantry_items=pantry_items)
    return [rec.model_dump(mode="json") for rec in ranked]


def tool_generate_recipe(db: Session, user_id: int, prompt_hint: str = "") -> dict[str, Any]:
    """
    Generates a custom AI recipe based on the user's available pantry ingredients and optional prompt.
    """
    pantry_items = db.query(PantryItem).filter(PantryItem.user_id == user_id).all()
    available_names = [p.name for p in pantry_items]

    recipe_obj = generate_recipe_from_pantry(available_names)
    return recipe_obj.model_dump(mode="json")


def tool_get_shopping_list(db: Session, user_id: int) -> list[dict[str, Any]]:
    """
    Fetches the user's current shopping list.
    """
    items = db.query(ShoppingListItem).filter(ShoppingListItem.user_id == user_id).all()
    return [
        {
            "id": i.id,
            "name": i.name,
            "quantity": i.quantity,
            "unit": i.unit,
            "is_completed": i.is_completed,
        }
        for i in items
    ]


def tool_add_to_shopping_list(
    db: Session,
    user_id: int,
    name: str,
    quantity: float = 1.0,
    unit: str = "pieces",
    category: str = "Other",
) -> dict[str, Any]:
    """
    Adds an item to the user's shopping list.
    """
    new_item = ShoppingListItem(
        user_id=user_id,
        name=name,
        quantity=quantity,
        unit=unit,
        category=category,
        is_completed=False,
    )
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return {
        "success": True,
        "message": f"Added {name} to shopping list",
        "id": new_item.id,
    }
