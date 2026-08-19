import json

from google import genai

from app.core.config import settings


client = genai.Client(
    api_key=settings.GEMINI_API_KEY
)


def generate_recipe(
    pantry_items: list[str],
    additional_instructions: str | None = None,
):

    ingredients_text = ", ".join(
        pantry_items
    )

    prompt = f"""
You are PantryPilot's recipe generation engine.

The user currently has these ingredients:

{ingredients_text}

Create one practical recipe using primarily
the ingredients available.

Return ONLY valid JSON.

Required JSON structure:

{{
    "name": "recipe name",
    "description": "short description",
    "cooking_time": 15,
    "difficulty": "easy",
    "ingredients": [
        {{
            "name": "ingredient",
            "quantity": 1,
            "unit": "piece"
        }}
    ],
    "instructions": "step-by-step instructions"
}}

Do not invent unrealistic quantities.

Additional user instructions:

{additional_instructions or "None"}
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )

    text = response.text.strip()

    if text.startswith("```"):
        text = text.replace(
            "```json",
            "",
        ).replace(
            "```",
            "",
        ).strip()

    return json.loads(text)