import json
import logging
from typing import Any

import redis

from app.core.config import settings

logger = logging.getLogger("pantrypilot.redis")

# Initialize Redis client with decode_responses=True so strings are returned instead of bytes
redis_client = redis.from_url(
    settings.REDIS_URL,
    decode_responses=True,
    socket_timeout=2.0,
    socket_connect_timeout=2.0,
)


def set_cache(
    key: str,
    value: Any,
    expiration: int = 300,
) -> bool:
    """
    Stores a value in Redis with a specified Time-To-Live (TTL) in seconds.
    Automatically serializes non-string Python objects (dict, list) using JSON.
    """
    try:
        if not isinstance(value, str):
            serialized_value = json.dumps(value)
        else:
            serialized_value = value

        redis_client.setex(
            name=key,
            time=expiration,
            value=serialized_value,
        )
        return True
    except redis.RedisError as exc:
        logger.warning(f"[REDIS ERROR] Failed to set cache key '{key}': {exc}")
        return False
    except Exception as exc:
        logger.warning(f"[REDIS ERROR] Serialization failure for key '{key}': {exc}")
        return False


def get_cache(key: str) -> Any:
    """
    Retrieves a cached value from Redis by key.
    Automatically parses JSON strings into Python dictionaries or lists if applicable.
    Returns None on cache miss or connection error.
    """
    try:
        cached_data = redis_client.get(key)
        if cached_data is None:
            return None

        # Attempt to deserialize JSON content
        try:
            return json.loads(cached_data)
        except (json.JSONDecodeError, TypeError):
            return cached_data
    except redis.RedisError as exc:
        logger.warning(f"[REDIS ERROR] Failed to get cache key '{key}': {exc}")
        return None


def delete_cache(key: str) -> bool:
    """
    Deletes a cache key from Redis (Cache Invalidation).
    """
    try:
        redis_client.delete(key)
        return True
    except redis.RedisError as exc:
        logger.warning(f"[REDIS ERROR] Failed to delete cache key '{key}': {exc}")
        return False