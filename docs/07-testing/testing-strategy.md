# Testing Strategy - Business Planner

> **Comprehensive testing approach**  
> **Created**: 2025-10-17  
> **Framework**: Pytest + pytest-asyncio  
> **Target Coverage**: 80%+ overall, 95%+ domain logic

---

## 🎯 Testing Philosophy

### Principles
1. **Test behavior, not implementation**
2. **Fast feedback** - Most tests < 100ms
3. **Reliable** - No flaky tests
4. **Isolated** - Tests don't affect each other
5. **Coverage** - 80%+ but focus on critical paths

### Test Pyramid

```
       /\        E2E (5%)
      /  \       ↑ Slow, fragile
     /────\      Integration (15%)
    /──────\     ↑ Medium speed
   /────────\    Unit (80%)
  /──────────\   ↑ Fast, reliable
```

---

## 📋 Test Structure

```
tests/
├── conftest.py              # Shared fixtures
├── unit/                    # Fast, isolated (80% of tests)
│   ├── test_parsers.py
│   ├── test_services.py
│   ├── test_rules.py
│   ├── test_value_objects.py
│   └── test_domain_events.py
├── integration/             # With real dependencies (15%)
│   ├── test_api.py
│   ├── test_database.py
│   ├── test_redis.py
│   └── test_telegram.py
├── e2e/                     # Full workflows (5%)
│   └── test_voice_to_task.py
└── fixtures/                # Test data
    ├── tasks.py
    ├── projects.py
    └── audio_samples/
```

---

## ✅ Unit Tests (80%)

### Purpose
Test individual functions/methods in isolation

### Characteristics
- **Fast**: < 10ms per test
- **No I/O**: No database, network, files
- **Mocked dependencies**: Use mocks/stubs
- **High coverage**: Every function tested

### Example: Test Business Rules

```python
import pytest
from src.domain.rules.deadline_rules import adjust_for_workday
from datetime import datetime
from zoneinfo import ZoneInfo

def test_weekend_adjusts_to_monday():
    """Test weekend deadlines move to Monday."""
    
    # Saturday
    saturday = datetime(2025, 10, 18, 10, 0, tzinfo=ZoneInfo("Asia/Almaty"))
    
    adjusted = adjust_for_workday(saturday)
    
    assert adjusted.weekday() == 0  # Monday
    assert adjusted.hour == 9       # 09:00


def test_weekday_unchanged():
    """Test weekday deadlines stay unchanged."""
    
    # Tuesday
    tuesday = datetime(2025, 10, 21, 15, 0, tzinfo=ZoneInfo("Asia/Almaty"))
    
    adjusted = adjust_for_workday(tuesday)
    
    assert adjusted == tuesday  # No change
```

### Example: Test Value Objects

```python
from src.domain.value_objects import Duration, Priority

def test_duration_validation():
    """Test duration value object."""
    
    # Valid
    duration = Duration(90)
    assert duration.minutes == 90
    assert duration.hours == 1.5
    assert duration.display == "1 ч 30 мин"
    
    # Invalid: too short
    with pytest.raises(ValueError, match="at least 1 minute"):
        Duration(0)
    
    # Invalid: too long
    with pytest.raises(ValueError, match="cannot exceed 480"):
        Duration(500)


def test_priority_from_importance_urgency():
    """Test Eisenhower matrix priority calculation."""
    
    assert Priority.from_importance_urgency(True, True) == Priority.DO_NOW
    assert Priority.from_importance_urgency(True, False) == Priority.SCHEDULE
    assert Priority.from_importance_urgency(False, True) == Priority.DELEGATE
    assert Priority.from_importance_urgency(False, False) == Priority.BACKLOG
```

---

## 🔗 Integration Tests (15%)

### Purpose
Test components working together with real dependencies

### Characteristics
- **Medium speed**: 100-500ms per test
- **Real database**: PostgreSQL test instance
- **Real Redis**: Redis test instance
- **Realistic**: Close to production setup

### Setup (conftest.py)

```python
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

@pytest_asyncio.fixture
async def db_session():
    """Provide database session for tests."""
    
    # Create test engine
    engine = create_async_engine(
        "postgresql+asyncpg://planner:test@localhost:5432/planner_test",
        echo=False
    )
    
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Provide session
    async with AsyncSession(engine) as session:
        yield session
    
    # Cleanup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest_asyncio.fixture
async def redis_client():
    """Provide Redis client for tests."""
    
    import aioredis
    
    redis = await aioredis.create_redis_pool("redis://localhost:6379/1")
    
    yield redis
    
    # Cleanup
    await redis.flushdb()
    redis.close()
    await redis.wait_closed()
```

### Example: Test Database Operations

```python
async def test_create_task_with_business_isolation(db_session):
    """Test task creation respects business isolation."""
    
    # Create repository
    repo = SQLAlchemyTaskRepository(db_session)
    
    # Create tasks in different businesses
    inventum_task = await repo.create(Task(
        title="Ремонт фрезера",
        business_id=1,
        user_id=1
    ))
    
    lab_task = await repo.create(Task(
        title="Моделирование коронки",
        business_id=2,
        user_id=1
    ))
    
    # Find by business
    inventum_tasks = await repo.find_by_business(user_id=1, business_id=1)
    
    # Verify isolation
    assert len(inventum_tasks) == 1
    assert inventum_tasks[0].id == inventum_task.id
    assert all(t.business_id == 1 for t in inventum_tasks)


async def test_rag_vector_search(db_session):
    """Test RAG similarity search with business isolation."""
    
    # Create tasks with embeddings
    task1 = await create_task_with_embedding(
        "Починить фрезер",
        business_id=1,
        embedding=[0.1, 0.2, ...]  # Mock embedding
    )
    
    task2 = await create_task_with_embedding(
        "Ремонт фрезера",
        business_id=1,
        embedding=[0.11, 0.21, ...]  # Similar embedding
    )
    
    task3 = await create_task_with_embedding(
        "Починить прототип",
        business_id=3,  # Different business!
        embedding=[0.1, 0.2, ...]  # Same embedding
    )
    
    # Complete tasks (for learning)
    await repo.complete(task1.id, actual_duration=120)
    await repo.complete(task2.id, actual_duration=105)
    await repo.complete(task3.id, actual_duration=180)
    
    # Search from business 1
    similar = await repo.find_similar(
        embedding=[0.1, 0.2, ...],
        business_id=1,
        limit=5
    )
    
    # Verify: Only business 1 tasks
    assert len(similar) == 2
    assert all(t.business_id == 1 for t in similar)
    # task3 (business 3) should NOT be in results!
```

---

## 🌐 E2E Tests (5%)

### Purpose
Test complete user workflows end-to-end

### Characteristics
- **Slow**: 1-5 seconds per test
- **Full stack**: Real API, database, AI (mocked)
- **User perspective**: Simulate real usage

### Example: Voice to Task Complete Flow

```python
import pytest
from httpx import AsyncClient

@pytest.mark.e2e
async def test_voice_to_task_complete_workflow(
    api_client: AsyncClient,
    db_session,
    mock_openai
):
    """Test complete voice → task creation → completion flow."""
    
    # 1. Send voice message (mocked AI calls)
    audio_data = load_test_audio("repair_mill.ogg")
    
    response = await api_client.post(
        "/tasks",
        json={
            "title": "Transcribed from voice",
            "business_id": 1,
            "created_via": "voice"
        }
    )
    
    assert response.status_code == 201
    task_data = response.json()
    task_id = task_data["id"]
    
    # 2. Verify task created
    assert task_data["title"] == "Transcribed from voice"
    assert task_data["business_id"] == 1
    assert task_data["status"] == "open"
    assert task_data["estimated_duration"] is not None
    
    # 3. Complete task
    response = await api_client.post(
        f"/tasks/{task_id}/complete",
        json={"actual_duration": 110}
    )
    
    assert response.status_code == 200
    completed_task = response.json()
    
    # 4. Verify completion
    assert completed_task["status"] == "done"
    assert completed_task["actual_duration"] == 110
    assert completed_task["completed_at"] is not None
    
    # 5. Verify learning (next task uses this data)
    response = await api_client.post(
        "/tasks",
        json={
            "title": "Similar repair task",
            "business_id": 1
        }
    )
    
    new_task = response.json()
    # Estimate should be influenced by previous task
    assert 90 <= new_task["estimated_duration"] <= 130  # Near 110 min
```

---

## 🎭 Mocking Strategy

### Mock External APIs

```python
import pytest
from unittest.mock import AsyncMock, patch

@pytest.fixture
def mock_openai():
    """Mock OpenAI API calls."""
    
    with patch('openai.AsyncOpenAI') as mock:
        # Mock Whisper
        mock.return_value.audio.transcriptions.create = AsyncMock(
            return_value=MockWhisperResponse(
                text="Починить фрезер для Иванова"
            )
        )
        
        # Mock GPT-5 Nano
        mock.return_value.chat.completions.create = AsyncMock(
            return_value=MockGPTResponse(
                content='{"title": "Починить фрезер", "business_id": 1}'
            )
        )
        
        yield mock


async def test_with_mocked_ai(mock_openai):
    """Test using mocked AI."""
    
    result = await parse_voice_task(audio_bytes)
    
    # Verify called correctly
    mock_openai.return_value.audio.transcriptions.create.assert_called_once()
    
    # Verify result
    assert result.title == "Починить фрезер"
```

---

## 📊 Coverage Requirements

### Target Coverage

| Component | Target | Critical |
|-----------|--------|----------|
| **Domain logic** | 95%+ | ⭐⭐⭐ |
| **API endpoints** | 90%+ | ⭐⭐⭐ |
| **Parsers/AI** | 85%+ | ⭐⭐ |
| **Infrastructure** | 70%+ | ⭐ |
| **Overall** | 80%+ | ⭐⭐ |

### Commands

```bash
# Run tests with coverage
pytest tests/ --cov=src --cov-report=html --cov-report=term

# View HTML report
open htmlcov/index.html

# Fail if coverage < 80%
pytest --cov-fail-under=80
```

---

## 🏷️ Test Markers

### Organize Tests

```python
# In pytest.ini
[pytest]
markers =
    unit: Unit tests (fast, isolated)
    integration: Integration tests (database, Redis)
    e2e: End-to-end tests (full workflows)
    slow: Slow tests (> 1 second)
    ai: Tests that use AI APIs

# Mark tests
@pytest.mark.unit
async def test_fast_unit():
    ...

@pytest.mark.integration
@pytest.mark.slow
async def test_database():
    ...
```

### Run Selectively

```bash
# Only unit tests
pytest -m unit

# Only integration
pytest -m integration

# Exclude slow
pytest -m "not slow"

# Only AI tests
pytest -m ai
```

---

## 🧪 Test Data (Fixtures)

### Realistic Russian Data

```python
from faker import Faker

fake = Faker('ru_RU')  # Russian locale

@pytest.fixture
def sample_tasks():
    """Realistic Russian task titles."""
    return [
        "Починить фрезер для клиента Иванова",
        "Диагностика платы компрессора",
        "Моделирование 3 коронок для клиники",
        "Разработать прототип нового наконечника",
        "Позвонить поставщику фрез из Китая"
    ]


@pytest.fixture
def business_keywords():
    """Keywords for each business."""
    return {
        1: ["фрезер", "ремонт", "диагностика"],
        2: ["коронка", "моделирование", "CAD"],
        3: ["прототип", "разработка", "workshop"],
        4: ["поставщик", "Китай", "контракт"]
    }
```

---

## 🎯 Critical Test Scenarios

### 1. Business Isolation (Critical! - ADR-003)

```python
@pytest.mark.integration
async def test_business_isolation_in_rag(db_session):
    """CRITICAL: Test RAG respects business boundaries."""
    
    # Create identical task titles in different businesses
    inventum_task = await create_task(
        "Диагностика оборудования",
        business_id=1,
        actual_duration=120
    )
    
    rd_task = await create_task(
        "Диагностика оборудования",  # Same title!
        business_id=3,
        actual_duration=240  # Different duration!
    )
    
    # Search from Inventum context
    similar = await find_similar_tasks(
        title="Диагностика оборудования",
        business_id=1
    )
    
    # CRITICAL: Must only return Inventum task
    assert len(similar) == 1
    assert similar[0].id == inventum_task.id
    assert similar[0].business_id == 1
    assert similar[0].actual_duration == 120  # NOT 240!
    
    # Verify R&D task NOT in results
    assert all(t.id != rd_task.id for t in similar)
```

### 2. RAG Learning Loop

```python
@pytest.mark.integration
async def test_rag_learning_improves_estimates():
    """Test that system learns from actual durations."""
    
    # Week 1: No history
    task1 = await create_task("Позвонить поставщику", business_id=4)
    assert task1.estimated_duration == 60  # Default
    
    # Complete
    await complete_task(task1.id, actual_duration=45)
    
    # Week 2: With history
    task2 = await create_task("Звонок поставщику", business_id=4)
    # Should be influenced by task1
    assert 40 <= task2.estimated_duration <= 50  # Near 45
    
    # Complete
    await complete_task(task2.id, actual_duration=42)
    
    # Week 3: More history
    task3 = await create_task("Связаться с поставщиком", business_id=4)
    # Should average task1 and task2
    assert 42 <= task3.estimated_duration <= 46  # Near 43.5
```

### 3. Voice Processing End-to-End

```python
@pytest.mark.e2e
@pytest.mark.slow
async def test_voice_to_task_e2e(mock_openai, db_session):
    """Test complete voice message processing."""
    
    # Prepare voice message
    audio = load_test_audio("repair_task.ogg")
    
    # Mock AI responses
    mock_openai.whisper.return_value = "Дима должен починить фрезер завтра утром"
    mock_openai.gpt5nano.return_value = {
        "title": "Починить фрезер",
        "business_id": 1,
        "deadline": "завтра утром",
        "assigned_to": "Дима",
        "priority": 1
    }
    
    # Process voice
    result = await process_voice_message(
        audio=audio,
        user_id=1,
        chat_id=123
    )
    
    # Verify task created
    assert result.task_id is not None
    assert result.business_id == 1
    assert result.assigned_member.name == "Дима"
    assert result.deadline.hour == 9  # утром = 09:00
    
    # Verify in database
    task = await task_repo.get_by_id(result.task_id)
    assert task.title == "Починить фрезер"
    assert task.business_id == 1
```

---

## 🎨 BDD Style Tests (Gherkin)

### Example Scenario

```gherkin
Feature: Voice Task Creation

  Scenario: User creates urgent repair task
    Given user is Константин (CEO)
    And user has Telegram account
    When user sends voice message "Срочно, Дима должен починить фрезер для Иванова сегодня к обеду"
    Then task is created with title "Починить фрезер для Иванова"
    And business is detected as "Inventum" (id: 1)
    And assigned to "Дима"
    And deadline is today at 13:00
    And priority is 1 (DO NOW)
    And user receives confirmation in Telegram
    
  Scenario: System learns from completion
    Given task "Позвонить поставщику" exists
    And estimated duration is 60 minutes (default)
    When user completes task with actual duration 45 minutes
    Then system stores actual_duration in database
    And next similar task should estimate ~45 minutes
```

---

## 🔄 Test Factories

### Task Factory

```python
from factory import Factory, Faker, SubFactory

class TaskFactory(Factory):
    class Meta:
        model = Task
    
    id = Faker('random_int', min=1, max=10000)
    user_id = 1
    business_id = Faker('random_int', min=1, max=4)
    title = Faker('sentence', locale='ru_RU')
    status = "open"
    priority = 2
    estimated_duration = Faker('random_int', min=30, max=240)
    
    # Russian-specific
    @classmethod
    def inventum_repair(cls, **kwargs):
        """Factory for Inventum repair tasks."""
        return cls(
            business_id=1,
            title=Faker('random_element', elements=[
                "Ремонт фрезера",
                "Диагностика платы",
                "Починить наконечник"
            ]),
            **kwargs
        )


# Usage
task = TaskFactory()
repair_task = TaskFactory.inventum_repair(assigned_to=3)  # Дима
```

---

## ⚡ Performance Tests (Optional)

### Load Testing

```python
import pytest
import asyncio

@pytest.mark.slow
async def test_concurrent_task_creation():
    """Test system handles concurrent requests."""
    
    # Create 10 tasks simultaneously
    tasks = await asyncio.gather(*[
        create_task(f"Task {i}", business_id=1)
        for i in range(10)
    ])
    
    # Verify all created
    assert len(tasks) == 10
    assert all(t.id is not None for t in tasks)


async def test_rag_search_performance():
    """Test vector search is fast enough."""
    
    # Create 1000 tasks with embeddings
    for i in range(1000):
        await create_task_with_embedding(...)
    
    # Measure search time
    start = time.time()
    results = await find_similar_tasks(embedding=test_embedding, business_id=1)
    duration = (time.time() - start) * 1000
    
    # Should be < 100ms
    assert duration < 100, f"Search took {duration}ms, expected < 100ms"
```

---

## 📊 Quality Metrics

### Test Metrics

```bash
# Run tests with metrics
pytest tests/ -v --durations=10 --cov=src

# Output:
# ===== slowest 10 test durations =====
# 2.45s test_voice_to_task_e2e
# 1.23s test_rag_search_performance
# 0.85s test_database_integration
# ...

# Coverage report:
# src/domain/services/task_service.py    98%
# src/api/routes/tasks.py                95%
# src/ai/parsers/task_parser.py          87%
# ...
# TOTAL                                  82%
```

---

## ✅ Pre-Commit Testing

### Git Hook

```.git/hooks/pre-commit
#!/bin/bash

# Run fast tests before commit
pytest tests/unit -q

if [ $? -ne 0 ]; then
    echo "❌ Tests failed. Commit aborted."
    exit 1
fi

echo "✅ Tests passed"
```

---

## 🎯 Test Naming Convention

### Format

```
test_should_[expected]_when_[condition]
```

### Examples

```python
# ✅ GOOD: Descriptive
async def test_should_create_task_when_valid_data():
    ...

async def test_should_raise_error_when_invalid_business_id():
    ...

async def test_should_filter_by_business_when_searching_similar_tasks():
    ...

# ❌ BAD: Vague
async def test_task():
    ...

async def test_1():
    ...
```

---

## 🚀 Running Tests

### Development

```bash
# All tests
pytest

# Fast only (unit)
pytest tests/unit

# With coverage
pytest --cov=src --cov-report=html

# Specific file
pytest tests/unit/test_parsers.py

# Specific test
pytest tests/unit/test_parsers.py::test_should_parse_business_context

# Verbose
pytest -v

# Stop on first failure
pytest -x

# Failed tests only (rerun)
pytest --lf
```

### CI/CD

```bash
# In GitHub Actions (ci.yml)
pytest tests/ \
  --cov=src \
  --cov-report=xml \
  --cov-fail-under=80 \
  -v
```

---

## 📖 References

- Pytest: https://docs.pytest.org/
- pytest-asyncio: https://pytest-asyncio.readthedocs.io/
- Coverage.py: https://coverage.readthedocs.io/
- .cursorrules (Testing Requirements section)

---

**Status**: ✅ Testing Strategy Complete  
**Test Types**: Unit (80%), Integration (15%), E2E (5%)  
**Target Coverage**: 80%+ overall  
**Critical Focus**: Business isolation, RAG learning  
**Framework**: pytest + pytest-asyncio

