import asyncio
import json
import logging
from typing import Any
from fastapi import WebSocket
import redis.asyncio as aioredis

from app.core.config import settings

logger = logging.getLogger("pantrypilot.websocket")


class ConnectionManager:
    """
    Manages active WebSocket connections per authenticated user_id.
    Provides multi-tenant user data isolation so User A never receives User B's notifications.
    """

    def __init__(self):
        # Maps user_id -> list of active WebSocket instances
        self.active_connections: dict[int, list[WebSocket]] = {}

    async def connect(self, user_id: int, websocket: WebSocket):
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)
        logger.info(f"[WEBSOCKET CONNECTED] User ID {user_id} connected. Active user connections: {len(self.active_connections[user_id])}")
        print(f"[WEBSOCKET CONNECTED] User ID {user_id} connected. Active user connections: {len(self.active_connections[user_id])}")

    def disconnect(self, user_id: int, websocket: WebSocket):
        if user_id in self.active_connections:
            if websocket in self.active_connections[user_id]:
                self.active_connections[user_id].remove(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
        logger.info(f"[WEBSOCKET DISCONNECTED] User ID {user_id} disconnected.")
        print(f"[WEBSOCKET DISCONNECTED] User ID {user_id} disconnected.")

    async def send_personal_message(self, message: dict[str, Any], user_id: int):
        """
        Sends a real-time JSON message ONLY to the specified user's active WebSocket connection(s).
        """
        if user_id in self.active_connections:
            disconnected_sockets = []
            for websocket in self.active_connections[user_id]:
                try:
                    await websocket.send_json(message)
                except Exception as exc:
                    logger.warning(f"[WEBSOCKET SEND ERROR] Failed to send to User {user_id}: {exc}")
                    disconnected_sockets.append(websocket)

            # Cleanup broken sockets
            for ws in disconnected_sockets:
                self.disconnect(user_id, ws)

    async def broadcast(self, message: dict[str, Any]):
        """
        Sends a JSON message to all currently connected users.
        """
        for user_id, sockets in list(self.active_connections.items()):
            for ws in sockets:
                try:
                    await ws.send_json(message)
                except Exception:
                    pass


# Singleton ConnectionManager instance
manager = ConnectionManager()


async def redis_pubsub_listener(connection_manager: ConnectionManager):
    """
    Background asyncio task running in FastAPI.
    Subscribes to Redis Pub/Sub channel 'pantrypilot:notifications'.
    When Celery publishes a notification, forwards it to the targeted user's WebSocket!
    """
    logger.info("[REDIS PUBSUB LISTENER] Initializing Redis Pub/Sub listener for WebSockets...")

    while True:
        try:
            r = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
            pubsub = r.pubsub()
            await pubsub.subscribe("pantrypilot:notifications")

            async for message in pubsub.listen():
                if message["type"] == "message":
                    raw_data = message["data"]
                    try:
                        data = json.loads(raw_data)
                        target_user_id = data.get("user_id")
                        if target_user_id:
                            msg_text = str(data.get("message", ""))
                            safe_msg = msg_text.encode("ascii", "ignore").decode("ascii")
                            print(f"[REDIS PUBSUB MATCH] Real-time notification for User {target_user_id}: {safe_msg}")
                            await connection_manager.send_personal_message(data, int(target_user_id))
                    except Exception as exc:
                        logger.error(f"[REDIS PUBSUB ERROR] Failed to parse message: {exc}")

        except asyncio.CancelledError:
            logger.info("[REDIS PUBSUB LISTENER] Task cancelled. Stopping listener.")
            break
        except Exception as exc:
            logger.error(f"[REDIS PUBSUB LISTENER ERROR] Reconnecting in 5s due to error: {exc}")
            await asyncio.sleep(5)
