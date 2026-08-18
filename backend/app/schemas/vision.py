from pydantic import BaseModel, Field


class DetectedFood(BaseModel):
    name: str = Field(
        description="Common name of the food item."
    )

    category: str = Field(
        description="Food category such as Dairy, Fruit, Vegetable, Grain, Protein, Beverage, Snack, or Other."
    )

    estimated_quantity: float | None = Field(
        default=None,
        description="Estimated number or amount visible."
    )

    unit: str | None = Field(
        default=None,
        description="Unit such as pieces, container, bottle, packet, kg, litre, etc."
    )

    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Confidence that this food item is correctly identified."
    )


class FoodDetectionResponse(BaseModel):
    items: list[DetectedFood]