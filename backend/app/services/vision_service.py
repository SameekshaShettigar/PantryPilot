import base64
import json
from pydantic import ValidationError

from app.core.config import settings
from google import genai

from app.schemas.vision import FoodDetectionResponse


GEMINI_API_KEY = settings.GEMINI_API_KEY

client = None
if GEMINI_API_KEY:
    client = genai.Client(api_key=GEMINI_API_KEY)


MODEL_NAME = "gemini-3.6-flash"


FOOD_DETECTION_PROMPT = """
You are PantryPilot's food recognition system.

Analyze the provided kitchen, refrigerator, pantry, or food image.

Identify visible food and beverage items.

For each clearly identifiable item, provide:
- common food name
- category (such as Dairy, Fruit, Vegetable, Grain, Protein, Beverage, Snack, or Other)
- estimated quantity (numeric float, >= 0.0)
- unit (e.g. pieces, container, bottle, packet, kg, litre)
- confidence score strictly between 0.0 and 1.0 (e.g. 0.95)

Rules:
1. Only report items that are actually visible.
2. Do not invent items.
3. If an item cannot reasonably be identified, do not include it.
4. Confidence MUST be a float between 0.0 and 1.0 inclusive.
"""


def detect_food(
    image_bytes: bytes,
    mime_type: str,
) -> FoodDetectionResponse:
    if not client:
        raise RuntimeError("GEMINI_API_KEY is not configured")

    image_base64 = base64.b64encode(image_bytes).decode("utf-8")

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=[
            {
                "role": "user",
                "parts": [
                    {"text": FOOD_DETECTION_PROMPT},
                    {
                        "inline_data": {
                            "mime_type": mime_type,
                            "data": image_base64,
                        }
                    },
                ],
            }
        ],
        config={
            "response_mime_type": "application/json",
            "response_schema": FoodDetectionResponse,
        },
    )

    raw_json_text = response.text

    # Strict Pydantic Validation Step:
    # We parse Gemini's raw JSON and validate every field against Pydantic schema rules
    # (e.g., confidence must be between 0.0 and 1.0).
    try:
        detection_result = FoodDetectionResponse.model_validate_json(raw_json_text)
    except ValidationError as val_err:
        raise ValueError(
            f"Gemini output failed Pydantic validation: {val_err}"
        ) from val_err
    except json.JSONDecodeError as json_err:
        raise ValueError(
            f"Gemini output is not valid JSON: {json_err}"
        ) from json_err

    # Compute initial suggested human-in-the-loop accept state based on confidence score (e.g. >= 0.50)
    for item in detection_result.items:
        item.accept = item.confidence >= 0.50

    return detection_result