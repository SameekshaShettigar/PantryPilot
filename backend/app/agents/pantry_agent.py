import json
import logging
from typing import Any
from sqlalchemy.orm import Session

from google import genai
from google.genai import types

from app.agents.tools import (
    tool_add_pantry_item,
    tool_add_to_shopping_list,
    tool_generate_recipe,
    tool_get_expiring_items,
    tool_get_pantry_items,
    tool_get_recipe_recommendations,
    tool_get_shopping_list,
)
from app.core.config import settings

logger = logging.getLogger("pantrypilot.agent")

MODEL_NAME = "gemini-3-flash-preview"

# Tool Registry mapping Gemini function names to Python implementations
TOOL_REGISTRY = {
    "get_pantry_items": tool_get_pantry_items,
    "get_expiring_items": tool_get_expiring_items,
    "add_pantry_item": tool_add_pantry_item,
    "get_recipe_recommendations": tool_get_recipe_recommendations,
    "generate_recipe": tool_generate_recipe,
    "get_shopping_list": tool_get_shopping_list,
    "add_to_shopping_list": tool_add_to_shopping_list,
}

# Function Declarations provided to Gemini
TOOL_DECLARATIONS = types.Tool(
    function_declarations=[
        types.FunctionDeclaration(
            name="get_pantry_items",
            description="Fetches all food items and ingredients currently stored in the user's pantry.",
            parameters=types.Schema(
                type="OBJECT",
                properties={},
            ),
        ),
        types.FunctionDeclaration(
            name="get_expiring_items",
            description="Fetches pantry items that are expiring soon within the specified number of days.",
            parameters=types.Schema(
                type="OBJECT",
                properties={
                    "days": types.Schema(
                        type="INTEGER",
                        description="Threshold in days (default 3)",
                    ),
                },
            ),
        ),
        types.FunctionDeclaration(
            name="add_pantry_item",
            description="Adds a new item/ingredient to the user's pantry.",
            parameters=types.Schema(
                type="OBJECT",
                properties={
                    "name": types.Schema(type="STRING", description="Name of the item (e.g. Milk, Eggs)"),
                    "quantity": types.Schema(type="NUMBER", description="Quantity amount (e.g. 2.0)"),
                    "unit": types.Schema(type="STRING", description="Unit of measurement (e.g. litres, pieces)"),
                    "category": types.Schema(type="STRING", description="Category (Dairy, Vegetables, Meat, Bakery, Other)"),
                    "expiry_date": types.Schema(type="STRING", description="Expiry date in YYYY-MM-DD format (optional)"),
                },
                required=["name"],
            ),
        ),
        types.FunctionDeclaration(
            name="get_recipe_recommendations",
            description="Recommends recipes based on available pantry items and expiring food items.",
            parameters=types.Schema(
                type="OBJECT",
                properties={},
            ),
        ),
        types.FunctionDeclaration(
            name="generate_recipe",
            description="Generates a brand new AI custom recipe tailored to the user's available pantry ingredients.",
            parameters=types.Schema(
                type="OBJECT",
                properties={
                    "prompt_hint": types.Schema(type="STRING", description="Optional user preferences or time constraints"),
                },
            ),
        ),
        types.FunctionDeclaration(
            name="get_shopping_list",
            description="Fetches the user's current grocery shopping list.",
            parameters=types.Schema(
                type="OBJECT",
                properties={},
            ),
        ),
        types.FunctionDeclaration(
            name="add_to_shopping_list",
            description="Adds an ingredient/item to the user's shopping list.",
            parameters=types.Schema(
                type="OBJECT",
                properties={
                    "name": types.Schema(type="STRING", description="Name of the grocery item"),
                    "quantity": types.Schema(type="NUMBER", description="Quantity needed"),
                    "unit": types.Schema(type="STRING", description="Unit of measurement"),
                },
                required=["name"],
            ),
        ),
    ]
)

SYSTEM_INSTRUCTION = """
You are PantryPilot's Autonomous AI Assistant and Kitchen Companion.
Your task is to help the user manage their pantry, avoid food waste, recommend recipes, and manage shopping lists.

Guidelines:
1. Always use available tools to inspect actual pantry data, expiring items, or shopping lists when answering questions. Do not guess user pantry contents.
2. If a user asks "What can I cook?", call `get_pantry_items` or `get_expiring_items` first, then recommend or generate a recipe.
3. Be helpful, concise, friendly, and food-aware.
4. When you execute actions (like adding items to pantry or shopping list), confirm the action clearly to the user.
"""


def run_pantry_agent(
    db: Session,
    user_id: int,
    user_message: str,
) -> dict[str, Any]:
    """
    Multi-step ReAct Agent execution loop:
    1. Sends user message and tool definitions to Gemini.
    2. If Gemini requests tool calls, executes Python tools safely with authenticated user_id & db.
    3. Feeds tool responses back into Gemini.
    4. Returns final response text and list of executed tool names.
    """
    if not settings.GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY is not configured")

    client = genai.Client(api_key=settings.GEMINI_API_KEY)
    tools_used = []

    # Initialize chat session with system instruction and tool definitions
    chat = client.chats.create(
        model=MODEL_NAME,
        config=types.GenerateContentConfig(
            tools=[TOOL_DECLARATIONS],
            system_instruction=SYSTEM_INSTRUCTION,
            temperature=0.3,
        ),
    )

    # Initial turn
    response = chat.send_message(user_message)
    max_turns = 5
    turn_count = 0

    while turn_count < max_turns:
        turn_count += 1

        # Check if Gemini wants to call tool(s)
        function_calls = getattr(response, "function_calls", None)
        if not function_calls and hasattr(response, "candidates") and response.candidates:
            # Extract function calls from candidate parts if needed
            for part in response.candidates[0].content.parts:
                if getattr(part, "function_call", None):
                    function_calls = [part.function_call]
                    break

        if not function_calls:
            # Final text answer reached!
            break

        # Process each tool call requested by Gemini
        function_responses = []
        for call in function_calls:
            fn_name = call.name
            fn_args = dict(call.args) if call.args else {}

            logger.info(f"[AI AGENT TOOL CALL] Executing tool '{fn_name}' with args {fn_args} for user {user_id}")
            print(f"[AI AGENT TOOL CALL] Executing tool '{fn_name}' with args {fn_args} for user {user_id}")

            if fn_name not in tools_used:
                tools_used.append(fn_name)

            tool_fn = TOOL_REGISTRY.get(fn_name)
            if tool_fn:
                try:
                    # Enforce Security: Inject db and user_id directly from JWT context
                    tool_result = tool_fn(db=db, user_id=user_id, **fn_args)
                except Exception as exc:
                    tool_result = {"error": f"Tool execution failed: {str(exc)}"}
            else:
                tool_result = {"error": f"Unknown tool '{fn_name}'"}

            function_responses.append(
                types.Part(
                    function_response=types.FunctionResponse(
                        name=fn_name,
                        response={"result": tool_result},
                    )
                )
            )

        # Send tool output back to Gemini
        response = chat.send_message(function_responses)

    final_text = response.text if hasattr(response, "text") and response.text else "Task completed."

    return {
        "response": final_text,
        "tools_used": tools_used,
    }
