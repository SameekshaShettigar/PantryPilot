import os
import base64

from dotenv import load_dotenv
from google import genai

from app.schemas.vision import FoodDetectionResponse


load_dotenv()


GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY is not configured"
    )


client = genai.Client(
    api_key=GEMINI_API_KEY
)


MODEL_NAME = "gemini-3.6-flash"


FOOD_DETECTION_PROMPT = """
You are PantryPilot's food recognition system.

Analyze the provided kitchen, refrigerator, pantry, or food image.

Identify visible food and beverage items.

For each clearly identifiable item, provide:

- common food name
- category
- estimated quantity
- unit
- confidence score from 0.0 to 1.0

Rules:

1. Only report items that are actually visible.
2. Do not invent items.
3. If an item cannot reasonably be identified, do not include it.
4. If several identical items are visible, estimate their count.
5. Use common everyday food names.
6. Confidence must represent how certain you are that the identification is correct.
7. Quantity is an estimate, so do not pretend it is exact.
8. Return an empty list if no food items can be confidently identified.
"""


def detect_food(
    image_bytes: bytes,
    mime_type: str,
) -> FoodDetectionResponse:

    image_base64 = base64.b64encode(
        image_bytes
    ).decode("utf-8")

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=[
            {
                "role": "user",
                "parts": [
                    {
                        "text": FOOD_DETECTION_PROMPT
                    },
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

    return FoodDetectionResponse.model_validate_json(
        response.text
    )