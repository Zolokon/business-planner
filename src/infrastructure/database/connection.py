"""
Database connection management - Business Planner.

PostgreSQL 15 with pgvector extension using asyncpg driver.

Reference:
- ADR-005 (PostgreSQL + pgvector)
- docs/02-database/schema.sql
"""

from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker
)
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool

from src.config import settings
from src.utils.logger import logger


# Base class for SQLAlchemy models
Base = declarative_base()


# ============================================================================
# Async Engine
# ============================================================================

# Create async engine
engine = create_async_engine(
    settings.database_url,
    echo=settings.db_echo,  # Log SQL queries (debug mode)
    pool_size=settings.db_pool_size,
    max_overflow=settings.db_max_overflow,
    pool_pre_ping=True,  # Check connection health before using
    pool_recycle=3600,   # Recycle connections after 1 hour
    future=True
)

# Session factory
async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,  # Don't expire objects after commit
    autoflush=False,         # Manual flush control
    autocommit=False         # Manual commit control
)


# ============================================================================
# Session Management
# ============================================================================

async def get_session() -> AsyncSession:
    """Get database session (FastAPI dependency).
    
    Usage in FastAPI:
        @app.get("/tasks")
        async def get_tasks(session: AsyncSession = Depends(get_session)):
            ...
    
    Yields:
        AsyncSession: Database session
    """
    async with async_session_factory() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            logger.error("database_session_error", error=str(e))
            raise
        finally:
            await session.close()


# ============================================================================
# Database Initialization
# ============================================================================

async def init_database() -> None:
    """Initialize database (create tables, enable extensions).

    Should be called on application startup.
    Uses Alembic migrations in production.
    """

    logger.info("initializing_database", url=mask_connection_string(settings.database_url))

    try:
        # Test connection
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
            logger.info("database_connection_ok")

        logger.info("database_initialized")

    except Exception as e:
        logger.error("database_initialization_failed", error=str(e))
        raise


async def close_database() -> None:
    """Close database connections.
    
    Should be called on application shutdown.
    """
    logger.info("closing_database_connections")
    await engine.dispose()
    logger.info("database_connections_closed")


# ============================================================================
# Health Check
# ============================================================================

async def check_database_health() -> bool:
    """Check if database is accessible.

    Returns:
        True if database is healthy
    """
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error("database_health_check_failed", error=str(e))
        return False


# ============================================================================
# Utilities
# ============================================================================

def mask_connection_string(url: str) -> str:
    """Mask password in connection string for logging.
    
    Args:
        url: Database URL
        
    Returns:
        URL with masked password
        
    Example:
        >>> mask_connection_string("postgresql://user:pass@localhost/db")
        "postgresql://user:***@localhost/db"
    """
    from urllib.parse import urlparse, urlunparse
    
    parsed = urlparse(url)
    if parsed.password:
        # Replace password with ***
        netloc = f"{parsed.username}:***@{parsed.hostname}"
        if parsed.port:
            netloc += f":{parsed.port}"
        
        masked = parsed._replace(netloc=netloc)
        return urlunparse(masked)
    
    return url

