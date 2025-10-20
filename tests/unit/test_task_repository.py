"""
Unit Tests - TaskRepository (CRUD Operations).

Tests all database operations for tasks.

Reference: src/infrastructure/database/repositories/task_repository.py
"""

import pytest
from datetime import datetime, date, timedelta

from src.infrastructure.database.repositories.task_repository import TaskRepository
from src.domain.models import TaskCreate, TaskUpdate, Task
from src.domain.models.enums import TaskStatus, Priority

# Mark all tests in this module as asyncio
pytestmark = pytest.mark.asyncio


# ============================================================================
# Create Task Tests
# ============================================================================

@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_task_minimal(test_session, test_user, test_business):
    """Test creating task with minimal required fields."""

    repo = TaskRepository(test_session)

    task_data = TaskCreate(
        title="Test task",
        business_id=test_business.id
    )

    task = await repo.create(task_data, user_id=test_user.id)

    # Check task was created
    assert task.id is not None
    assert task.title == "Test task"
    assert task.business_id == test_business.id
    # Note: created_by_id not exposed in Task model (only in ORM)
    assert task.status == TaskStatus.PENDING
    assert task.priority == Priority.MEDIUM  # Default


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_task_full_data(test_session, test_user, test_business, test_member):
    """Test creating task with all fields populated."""

    repo = TaskRepository(test_session)

    deadline = datetime.now() + timedelta(days=1)

    task_data = TaskCreate(
        title="Починить фрезер для Иванова",
        business_id=test_business.id,
        priority=Priority.HIGH,
        assigned_to=test_member.id,
        estimated_duration=120,  # 2 hours
        deadline=deadline,
        deadline_text="завтра",
        description="Срочно!"
    )

    task = await repo.create(task_data, user_id=test_user.id)

    # Verify all fields
    assert task.title == "Починить фрезер для Иванова"
    assert task.priority == Priority.HIGH
    assert task.assigned_to == test_member.id
    assert task.estimated_duration == 120
    assert task.deadline is not None
    assert task.description == "Срочно!"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_task_default_values(test_session, test_user, test_business):
    """Test that default values are set correctly."""

    repo = TaskRepository(test_session)

    task_data = TaskCreate(
        title="Test",
        business_id=test_business.id
    )

    task = await repo.create(task_data, user_id=test_user.id)

    # Check defaults
    assert task.status == TaskStatus.PENDING
    assert task.priority == Priority.MEDIUM
    assert task.created_at is not None
    assert task.updated_at is not None


# ============================================================================
# Get Task Tests
# ============================================================================

@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_task_by_id_exists(test_session, test_task):
    """Test getting existing task by ID."""

    repo = TaskRepository(test_session)

    task = await repo.get_by_id(test_task.id)

    assert task is not None
    assert task.id == test_task.id
    assert task.title == test_task.title


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_task_by_id_not_found(test_session):
    """Test getting non-existent task returns None."""

    repo = TaskRepository(test_session)

    task = await repo.get_by_id(99999)

    assert task is None


# ============================================================================
# Update Task Tests
# ============================================================================

@pytest.mark.unit
@pytest.mark.asyncio
async def test_update_task_title(test_session, test_task):
    """Test updating task title."""

    repo = TaskRepository(test_session)

    update_data = TaskUpdate(title="Updated title")
    updated_task = await repo.update(test_task.id, update_data)

    assert updated_task.title == "Updated title"
    assert updated_task.id == test_task.id


@pytest.mark.unit
@pytest.mark.asyncio
async def test_update_task_priority(test_session, test_task):
    """Test updating task priority."""

    repo = TaskRepository(test_session)

    update_data = TaskUpdate(priority=Priority.HIGH)
    updated_task = await repo.update(test_task.id, update_data)

    assert updated_task.priority == Priority.HIGH


@pytest.mark.unit
@pytest.mark.asyncio
async def test_update_task_multiple_fields(test_session, test_task):
    """Test updating multiple fields at once."""

    repo = TaskRepository(test_session)

    new_deadline = datetime.now() + timedelta(days=2)

    update_data = TaskUpdate(
        title="New title",
        priority=Priority.LOW,
        deadline=new_deadline,
        description="Updated description"
    )

    updated_task = await repo.update(test_task.id, update_data)

    assert updated_task.title == "New title"
    assert updated_task.priority == Priority.LOW
    assert updated_task.description == "Updated description"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_update_task_not_found(test_session):
    """Test updating non-existent task raises error."""

    repo = TaskRepository(test_session)

    update_data = TaskUpdate(title="New title")

    with pytest.raises(ValueError, match="not found"):
        await repo.update(99999, update_data)


# ============================================================================
# Complete Task Tests
# ============================================================================

@pytest.mark.unit
@pytest.mark.asyncio
async def test_complete_task_success(test_session, test_task):
    """Test completing a task with actual duration."""

    repo = TaskRepository(test_session)

    completed_task = await repo.complete(test_task.id, actual_duration=100)

    assert completed_task.status == TaskStatus.COMPLETED
    assert completed_task.actual_duration == 100
    assert completed_task.completed_at is not None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_complete_task_calculates_accuracy(test_session, test_user, test_business):
    """Test that estimation accuracy is calculated correctly."""

    repo = TaskRepository(test_session)

    # Create task with estimated duration
    task_data = TaskCreate(
        title="Test",
        business_id=test_business.id,
        estimated_duration=120  # 2 hours
    )

    task = await repo.create(task_data, user_id=test_user.id)

    # Complete with actual duration
    completed_task = await repo.complete(task.id, actual_duration=100)

    # Check accuracy calculation (should be around 83%)
    assert completed_task.estimation_accuracy is not None
    assert 80 <= completed_task.estimation_accuracy <= 85


@pytest.mark.unit
@pytest.mark.asyncio
async def test_complete_task_not_found(test_session):
    """Test completing non-existent task raises error."""

    repo = TaskRepository(test_session)

    with pytest.raises(ValueError, match="not found"):
        await repo.complete(99999, actual_duration=60)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_complete_task_already_completed(test_session, test_user, test_business):
    """Test completing already completed task raises error."""

    repo = TaskRepository(test_session)

    # Create and complete task
    task_data = TaskCreate(title="Test", business_id=test_business.id)
    task = await repo.create(task_data, user_id=test_user.id)
    await repo.complete(task.id, actual_duration=60)

    # Try to complete again
    with pytest.raises(ValueError, match="already completed"):
        await repo.complete(task.id, actual_duration=60)


# ============================================================================
# Delete Task Tests
# ============================================================================

@pytest.mark.unit
@pytest.mark.asyncio
async def test_delete_task_soft_delete(test_session, test_task):
    """Test that delete is a soft delete (archives task)."""

    repo = TaskRepository(test_session)

    await repo.delete(test_task.id)

    # Task should still exist but be archived
    deleted_task = await repo.get_by_id(test_task.id)
    assert deleted_task is not None
    assert deleted_task.status == TaskStatus.ARCHIVED


@pytest.mark.unit
@pytest.mark.asyncio
async def test_delete_task_not_found(test_session):
    """Test deleting non-existent task raises error."""

    repo = TaskRepository(test_session)

    with pytest.raises(ValueError, match="not found"):
        await repo.delete(99999)


# ============================================================================
# Find Tasks Tests
# ============================================================================

@pytest.mark.unit
@pytest.mark.asyncio
async def test_find_by_business(test_session, test_user, test_business):
    """Test finding tasks filtered by business."""

    repo = TaskRepository(test_session)

    # Create tasks in different businesses
    task1 = TaskCreate(title="Task 1", business_id=1)
    task2 = TaskCreate(title="Task 2", business_id=1)
    task3 = TaskCreate(title="Task 3", business_id=2)

    await repo.create(task1, user_id=test_user.id)
    await repo.create(task2, user_id=test_user.id)
    await repo.create(task3, user_id=test_user.id)

    # Find tasks for business 1
    tasks = await repo.find_by_business(
        user_id=test_user.id,
        business_id=1
    )

    # Should only get business 1 tasks
    assert len(tasks) == 2
    assert all(t.business_id == 1 for t in tasks)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_find_by_business_with_status_filter(test_session, test_user, test_business):
    """Test finding tasks filtered by business and status."""

    repo = TaskRepository(test_session)

    # Create tasks with different statuses
    task1 = TaskCreate(title="Open task", business_id=test_business.id)
    task2 = TaskCreate(title="Another open", business_id=test_business.id)

    t1 = await repo.create(task1, user_id=test_user.id)
    t2 = await repo.create(task2, user_id=test_user.id)

    # Complete one task
    await repo.complete(t1.id, actual_duration=60)

    # Find only open tasks
    open_tasks = await repo.find_by_business(
        user_id=test_user.id,
        business_id=test_business.id,
        status="open"
    )

    assert len(open_tasks) == 1
    assert open_tasks[0].id == t2.id


@pytest.mark.unit
@pytest.mark.asyncio
async def test_find_by_deadline_specific_date(test_session, test_user, test_tasks_multiple):
    """Test finding tasks by specific deadline date."""

    repo = TaskRepository(test_session)

    today = datetime.now().date()

    # Find tasks for today
    today_tasks = await repo.find_by_deadline(
        user_id=test_user.id,
        date=today
    )

    # Should get 2 tasks (high priority + medium priority for today)
    assert len(today_tasks) >= 2

    # All should have deadline on today
    for task in today_tasks:
        assert task.deadline.date() == today


@pytest.mark.unit
@pytest.mark.asyncio
async def test_find_by_deadline_empty_result(test_session, test_user):
    """Test finding tasks for date with no tasks."""

    repo = TaskRepository(test_session)

    future_date = date.today() + timedelta(days=365)

    tasks = await repo.find_by_deadline(
        user_id=test_user.id,
        date=future_date
    )

    assert len(tasks) == 0


@pytest.mark.unit
@pytest.mark.asyncio
async def test_find_by_date_range(test_session, test_user, test_tasks_multiple):
    """Test finding tasks in date range (week)."""

    repo = TaskRepository(test_session)

    today = datetime.now().date()
    week_end = today + timedelta(days=7)

    tasks = await repo.find_by_date_range(
        user_id=test_user.id,
        start_date=today,
        end_date=week_end
    )

    # Should get tasks within 7 days
    assert len(tasks) >= 3

    # All should be within range
    for task in tasks:
        assert today <= task.deadline.date() <= week_end


@pytest.mark.unit
@pytest.mark.asyncio
async def test_find_by_date_range_ordering(test_session, test_user, test_tasks_multiple):
    """Test that tasks are ordered by deadline, then priority."""

    repo = TaskRepository(test_session)

    today = datetime.now().date()
    week_end = today + timedelta(days=7)

    tasks = await repo.find_by_date_range(
        user_id=test_user.id,
        start_date=today,
        end_date=week_end
    )

    # Check ordering (earliest deadline first)
    for i in range(len(tasks) - 1):
        assert tasks[i].deadline <= tasks[i + 1].deadline


# ============================================================================
# Business Isolation Tests (ADR-003)
# ============================================================================

@pytest.mark.unit
@pytest.mark.asyncio
async def test_business_isolation_enforced(test_session, test_user):
    """Test that business isolation is enforced (CRITICAL)."""

    repo = TaskRepository(test_session)

    # Create tasks in different businesses
    task1 = TaskCreate(title="Inventum task", business_id=1)
    task2 = TaskCreate(title="Lab task", business_id=2)

    await repo.create(task1, user_id=test_user.id)
    await repo.create(task2, user_id=test_user.id)

    # Query for business 1
    business1_tasks = await repo.find_by_business(
        user_id=test_user.id,
        business_id=1
    )

    # Should ONLY get business 1 tasks (isolation!)
    assert len(business1_tasks) == 1
    assert all(t.business_id == 1 for t in business1_tasks)

    # Verify no cross-contamination
    business2_tasks = await repo.find_by_business(
        user_id=test_user.id,
        business_id=2
    )

    assert len(business2_tasks) == 1
    assert all(t.business_id == 2 for t in business2_tasks)


# ============================================================================
# Embedding Tests
# ============================================================================

@pytest.mark.unit
@pytest.mark.asyncio
async def test_update_embedding(test_session, test_task):
    """Test updating task embedding vector."""

    repo = TaskRepository(test_session)

    # Create dummy embedding (1536 dimensions)
    embedding = [0.1] * 1536

    await repo.update_embedding(test_task.id, embedding)

    # Verify embedding was stored
    updated_task = await repo.get_by_id(test_task.id)
    assert updated_task.embedding is not None
    assert len(updated_task.embedding) == 1536


@pytest.mark.unit
@pytest.mark.asyncio
async def test_update_embedding_nonexistent_task(test_session):
    """Test updating embedding for non-existent task (should not crash)."""

    repo = TaskRepository(test_session)

    embedding = [0.1] * 1536

    # Should not raise error (graceful handling)
    await repo.update_embedding(99999, embedding)


# ============================================================================
# Edge Cases
# ============================================================================

@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_task_with_null_deadline(test_session, test_user, test_business):
    """Test creating task with no deadline."""

    repo = TaskRepository(test_session)

    task_data = TaskCreate(
        title="No deadline task",
        business_id=test_business.id,
        deadline=None
    )

    task = await repo.create(task_data, user_id=test_user.id)

    assert task.deadline is None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_find_tasks_respects_limit(test_session, test_user, test_business):
    """Test that find_by_business respects limit parameter."""

    repo = TaskRepository(test_session)

    # Create 10 tasks
    for i in range(10):
        task_data = TaskCreate(title=f"Task {i}", business_id=test_business.id)
        await repo.create(task_data, user_id=test_user.id)

    # Query with limit=5
    tasks = await repo.find_by_business(
        user_id=test_user.id,
        business_id=test_business.id,
        limit=5
    )

    assert len(tasks) == 5
