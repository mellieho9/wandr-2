"""
Redis client for OAuth state management.
Provides connection management with fallback to in-memory storage for local development.
"""

import logging
import redis
from typing import Optional
from config.settings import Settings

logger = logging.getLogger(__name__)


class RedisClient:
    """
    Redis client wrapper with connection management and fallback support.
    """

    def __init__(self):
        """Initialize Redis client with configuration from settings."""
        self.settings = Settings()
        self._client: Optional[redis.Redis] = None
        self._available = False
        self._in_memory_fallback = {}
        self._initialize_connection()

    def _initialize_connection(self):
        """
        Initialize Redis connection if configuration is available.
        Falls back to in-memory storage if Redis is unavailable.
        """
        redis_host = self.settings.REDIS_HOST
        redis_port = self.settings.REDIS_PORT

        # Check if Redis configuration is provided
        if not redis_host:
            logger.info(
                "Redis not configured, using in-memory storage for OAuth states"
            )
            self._available = False
            return

        try:
            # Attempt to connect to Redis
            self._client = redis.Redis(
                host=redis_host,
                port=redis_port,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
            )

            # Test connection
            self._client.ping()
            self._available = True
            logger.info(
                "Redis connection established successfully at %s:%s",
                redis_host,
                redis_port,
            )

        except (redis.ConnectionError, redis.TimeoutError) as e:
            logger.warning(
                "Failed to connect to Redis at %s:%s: %s. Using in-memory fallback.",
                redis_host,
                redis_port,
                e,
            )
            self._available = False
            self._client = None
        except Exception as e:
            logger.error(
                "Unexpected error connecting to Redis: %s. Using in-memory fallback.", e
            )
            self._available = False
            self._client = None

    def is_available(self) -> bool:
        """
        Check if Redis is available.

        Returns:
            bool: True if Redis connection is active, False otherwise
        """
        return self._available

    def set_with_ttl(self, key: str, value: str, ttl_seconds: int = 300) -> bool:
        """
        Store a key-value pair with TTL (time-to-live).

        Args:
            key: The key to store
            value: The value to store
            ttl_seconds: Time-to-live in seconds (default: 300 = 5 minutes)

        Returns:
            bool: True if successful, False otherwise
        """
        if self._available and self._client:
            try:
                self._client.setex(key, ttl_seconds, value)
                logger.debug("Stored key in Redis: %s (TTL: %ds)", key, ttl_seconds)
                return True
            except Exception as e:
                logger.error(
                    "Failed to store key in Redis: %s. Falling back to in-memory.", e
                )
                self._available = False

        # Fallback to in-memory storage
        self._in_memory_fallback[key] = value
        logger.debug("Stored key in memory: %s", key)
        return True

    def get(self, key: str) -> Optional[str]:
        """
        Retrieve a value by key.

        Args:
            key: The key to retrieve

        Returns:
            Optional[str]: The value if found, None otherwise
        """
        if self._available and self._client:
            try:
                value = self._client.get(key)
                logger.debug("Retrieved key from Redis: %s", key)
                return value
            except Exception as e:
                logger.error(
                    "Failed to retrieve key from Redis: %s. Checking in-memory fallback.",
                    e,
                )
                self._available = False

        # Fallback to in-memory storage
        value = self._in_memory_fallback.get(key)
        if value:
            logger.debug("Retrieved key from memory: %s", key)
        return value

    def delete(self, key: str) -> bool:
        """
        Delete a key.

        Args:
            key: The key to delete

        Returns:
            bool: True if successful, False otherwise
        """
        if self._available and self._client:
            try:
                self._client.delete(key)
                logger.debug("Deleted key from Redis: %s", key)
                return True
            except Exception as e:
                logger.error(
                    "Failed to delete key from Redis: %s. Falling back to in-memory.", e
                )
                self._available = False

        # Fallback to in-memory storage
        if key in self._in_memory_fallback:
            del self._in_memory_fallback[key]
            logger.debug("Deleted key from memory: %s", key)
        return True

    def exists(self, key: str) -> bool:
        """
        Check if a key exists.

        Args:
            key: The key to check

        Returns:
            bool: True if key exists, False otherwise
        """
        if self._available and self._client:
            try:
                exists = self._client.exists(key) > 0
                logger.debug("Checked key existence in Redis: %s = %s", key, exists)
                return exists
            except Exception as e:
                logger.error(
                    "Failed to check key existence in Redis: %s. Checking in-memory fallback.",
                    e,
                )
                self._available = False

        # Fallback to in-memory storage
        exists = key in self._in_memory_fallback
        logger.debug("Checked key existence in memory: %s = %s", key, exists)
        return exists

    def close(self):
        """Close Redis connection."""
        if self._client:
            try:
                self._client.close()
                logger.info("Redis connection closed")
            except Exception as e:
                logger.error("Error closing Redis connection: %s", e)


# Global Redis client instance
_redis_client: Optional[RedisClient] = None


def get_redis_client() -> RedisClient:
    """
    Get or create the global Redis client instance.

    Returns:
        RedisClient: The global Redis client instance
    """
    global _redis_client
    if _redis_client is None:
        _redis_client = RedisClient()
    return _redis_client
