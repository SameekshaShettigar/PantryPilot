from pydantic import BaseModel, Field


class RecipeIngredientSchema(BaseModel):
    name: str
    quantity: float | None = None
    unit: str | None = None

    model_config = {"from_attributes": True}


class RecipeResponse(BaseModel):
    id: int
    name: str
    description: str | None = None
    cooking_time: int | None = None
    difficulty: str | None = None
    instructions: str
    ingredients: list[RecipeIngredientSchema]

    model_config = {"from_attributes": True}


class ExpiringIngredientDetail(BaseModel):
    name: str
    days_until_expiry: int | None = None


class RecipeRecommendation(BaseModel):
    recipe: RecipeResponse
    match_percentage: float = Field(
        description="Percentage of required ingredients available in user pantry (0-100)."
    )
    available_ingredients: list[str]
    missing_ingredients: list[str]
    expiring_ingredients_used: list[ExpiringIngredientDetail] = []
    is_expiring_soon_priority: bool = Field(
        default=False,
        description="True if recipe helps consume ingredients expiring soon.",
    )
    rank_score: float = Field(
        description="Calculated recommendation score based on match percentage and expiring urgency."
    )


class GeneratedRecipeIngredient(BaseModel):
    name: str = Field(min_length=1)
    quantity: float = Field(default=1.0, ge=0.0)
    unit: str = Field(default="pieces", min_length=1)


class GeneratedRecipe(BaseModel):
    name: str = Field(min_length=1)
    description: str = Field(default="")
    cooking_time: int = Field(default=15, ge=1)
    difficulty: str = Field(default="easy")
    ingredients: list[GeneratedRecipeIngredient] = Field(min_items=1)
    instructions: str = Field(min_length=5)