import json
from pydantic import ValidationError

from app.core.config import settings
from google import genai

from app.schemas.recipe import GeneratedRecipe


GEMINI_API_KEY = settings.GEMINI_API_KEY

client = None
if GEMINI_API_KEY:
    client = genai.Client(api_key=GEMINI_API_KEY)


MODEL_NAME = "gemini-3.6-flash"


RECIPE_GENERATION_PROMPT = """
You are PantryPilot's expert AI Chef.

The user has the following ingredients available in their kitchen pantry:
{pantry_ingredients}

Generate a creative, delicious, easy-to-cook recipe that uses PRIMARILY these available ingredients.
You may include basic seasonings or staples (salt, pepper, oil, water) if needed.

Provide:
- A catchy recipe name
- A short description
- Estimated cooking time in minutes
- Difficulty level (easy, medium, hard)
- List of ingredients with quantities and units
- Clear step-by-step cooking instructions
"""


def generate_recipe_from_pantry(
    available_ingredients: list[str],
) -> GeneratedRecipe:
    if not client:
        raise RuntimeError("GEMINI_API_KEY is not configured")

    if not available_ingredients:
        available_ingredients = ["Eggs", "Bread", "Tomato", "Cheese"]

    ingredients_text = ", ".join(available_ingredients)
    prompt = RECIPE_GENERATION_PROMPT.format(pantry_ingredients=ingredients_text)

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=[
            {
                "role": "user",
                "parts": [{"text": prompt}],
            }
        ],
        config={
            "response_mime_type": "application/json",
            "response_schema": GeneratedRecipe,
        },
    )

    raw_json_text = response.text

    # Strict Pydantic Validation Step:
    try:
        recipe_result = GeneratedRecipe.model_validate_json(raw_json_text)
        return recipe_result
    except ValidationError as val_err:
        raise ValueError(
            f"Generated recipe failed Pydantic validation: {val_err}"
        ) from val_err
    except json.JSONDecodeError as json_err:
        raise ValueError(
            f"Generated recipe is not valid JSON: {json_err}"
        ) from json_err
