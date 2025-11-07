"""
Prisma client initialization and database utilities.
"""

from prisma import Prisma
from contextlib import asynccontextmanager
import logging
import threading

logger = logging.getLogger(__name__)

# Thread-local storage for Prisma client instances
_thread_local = threading.local()


def get_db() -> Prisma:
    """
    Get a thread-local Prisma client instance.
    This ensures each thread/request has its own client to avoid event loop conflicts.

    Returns:
        Prisma: The Prisma client instance
    """
    if (
        not hasattr(_thread_local, "prisma_client")
        or _thread_local.prisma_client is None
    ):
        _thread_local.prisma_client = Prisma()

    return _thread_local.prisma_client


async def connect_db():
    """
    Connect to the database.
    Should be called at application startup.
    """
    db = get_db()
    if not db.is_connected():
        await db.connect()
        logger.info("Database connected successfully")


async def disconnect_db():
    """
    Disconnect from the database.
    Should be called at application shutdown.
    """
    db = get_db()
    if db.is_connected():
        await db.disconnect()
        logger.info("Database disconnected")


@asynccontextmanager
async def db_transaction():
    """
    Context manager for database transactions.

    Usage:
        async with db_transaction():
            await db.user.create(...)
            await db.notionschema.create(...)
    """
    db = get_db()

    try:
        # Prisma Client Python handles transactions automatically
        # This context manager is for explicit transaction control if needed
        yield db
    except Exception as e:
        logger.error(f"Transaction failed: {e}")
        raise


async def ensure_connected():
    """
    Ensure the database is connected.
    Connects if not already connected.
    """
    db = get_db()
    if not db.is_connected():
        await connect_db()
