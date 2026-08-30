from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)

_engine: AsyncEngine | None = None
_sessionmaker: async_sessionmaker[AsyncSession] | None = None


def get_engine() -> AsyncEngine:
    global _engine
    if _engine is None:
        settings = get_settings()
        url = settings.async_database_url

        connect_args = {}
        # Special handling for SQLite fallback in test environments
        if url.startswith("sqlite"):
            connect_args = {"check_same_thread": False}

        _engine = create_async_engine(
            url,
            echo=False,
            future=True,
            connect_args=connect_args,
            pool_pre_ping=True,
            **({"pool_size": settings.database_pool_size, "max_overflow": settings.database_max_overflow} if not url.startswith("sqlite") else {}),
        )
        logger.info("database_engine_created", url=url.split("@")[-1] if "@" in url else url)
    return _engine


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    global _sessionmaker
    if _sessionmaker is None:
        engine = get_engine()
        _sessionmaker = async_sessionmaker(
            bind=engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
        )
    return _sessionmaker


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency that yields an asynchronous database session.
    Automatically closes session upon request completion.
    """
    session_factory = get_session_factory()
    async with session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
