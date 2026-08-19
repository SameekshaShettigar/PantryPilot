from pydantic import BaseModel, Field


class DetectedFood(BaseModel):
    name: str = Field(
        min_length=1,
        description="Common name of the food item."
    )

    category: str = Field(
        default="Other",
        description="Food category such as Dairy, Fruit, Vegetable, Grain, Protein, Beverage, Snack, or Other."
    )

    estimated_quantity: float = Field(
        default=1.0,
        ge=0.0,
        description="Estimated number or amount visible."
    )

    unit: str = Field(
        default="pieces",
        min_length=1,
        description="Unit such as pieces, container, bottle, packet, kg, litre, etc."
    )

    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Confidence score between 0.0 and 1.0 (e.g. 0.95 for 95%)."
    )

    accept: bool = Field(
        default=True,
        description="Suggested human-in-the-loop selection status (True if confidence >= 0.5)."
    )


class FoodDetectionResponse(BaseModel):
    items: list[DetectedFood]