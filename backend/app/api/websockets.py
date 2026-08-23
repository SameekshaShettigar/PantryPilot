import logging
from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect, status
import jwt
from jwt.exceptions import InvalidTokenError

from app.core.security import ALGORITHM, SECRET_KEY
from app.db.database import SessionLocal
from app.models.user import User
from app.services.websocket_manager import manager

logger = logging.getLogger("pantrypilot.websockets_api")

router = APIRouter(
    prefix="/ws",
    tags=["WebSockets"],
)


def get_user_from_jwt_token(token: str) -> User | None:
    """
    Validates JWT token from WebSocket query parameters and fetches user from DB.
    """
    if not token or not token.strip():
        return None

    clean_token = token.strip()
    if clean_token.startswith("Bearer "):
        clean_token = clean_token[7:]

    db = SessionLocal()
    try:
        payload = jwt.decode(clean_token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id_str = payload.get("sub")
        if user_id_str is None:
            return None
        user_id = int(user_id_str)
        user = db.query(User).filter(User.id == user_id).first()
        return user
    except (InvalidTokenError, ValueError, Exception) as exc:
        logger.warning(f"[WEBSOCKET AUTH ERROR] Token validation failed: {exc}")
        return None
    finally:
        db.close()


@router.websocket("/notifications")
async def websocket_notifications_endpoint(
    websocket: WebSocket,
    token: str = Query(..., description="JWT access token for authentication"),
):
    """
    Authenticated WebSocket endpoint for real-time expiry notifications.
    Client connects to ws://localhost:8000/ws/notifications?token=<access_token>
    """
    # 1. Authenticate user from query parameter token
    user = get_user_from_jwt_token(token)

    if user is None:
        logger.warning("[WEBSOCKET REJECTED] Unauthenticated connection attempt rejected.")
        # Reject connection with Policy Violation code 1008
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Invalid or expired authentication token")
        return

    # 2. Register connection in ConnectionManager
    await manager.connect(user.id, websocket)

    try:
        # Send initial confirmation message
        await websocket.send_json({
            "type": "connection_established",
            "message": f"Connected to PantryPilot Real-Time Notifications as {user.username}",
            "user_id": user.id,
        })

        # 3. Maintain persistent connection loop
        while True:
            # Receive client ping or text messages
            data = await websocket.receive_text()
            # Respond to client ping/echo
            if data == "ping":
                await websocket.send_text("pong")

    except WebSocketDisconnect:
        manager.disconnect(user.id, websocket)
    except Exception as exc:
        logger.error(f"[WEBSOCKET ERROR] User {user.id} error: {exc}")
        manager.disconnect(user.id, websocket)
