"""
Database Engine & Async Session Management
Supports PostgreSQL (Production / Docker) with SQLite aiosqlite fallback (Local / Test)
"""
from typing import AsyncGenerator
import structlog
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from config import settings

log = structlog.get_logger()

db_url = settings.DATABASE_URL
try:
    if "postgresql" in db_url:
        import asyncpg  # noqa: F401
    engine = create_async_engine(
        db_url,
        echo=False,
        future=True,
        pool_pre_ping=True,
    )
except (ImportError, ModuleNotFoundError) as e:
    log.warning("PostgreSQL driver (asyncpg) unavailable, using local SQLite engine for dev/test", error=str(e))
    fallback_url = "sqlite+aiosqlite:///./cloudsquad_dev.db"
    engine = create_async_engine(fallback_url, echo=False, future=True)

async_session_factory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


def configure_engine(new_engine):
    """Allows test fixtures to rebind engine and session factory"""
    global engine, async_session_factory
    engine = new_engine
    async_session_factory = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    from database.base import Base
    import database.models  # noqa: F401
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
