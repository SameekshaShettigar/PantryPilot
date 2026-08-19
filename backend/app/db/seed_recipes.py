from sqlalchemy.orm import Session

from app.models.recipe import Recipe, RecipeIngredient


INITIAL_RECIPES = [
    {
        "name": "Cheese Omelette",
        "description": "Fluffy, classic omelette filled with melted cheese and fresh herbs.",
        "cooking_time": 10,
        "difficulty": "easy",
        "instructions": (
            "1. Beat 2-3 eggs in a bowl with a pinch of salt.\n"
            "2. Heat butter or oil in a non-stick frying pan over medium heat.\n"
            "3. Pour in beaten eggs and cook until edges begin to set.\n"
            "4. Sprinkle grated cheese and diced tomato on one half.\n"
            "5. Fold over, cook for 1 minute until cheese melts, and serve hot."
        ),
        "ingredients": [
            {"name": "eggs", "quantity": 2.0, "unit": "pieces"},
            {"name": "cheese", "quantity": 50.0, "unit": "grams"},
            {"name": "tomato", "quantity": 1.0, "unit": "piece"},
            {"name": "onion", "quantity": 0.5, "unit": "piece"},
            {"name": "salt", "quantity": 1.0, "unit": "pinch"},
        ],
    },
    {
        "name": "Tomato Egg Toast",
        "description": "Crispy toasted bread topped with scrambled eggs and fresh sliced tomatoes.",
        "cooking_time": 15,
        "difficulty": "easy",
        "instructions": (
            "1. Toast slices of bread until golden brown.\n"
            "2. Scramble eggs in a frying pan over medium heat.\n"
            "3. Layer scrambled eggs and sliced tomatoes onto toast.\n"
            "4. Season with salt, pepper, and optional cheese."
        ),
        "ingredients": [
            {"name": "eggs", "quantity": 2.0, "unit": "pieces"},
            {"name": "bread", "quantity": 2.0, "unit": "slices"},
            {"name": "tomato", "quantity": 1.0, "unit": "piece"},
            {"name": "cheese", "quantity": 30.0, "unit": "grams"},
        ],
    },
    {
        "name": "French Toast",
        "description": "Golden, cinnamon-infused French toast perfect for breakfast.",
        "cooking_time": 15,
        "difficulty": "easy",
        "instructions": (
            "1. Whisk eggs, milk, and sugar together in a shallow dish.\n"
            "2. Dip bread slices into mixture until coated.\n"
            "3. Fry in buttered skillet over medium heat until golden on both sides."
        ),
        "ingredients": [
            {"name": "bread", "quantity": 4.0, "unit": "slices"},
            {"name": "eggs", "quantity": 2.0, "unit": "pieces"},
            {"name": "milk", "quantity": 0.25, "unit": "cup"},
            {"name": "sugar", "quantity": 1.0, "unit": "tbsp"},
        ],
    },
    {
        "name": "Creamy Tomato Pasta",
        "description": "Rich and delicious pasta tossed in a creamy garlic tomato sauce.",
        "cooking_time": 25,
        "difficulty": "medium",
        "instructions": (
            "1. Boil pasta in salted water until al dente.\n"
            "2. Sauté minced garlic and diced tomatoes in olive oil.\n"
            "3. Stir in cream and parmesan cheese until smooth.\n"
            "4. Toss pasta with sauce and garnish with herbs."
        ),
        "ingredients": [
            {"name": "pasta", "quantity": 200.0, "unit": "grams"},
            {"name": "tomato", "quantity": 2.0, "unit": "pieces"},
            {"name": "garlic", "quantity": 2.0, "unit": "cloves"},
            {"name": "cream", "quantity": 0.5, "unit": "cup"},
            {"name": "parmesan", "quantity": 50.0, "unit": "grams"},
        ],
    },
    {
        "name": "Vegetable Stir Fry",
        "description": "Crispy mixed vegetables sautéed in a savory soy-garlic sauce.",
        "cooking_time": 20,
        "difficulty": "easy",
        "instructions": (
            "1. Chop onions, capsicum, and carrots into thin strips.\n"
            "2. Heat oil in a wok or large pan on high heat.\n"
            "3. Stir fry garlic and vegetables for 5-7 minutes.\n"
            "4. Add soy sauce and pepper, toss well, and serve hot."
        ),
        "ingredients": [
            {"name": "onion", "quantity": 1.0, "unit": "piece"},
            {"name": "capsicum", "quantity": 1.0, "unit": "piece"},
            {"name": "garlic", "quantity": 2.0, "unit": "cloves"},
            {"name": "carrot", "quantity": 1.0, "unit": "piece"},
            {"name": "soy sauce", "quantity": 2.0, "unit": "tbsp"},
        ],
    },
]


def seed_recipes_if_empty(db: Session):
    existing_count = db.query(Recipe).count()
    if existing_count > 0:
        return

    for item in INITIAL_RECIPES:
        recipe = Recipe(
            name=item["name"],
            description=item["description"],
            cooking_time=item["cooking_time"],
            difficulty=item["difficulty"],
            instructions=item["instructions"],
        )
        db.add(recipe)
        db.flush()

        for ing in item["ingredients"]:
            ingredient = RecipeIngredient(
                recipe_id=recipe.id,
                name=ing["name"],
                quantity=ing.get("quantity"),
                unit=ing.get("unit"),
            )
            db.add(ingredient)

    db.commit()
