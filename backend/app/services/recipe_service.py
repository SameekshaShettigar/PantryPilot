from sqlalchemy.orm import Session

from app.models.recipe import Recipe
from app.models.pantry_item import PantryItem


def normalize_name(name: str) -> str:
    return name.strip().lower()


def get_user_pantry(
    db: Session,
    user_id: int,
):
    return (
        db.query(PantryItem)
        .filter(PantryItem.user_id == user_id)
        .all()
    )


def calculate_recipe_match(
    recipe: Recipe,
    pantry_items: list[PantryItem],
):
    pantry_names = {
        normalize_name(item.name)
        for item in pantry_items
    }

    matched = []
    missing = []

    for ingredient in recipe.ingredients:

        ingredient_name = normalize_name(
            ingredient.name
        )

        if ingredient_name in pantry_names:
            matched.append(ingredient.name)
        else:
            missing.append(
                {
                    "name": ingredient.name,
                    "quantity": ingredient.quantity,
                    "unit": ingredient.unit,
                }
            )

    total = len(recipe.ingredients)

    if total == 0:
        match_percentage = 0
    else:
        match_percentage = (
            len(matched) / total
        ) * 100

    return {
        "match_percentage": round(
            match_percentage,
            2,
        ),
        "matched_ingredients": matched,
        "missing_ingredients": missing,
        "can_make": len(missing) == 0,
    }


def recommend_recipes(
    db: Session,
    user_id: int,
):
    pantry_items = get_user_pantry(
        db,
        user_id,
    )

    recipes = db.query(Recipe).all()

    recommendations = []

    for recipe in recipes:

        match = calculate_recipe_match(
            recipe,
            pantry_items,
        )

        recommendations.append(
            {
                "recipe": recipe,
                **match,
            }
        )

    recommendations.sort(
        key=lambda x: x["match_percentage"],
        reverse=True,
    )

    return recommendations