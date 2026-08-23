import sys
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parents[2]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import json
import logging
from typing import Any
import jwt
from mcp.server.mcpserver import MCPServer
from sqlalchemy.orm import Session

from app.core.security import ALGORITHM, SECRET_KEY
from app.db.database import SessionLocal
from app.models.notification import Notification
from app.models.pantry_item import PantryItem
from app.models.user import User
from app.services.recipe_engine import rank_recipes_for_pantry
from app.services.recipe_generation_service import generate_recipe_from_pantry
from app.services.redis_service import delete_cache

logger = logging.getLogger("pantrypilot.mcp")

# Initialize MCP Server
mcp_server = MCPServer(
    name="PantryPilot MCP Server",
    instructions="Official Model Context Protocol Server for PantryPilot. Exposes capabilities for pantry management, expiry checking, recipes, and notifications with strict JWT authentication.",
)


def authenticate_token(token: str, db: Session) -> User:
    """
    Verifies JWT token and extracts authenticated User object.
    Enforces user isolation & security for all MCP tool calls.
    """
    if not token or not token.strip():
        raise ValueError("Authentication error: JWT access token is required")

    clean_token = token.strip()
    if clean_token.startswith("Bearer "):
        clean_token = clean_token[7:]

    try:
        payload = jwt.decode(clean_token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id_str = payload.get("sub")
        if user_id_str is None:
            raise ValueError("Invalid token payload: missing 'sub'")
        user_id = int(user_id_str)
    except Exception as exc:
        raise ValueError(f"JWT authentication failed: {str(exc)}")

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise ValueError(f"User with ID {user_id} not found in database")

    return user


# ---------------------------------------------------------------------------
# MCP Tool 1: get_pantry_items
# ---------------------------------------------------------------------------
@mcp_server.tool()
def get_pantry_items(token: str) -> list[dict[str, Any]]:
    """
    Fetches all pantry items stored in PostgreSQL for the authenticated user.
    Requires a valid JWT access token.
    """
    db = SessionLocal()
    try:
        user = authenticate_token(token, db)
        items = db.query(PantryItem).filter(PantryItem.user_id == user.id).all()
        return [
            {
                "id": item.id,
                "name": item.name,
                "quantity": item.quantity,
                "unit": item.unit,
                "category": item.category,
                "expiry_date": item.expiry_date.isoformat() if item.expiry_date else None,
            }
            for item in items
        ]
    finally:
        db.close()


# ---------------------------------------------------------------------------
# MCP Tool 2: add_pantry_item
# ---------------------------------------------------------------------------
@mcp_server.tool()
def add_pantry_item(
    token: str,
    name: str,
    quantity: float = 1.0,
    unit: str = "pieces",
    category: str = "Other",
    expiry_date: str | None = None,
) -> dict[str, Any]:
    """
    Adds a new item to the authenticated user's pantry and invalidates recommendation cache.
    Requires a valid JWT access token.
    """
    db = SessionLocal()
    try:
        user = authenticate_token(token, db)

        parsed_expiry = None
        if expiry_date:
            from datetime import date
            try:
                parsed_expiry = date.fromisoformat(expiry_date)
            except ValueError:
                pass

        new_item = PantryItem(
            user_id=user.id,
            name=name,
            quantity=quantity,
            unit=unit,
            category=category,
            expiry_date=parsed_expiry,
        )
        db.add(new_item)
        db.commit()
        db.refresh(new_item)

        # Invalidate user recommendation cache
        delete_cache(f"user:{user.id}:recommendations")

        return {
            "success": True,
            "message": f"Successfully added '{name}' to pantry",
            "item_id": new_item.id,
        }
    finally:
        db.close()


# ---------------------------------------------------------------------------
# MCP Tool 3: update_pantry_item
# ---------------------------------------------------------------------------
@mcp_server.tool()
def update_pantry_item(
    token: str,
    item_id: int,
    quantity: float | None = None,
    unit: str | None = None,
) -> dict[str, Any]:
    """
    Updates quantity or unit of an existing pantry item for the authenticated user.
    Requires a valid JWT access token.
    """
    db = SessionLocal()
    try:
        user = authenticate_token(token, db)

        item = (
            db.query(PantryItem)
            .filter(PantryItem.id == item_id, PantryItem.user_id == user.id)
            .first()
        )
        if item is None:
            raise ValueError(f"Pantry item with ID {item_id} not found")

        if quantity is not None:
            item.quantity = quantity
        if unit is not None:
            item.unit = unit

        db.commit()
        db.refresh(item)

        # Invalidate user recommendation cache
        delete_cache(f"user:{user.id}:recommendations")

        return {
            "success": True,
            "message": f"Updated pantry item '{item.name}'",
            "item_id": item.id,
            "quantity": item.quantity,
            "unit": item.unit,
        }
    finally:
        db.close()


# ---------------------------------------------------------------------------
# MCP Tool 4: get_expiring_items
# ---------------------------------------------------------------------------
@mcp_server.tool()
def get_expiring_items(token: str, days: int = 3) -> list[dict[str, Any]]:
    """
    Fetches pantry items expiring within the specified number of days (default 3 days).
    Requires a valid JWT access token.
    """
    db = SessionLocal()
    try:
        user = authenticate_token(token, db)
        from datetime import date, timedelta

        today = date.today()
        threshold = today + timedelta(days=days)

        expiring = (
            db.query(PantryItem)
            .filter(
                PantryItem.user_id == user.id,
                PantryItem.expiry_date.isnot(None),
                PantryItem.expiry_date <= threshold,
            )
            .all()
        )

        result = []
        for item in expiring:
            days_left = (item.expiry_date - today).days
            result.append(
                {
                    "id": item.id,
                    "name": item.name,
                    "quantity": item.quantity,
                    "unit": item.unit,
                    "category": item.category,
                    "expiry_date": item.expiry_date.isoformat(),
                    "days_remaining": days_left,
                    "status": "expired" if days_left < 0 else "expiring_soon",
                }
            )
        return result
    finally:
        db.close()


# ---------------------------------------------------------------------------
# MCP Tool 5: get_notifications
# ---------------------------------------------------------------------------
@mcp_server.tool()
def get_notifications(token: str) -> list[dict[str, Any]]:
    """
    Fetches expiry notifications for the authenticated user.
    Requires a valid JWT access token.
    """
    db = SessionLocal()
    try:
        user = authenticate_token(token, db)
        notifications = (
            db.query(Notification)
            .filter(Notification.user_id == user.id)
            .order_by(Notification.created_at.desc())
            .all()
        )

        return [
            {
                "id": n.id,
                "message": n.message,
                "notification_type": n.notification_type,
                "is_read": n.is_read,
                "created_at": n.created_at.isoformat(),
            }
            for n in notifications
        ]
    finally:
        db.close()


# ---------------------------------------------------------------------------
# MCP Tool 6: generate_recipe
# ---------------------------------------------------------------------------
@mcp_server.tool()
def generate_recipe(token: str, prompt_hint: str = "") -> dict[str, Any]:
    """
    Generates a creative AI recipe using the user's available pantry ingredients and optional prompt.
    Requires a valid JWT access token.
    """
    db = SessionLocal()
    try:
        user = authenticate_token(token, db)
        items = db.query(PantryItem).filter(PantryItem.user_id == user.id).all()
        available = [i.name for i in items]

        recipe = generate_recipe_from_pantry(available)
        return recipe.model_dump(mode="json")
    finally:
        db.close()


def main():
    """
    Runs the MCP Server using stdio transport (Standard I/O).
    """
    print("[PANTRYPILOT MCP SERVER] Starting PantryPilot MCP Server on stdio transport...")
    logger.info("[PANTRYPILOT MCP SERVER] Starting PantryPilot MCP Server on stdio transport...")
    mcp_server.run()


if __name__ == "__main__":
    main()
