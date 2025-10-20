"""
Pytest Configuration and Shared Fixtures - Business Planner.

Global fixtures for all tests (unit, integration, e2e).
"""

import os
import pytest
import pytest_asyncio
import asyncio
from datetime import datetime, timedelta
from typing import AsyncGenerator
from unittest.mock import AsyncMock, MagicMock

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool, StaticPool
from sqlalchemy import text

# Set test environment variables BEFORE importing app code
# This MUST be done before any src imports
os.environ.setdefault('DATABASE_URL', 'sqlite+aiosqlite:///:memory:')
os.environ.setdefault('OPENAI_API_KEY', 'sk-test-dummy-key')
os.environ.setdefault('TELEGRAM_BOT_TOKEN', '123456:ABC-DEF-test')
os.environ.setdefault('TELEGRAM_SECRET_TOKEN', 'test-secret')
os.environ.setdefault('DEBUG', 'true')
os.environ.setdefault('REDIS_URL', 'redis://localhost:6379/1')

# Now we can safely import (but we'll avoid connection.py imports)
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Import Base and all models (models auto-register with Base when imported)
from src.infrastructure.database.connection import Base

# Import ALL models to ensure they're registered with Base.metadata
# This MUST come after Base import
from src.infrastructure.database.models import (
    UserORM,
    BusinessORM,
    MemberORM,
    TaskORM,
    ProjectORM,
    TaskHistoryORM
)
from src.domain.models.enums import TaskStatus, Priority


# ============================================================================
# Async Event Loop Configuration
# ============================================================================

@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests.

    Scope: session - one loop for all tests.
    """
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# ============================================================================
# Database Fixtures
# ============================================================================

@pytest_asyncio.fixture
async def test_db_engine():
    """Create in-memory SQLite database engine for testing.

    Each test gets a fresh database.
    Uses shared cache so all connections see the same schema.
    """
    # Use StaticPool to ensure all connections use the same in-memory database
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False
    )

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # Cleanup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def test_session(test_db_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create async database session for testing.

    Each test gets a fresh session.
    """
    async_session = async_sessionmaker(
        test_db_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    async with async_session() as session:
        yield session
        await session.rollback()  # Rollback any uncommitted changes


# ============================================================================
# Test Data Fixtures
# ============================================================================

@pytest_asyncio.fixture
async def test_user(test_session: AsyncSession) -> UserORM:
    """Create test user in database.

    Returns:
        UserORM with id=1, telegram_id=123456
    """
    user = UserORM(
        id=1,
        telegram_id=123456,
        name="Test User",
        username="test_user",
        timezone="Europe/Moscow",
        created_at=datetime.now()
    )

    test_session.add(user)
    await test_session.commit()
    await test_session.refresh(user)

    return user


@pytest_asyncio.fixture
async def test_business(test_session: AsyncSession, test_user: UserORM) -> BusinessORM:
    """Create test business in database.

    Returns:
        BusinessORM (Inventum)
    """
    business = BusinessORM(
        id=1,
        name="inventum",
        display_name="Inventum",
        description="Фрезерный ЧПУ бизнес",
        keywords=[],
        created_at=datetime.now()
    )

    test_session.add(business)
    await test_session.commit()
    await test_session.refresh(business)

    return business


@pytest_asyncio.fixture
async def test_member(test_session: AsyncSession, test_business: BusinessORM, test_user: UserORM) -> MemberORM:
    """Create test team member in database.

    Returns:
        MemberORM (Maxim - mechanic)
    """
    member = MemberORM(
        id=1,
        name="Максим",
        role="mechanic",
        business_ids=[test_business.id],
        created_at=datetime.now()
    )

    test_session.add(member)
    await test_session.commit()
    await test_session.refresh(member)

    return member


@pytest_asyncio.fixture
async def test_task(
    test_session: AsyncSession,
    test_business: BusinessORM,
    test_user: UserORM,
    test_member: MemberORM
) -> TaskORM:
    """Create test task in database.

    Returns:
        TaskORM (sample task for testing)
    """
    task = TaskORM(
        id=1,
        title="Починить фрезер для Иванова",
        business_id=test_business.id,
        created_by_id=test_user.id,
        assigned_to=test_member.id,
        status=TaskStatus.PENDING,
        priority=Priority.MEDIUM,
        estimated_duration=120,  # 2 hours
        deadline=datetime.now() + timedelta(days=1),
        deadline_text="завтра",
        created_via="voice",
        created_at=datetime.now()
    )

    test_session.add(task)
    await test_session.commit()
    await test_session.refresh(task)

    return task


@pytest_asyncio.fixture
async def test_tasks_multiple(
    test_session: AsyncSession,
    test_business: BusinessORM,
    test_user: UserORM
) -> list[TaskORM]:
    """Create multiple test tasks with different priorities and deadlines.

    Returns:
        List of 5 tasks (different priorities and dates)
    """
    today = datetime.now().date()

    tasks = [
        TaskORM(
            title="Срочная задача - высокий приоритет",
            business_id=test_business.id,
            created_by_id=test_user.id,
            status=TaskStatus.PENDING,
            priority=Priority.HIGH,
            deadline=datetime.combine(today, datetime.min.time()),
            created_at=datetime.now()
        ),
        TaskORM(
            title="Обычная задача на сегодня",
            business_id=test_business.id,
            created_by_id=test_user.id,
            status=TaskStatus.PENDING,
            priority=Priority.MEDIUM,
            deadline=datetime.combine(today, datetime.min.time()),
            created_at=datetime.now()
        ),
        TaskORM(
            title="Задача на завтра",
            business_id=test_business.id,
            created_by_id=test_user.id,
            status=TaskStatus.PENDING,
            priority=Priority.MEDIUM,
            deadline=datetime.combine(today + timedelta(days=1), datetime.min.time()),
            created_at=datetime.now()
        ),
        TaskORM(
            title="Задача на неделю",
            business_id=test_business.id,
            created_by_id=test_user.id,
            status=TaskStatus.PENDING,
            priority=Priority.LOW,
            deadline=datetime.combine(today + timedelta(days=7), datetime.min.time()),
            created_at=datetime.now()
        ),
        TaskORM(
            title="Завершенная задача",
            business_id=test_business.id,
            created_by_id=test_user.id,
            status=TaskStatus.COMPLETED,
            priority=Priority.MEDIUM,
            completed_at=datetime.now(),
            actual_duration=90,
            created_at=datetime.now() - timedelta(days=1)
        ),
    ]

    for task in tasks:
        test_session.add(task)

    await test_session.commit()

    for task in tasks:
        await test_session.refresh(task)

    return tasks


# ============================================================================
# Mock Fixtures
# ============================================================================

@pytest.fixture
def mock_openai_client():
    """Mock OpenAI client for testing.

    Returns:
        MagicMock with async methods for transcription, parsing, etc.
    """
    mock = MagicMock()

    # Mock transcription
    mock.transcribe_voice = AsyncMock(return_value=(
        "Нужно починить фрезер для Иванова до завтра",
        0.95  # confidence
    ))

    # Mock task parsing
    mock.parse_task = AsyncMock(return_value={
        "title": "Починить фрезер для Иванова",
        "business_id": 1,
        "deadline": "2025-10-21",
        "assigned_to": "Максим",
        "priority": 2
    })

    # Mock time estimation
    mock.estimate_time = AsyncMock(return_value=120)  # 2 hours

    return mock


@pytest.fixture
def mock_telegram_update():
    """Mock Telegram Update object.

    Returns:
        MagicMock simulating Telegram Update
    """
    mock_update = MagicMock()

    # Mock user
    mock_update.effective_user.id = 123456
    mock_update.effective_user.username = "test_user"
    mock_update.effective_user.first_name = "Test"

    # Mock message
    mock_update.message.reply_text = AsyncMock()
    mock_update.message.reply_chat_action = AsyncMock()

    # Mock callback query
    mock_update.callback_query = None

    return mock_update


@pytest.fixture
def mock_telegram_context():
    """Mock Telegram Context object.

    Returns:
        MagicMock simulating ContextTypes.DEFAULT_TYPE
    """
    mock_context = MagicMock()
    mock_context.args = []
    mock_context.bot = MagicMock()

    return mock_context


# ============================================================================
# Helper Fixtures
# ============================================================================

@pytest.fixture
def sample_voice_bytes() -> bytes:
    """Sample voice message bytes for testing.

    Returns:
        Dummy audio bytes
    """
    # Dummy audio data (not real audio, just for testing)
    return b"dummy_audio_data_for_testing" * 100


@pytest.fixture
def sample_transcript() -> str:
    """Sample voice transcript for testing.

    Returns:
        Russian transcript text
    """
    return "Нужно починить фрезер для Иванова до завтра высокий приоритет"


# ============================================================================
# Markers
# ============================================================================

# Markers are defined in pytest.ini:
# - unit: Fast, isolated tests
# - integration: Tests with database/Redis
# - e2e: Full workflow tests
# - slow: Tests > 1 second
# - ai: Tests using AI APIs
