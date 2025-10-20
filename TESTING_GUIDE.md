# Testing Guide - Business Planner

## Overview

This document describes the testing strategy and how to run tests for the Business Planner project.

## Test Structure

```
tests/
├── conftest.py              # Shared fixtures and configuration
├── unit/                    # Unit tests (fast, isolated)
│   ├── test_format_response.py      # Message formatting tests
│   ├── test_task_parser.py           # Task parsing and mapping tests
│   └── test_task_repository.py       # Database CRUD tests
├── integration/             # Integration tests (database, APIs)
└── e2e/                     # End-to-end tests
```

## Running Tests

### Prerequisites

```bash
# Install development dependencies
pip install -r requirements-dev.txt
```

Key test dependencies:
- `pytest` - Test framework
- `pytest-asyncio` - Async test support
- `aiosqlite` - SQLite async driver for tests
- `pytest-cov` - Coverage reporting
- `pytest-mock` - Mocking support

### Run All Tests

```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=src --cov-report=html
```

### Run Specific Test Suites

```bash
# Run only unit tests (fast)
python -m pytest -m unit

# Run only integration tests
python -m pytest -m integration

# Run specific test file
python -m pytest tests/unit/test_format_response.py

# Run specific test
python -m pytest tests/unit/test_format_response.py::test_format_response_success_minimal
```

### Verbose Output

```bash
# Verbose mode with short traceback
python -m pytest -v --tb=short

# Very verbose (show all output)
python -m pytest -vv --tb=long
```

## Test Markers

Tests are organized using pytest markers:

- `@pytest.mark.unit` - Fast, isolated unit tests
- `@pytest.mark.integration` - Tests with database/Redis
- `@pytest.mark.e2e` - End-to-end workflow tests
- `@pytest.mark.slow` - Tests that take > 1 second
- `@pytest.mark.ai` - Tests using AI APIs (may cost money)
- `@pytest.mark.asyncio` - Async tests

## Test Coverage

### Current Coverage (Phase 5 - Initial)

**Completed:**
- ✅ Message formatting (`format_response_node`) - 24/24 tests passing
- ✅ Task parsing (GPT-5 Nano integration) - Mocked tests
- ✅ Deadline parsing and user ID mapping
- ✅ Business ID detection
- ✅ Priority level parsing

**In Progress:**
- 🔄 Task Repository CRUD operations (created, needs fixture fixes)
- 🔄 Database fixtures (SQLite compatibility issues being resolved)

**Not Yet Covered:**
- ⏳ Command handlers (`/today`, `/week`, `/create`, etc.)
- ⏳ Callback handlers (button interactions)
- ⏳ Voice task creation workflow
- ⏳ RAG retrieval
- ⏳ Weekly analytics

### Coverage Goals

- **Phase 5 Target**: 60% unit test coverage
- **Phase 6 Target**: 80% overall coverage (unit + integration)

## Writing Tests

### Unit Test Example

```python
import pytest

@pytest.mark.unit
@pytest.mark.asyncio
async def test_format_response_success():
    """Test formatting successful response."""

    state = {
        "parsed_title": "Fix the machine",
        "parsed_business_id": 1,
        "parsed_priority": 2,
        # ... other fields
    }

    result = await format_response_node(state)

    assert "ЗАДАЧА СОЗДАНА" in result["telegram_response"]
    assert "Fix the machine" in result["telegram_response"]
```

### Using Fixtures

```python
@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_task(test_session, test_user, test_business):
    """Test creating a task in database."""

    repo = TaskRepository(test_session)

    task_data = TaskCreate(
        title="Test task",
        business_id=test_business.id
    )

    task = await repo.create(task_data, user_id=test_user.id)

    assert task.id is not None
    assert task.title == "Test task"
```

### Mocking External APIs

```python
from unittest.mock import AsyncMock, patch

@pytest.mark.unit
@pytest.mark.asyncio
async def test_with_mocked_openai(mock_openai_client):
    """Test with mocked OpenAI API."""

    with patch('src.ai.parsers.task_parser.openai_client', mock_openai_client):
        mock_openai_client.parse_task = AsyncMock(return_value={
            "title": "Test task",
            "business_id": 1
        })

        result = await parse_task_from_transcript("Test", user_id=1)

        assert result.title == "Test task"
```

## Fixtures

### Database Fixtures

- `test_db_engine` - In-memory SQLite database engine
- `test_session` - Async database session
- `test_user` - Test user (Telegram ID: 123456)
- `test_business` - Test business (Inventum)
- `test_member` - Test team member (Максим)
- `test_task` - Sample test task
- `test_tasks_multiple` - Multiple tasks with different dates/priorities

### Mock Fixtures

- `mock_openai_client` - Mocked OpenAI client
- `mock_telegram_update` - Mocked Telegram Update object
- `mock_telegram_context` - Mocked Telegram Context

### Helper Fixtures

- `sample_voice_bytes` - Dummy audio data
- `sample_transcript` - Russian voice transcript

## CI/CD Integration (Future)

When adding CI/CD, configure to run:

```yaml
# Example GitHub Actions
- name: Run tests
  run: |
    pip install -r requirements-dev.txt
    pytest tests/ -v --cov=src --cov-report=xml

- name: Upload coverage
  uses: codecov/codecov-action@v3
```

## Debugging Failed Tests

### Show Full Output

```bash
# Disable output capture
python -m pytest -s

# Show local variables in traceback
python -m pytest -l --tb=long
```

### Run Single Test

```bash
# Run one test for debugging
python -m pytest tests/unit/test_format_response.py::test_name -vv -s
```

### Use pdb Debugger

```python
import pytest

def test_something():
    result = calculate_something()
    pytest.set_trace()  # Breakpoint
    assert result == expected
```

## Known Issues

### SQLite Compatibility

Some tests require PostgreSQL-specific features:
- Vector embeddings (pgvector)
- ARRAY columns
- JSONB columns

For tests, we use compatibility shims:
- `Vector` → `JSON` (array of floats)
- `ARRAY` → `JSON` (array)
- `JSONB` → `JSON`

These are automatically handled in `src/infrastructure/database/models.py`.

### Async Fixtures

All database fixtures are async and must be used with `@pytest.mark.asyncio`:

```python
@pytest.mark.asyncio
async def test_with_db(test_session):
    # test code
```

## Best Practices

1. **Test Naming**: Use descriptive names like `test_create_task_with_deadline`
2. **AAA Pattern**: Arrange, Act, Assert
3. **One Assertion Per Test**: Keep tests focused
4. **Use Fixtures**: Don't repeat setup code
5. **Mock External APIs**: Don't hit real APIs in tests
6. **Fast Tests**: Unit tests should run in < 100ms

## Resources

- [pytest Documentation](https://docs.pytest.org/)
- [pytest-asyncio](https://pytest-asyncio.readthedocs.io/)
- [SQLAlchemy Testing](https://docs.sqlalchemy.org/en/20/orm/session_transaction.html#joining-a-session-into-an-external-transaction-such-as-for-test-suites)

## Next Steps

1. Fix database fixture compatibility issues
2. Add command handler tests
3. Add integration tests with real database
4. Set up coverage reporting
5. Add E2E tests for full workflows
6. Configure CI/CD to run tests automatically
