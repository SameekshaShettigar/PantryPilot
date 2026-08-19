from datetime import date, timedelta
import re

from app.models.pantry_item import PantryItem
from app.models.recipe import Recipe
from app.schemas.recipe import (
    ExpiringIngredientDetail,
    RecipeRecommendation,
    RecipeResponse,
)


def normalize_ingredient(name: str) -> str:
    """
    Normalizes ingredient text for flexible matching (lowercase, strip, basic plural removal).
    """
    clean = name.strip().lower()
    clean = re.sub(r"[^\w\s]", "", clean)

    # Basic plural normalization
    if clean.endswith("ies"):
        clean = clean[:-3] + "y"
    elif clean.endswith("es") and len(clean) > 4 and not clean.endswith("cheese"):
        clean = clean[:-2]
    elif clean.endswith("s") and len(clean) > 3 and not clean.endswith("ss"):
        clean = clean[:-1]

    return clean


def is_ingredient_match(recipe_ing_name: str, pantry_ing_name: str) -> bool:
    """
    Determines if a recipe ingredient matches a pantry item name.
    """
    norm_rec = normalize_ingredient(recipe_ing_name)
    norm_pan = normalize_ingredient(pantry_ing_name)

    if norm_rec == norm_pan:
        return True
    if norm_rec in norm_pan or norm_pan in norm_rec:
        return True

    return False


def rank_recipes_for_pantry(
    recipes: list[Recipe],
    pantry_items: list[PantryItem],
    today: date | None = None,
) -> list[RecipeRecommendation]:
    if today is None:
        today = date.today()

    expiry_threshold = today + timedelta(days=3)
    recommendations = []

    for recipe in recipes:
        total_ingredients = len(recipe.ingredients)
        if total_ingredients == 0:
            continue

        available_ingredients = []
        missing_ingredients = []
        expiring_used = []

        for req_ing in recipe.ingredients:
            matched_pantry_item = None
            for p_item in pantry_items:
                if is_ingredient_match(req_ing.name, p_item.name):
                    matched_pantry_item = p_item
                    break

            if matched_pantry_item:
                available_ingredients.append(req_ing.name)

                # Check if this matched pantry item is expiring soon
                if matched_pantry_item.expiry_date:
                    days_left = (matched_pantry_item.expiry_date - today).days
                    if matched_pantry_item.expiry_date <= expiry_threshold:
                        expiring_used.append(
                            ExpiringIngredientDetail(
                                name=matched_pantry_item.name,
                                days_until_expiry=days_left,
                            )
                        )
            else:
                missing_ingredients.append(req_ing.name)

        match_count = len(available_ingredients)
        missing_count = len(missing_ingredients)
        match_percentage = round((match_count / total_ingredients) * 100.0, 1)

        expiring_bonus = len(expiring_used) * 15.0
        missing_penalty = missing_count * 5.0

        rank_score = round(match_percentage + expiring_bonus - missing_penalty, 1)
        is_expiring_soon_priority = len(expiring_used) > 0

        recipe_schema = RecipeResponse.model_validate(recipe)

        recommendations.append(
            RecipeRecommendation(
                recipe=recipe_schema,
                match_percentage=match_percentage,
                available_ingredients=available_ingredients,
                missing_ingredients=missing_ingredients,
                expiring_ingredients_used=expiring_used,
                is_expiring_soon_priority=is_expiring_soon_priority,
                rank_score=rank_score,
            )
        )

    # Sort recommendations by rank_score descending, then match_percentage descending
    recommendations.sort(
        key=lambda r: (r.rank_score, r.match_percentage),
        reverse=True,
    )

    return recommendations
