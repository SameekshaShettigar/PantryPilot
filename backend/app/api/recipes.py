import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.db.dependencies import get_db
from app.db.seed_recipes import seed_recipes_if_empty
from app.models.pantry_item import PantryItem
from app.models.recipe import Recipe
from app.models.user import User
from app.schemas.recipe import (
    GeneratedRecipe,
    RecipeRecommendation,
    RecipeResponse,
)
from app.services.recipe_engine import rank_recipes_for_pantry
from app.services.recipe_generation_service import generate_recipe_from_pantry
from app.services.redis_service import get_cache, set_cache

logger = logging.getLogger("pantrypilot.recipes")

router = APIRouter(
    prefix="/recipes",
    tags=["Recipes"],
)


@router.get("", response_model=list[RecipeResponse])
def get_all_recipes(
    db: Session = Depends(get_db),
):
    seed_recipes_if_empty(db)
    recipes = db.query(Recipe).all()
    return recipes


@router.get("/{recipe_id}", response_model=RecipeResponse)
def get_recipe_by_id(
    recipe_id: int,
    db: Session = Depends(get_db),
):
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if recipe is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe not found",
        )
    return recipe


@router.post("/recommend", response_model=list[RecipeRecommendation])
def recommend_recipes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    seed_recipes_if_empty(db)

    # User-specific cache key to ensure user data isolation
    cache_key = f"user:{current_user.id}:recommendations"

    # 1. Check Redis Cache (Cache-Aside Pattern)
    cached_recommendations = get_cache(cache_key)

    if cached_recommendations is not None:
        print(f"[CACHE HIT] Recommendations retrieved from Redis for user {current_user.id}")
        logger.info(f"[CACHE HIT] Recommendations retrieved from Redis for user {current_user.id}")
        # Convert cached dicts back into Pydantic models matching response schema
        return [RecipeRecommendation.model_validate(item) for item in cached_recommendations]

    # 2. Cache Miss: Query PostgreSQL & calculate fresh recommendations
    print(f"[CACHE MISS] Calculating fresh recommendations from PostgreSQL for user {current_user.id}")
    logger.info(f"[CACHE MISS] Calculating fresh recommendations from PostgreSQL for user {current_user.id}")

    pantry_items = db.query(PantryItem).filter(
        PantryItem.user_id == current_user.id
    ).all()

    recipes = db.query(Recipe).all()

    ranked_recommendations = rank_recipes_for_pantry(
        recipes=recipes,
        pantry_items=pantry_items,
    )

    # 3. Store calculated recommendations in Redis with a 5-minute (300s) TTL
    serializable_data = [rec.model_dump(mode="json") for rec in ranked_recommendations]
    set_cache(key=cache_key, value=serializable_data, expiration=300)

    return ranked_recommendations


@router.post("/generate", response_model=GeneratedRecipe)
def generate_custom_recipe(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    pantry_items = db.query(PantryItem).filter(
        PantryItem.user_id == current_user.id
    ).all()

    available_ingredient_names = [p.name for p in pantry_items]

    try:
        generated = generate_recipe_from_pantry(available_ingredient_names)
        return generated
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Recipe generation failed: {str(exc)}",
        ) from exc