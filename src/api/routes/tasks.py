"""
Tasks API Routes - Business Planner.

REST API endpoints for task management.

Reference:
- docs/03-api/openapi.yaml
- .cursorrules (FastAPI patterns)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.models import Task, TaskCreate, TaskUpdate, TaskComplete
from src.infrastructure.database import get_session
from src.infrastructure.database.repositories.task_repository import TaskRepository
from src.utils.logger import logger


router = APIRouter()


# ============================================================================
# Dependencies
# ============================================================================

async def get_task_repository(
    session: AsyncSession = Depends(get_session)
) -> TaskRepository:
    """Get task repository dependency.
    
    Reference: .cursorrules (Dependency Injection section)
    """
    return TaskRepository(session)


# ============================================================================
# Endpoints
# ============================================================================

@router.post("/", response_model=Task, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    user_id: int = 1,  # TODO: Get from auth
    repo: TaskRepository = Depends(get_task_repository)
) -> Task:
    """Create new task.
    
    Args:
        task_data: Task creation data
        user_id: User ID (from auth)
        repo: Task repository
        
    Returns:
        Created task
        
    Raises:
        HTTPException: If validation fails
    """
    
    logger.info(
        "api_create_task",
        title=task_data.title,
        business_id=task_data.business_id,
        user_id=user_id
    )
    
    try:
        task = await repo.create(task_data, user_id=user_id)
        return task
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )


@router.get("/{task_id}", response_model=Task)
async def get_task(
    task_id: int,
    repo: TaskRepository = Depends(get_task_repository)
) -> Task:
    """Get task by ID.
    
    Args:
        task_id: Task ID
        repo: Task repository
        
    Returns:
        Task
        
    Raises:
        HTTPException: If task not found
    """
    
    task = await repo.get_by_id(task_id)
    
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found"
        )
    
    return task


@router.get("/", response_model=list[Task])
async def list_tasks(
    business_id: int | None = None,
    status: str | None = None,
    limit: int = 100,
    user_id: int = 1,  # TODO: Get from auth
    repo: TaskRepository = Depends(get_task_repository)
) -> list[Task]:
    """List tasks with optional filtering.
    
    Args:
        business_id: Filter by business (1-4)
        status: Filter by status (open, done, archived)
        limit: Maximum results
        user_id: User ID (from auth)
        repo: Task repository
        
    Returns:
        List of tasks
    """
    
    if business_id:
        tasks = await repo.find_by_business(
            user_id=user_id,
            business_id=business_id,
            status=status,
            limit=limit
        )
    else:
        # TODO: Implement find_all method
        tasks = []
    
    return tasks


@router.patch("/{task_id}", response_model=Task)
async def update_task(
    task_id: int,
    task_data: TaskUpdate,
    repo: TaskRepository = Depends(get_task_repository)
) -> Task:
    """Update task (partial update).
    
    Args:
        task_id: Task ID
        task_data: Fields to update
        repo: Task repository
        
    Returns:
        Updated task
    """
    
    try:
        task = await repo.update(task_id, task_data)
        return task
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.post("/{task_id}/complete", response_model=Task)
async def complete_task(
    task_id: int,
    completion_data: TaskComplete,
    repo: TaskRepository = Depends(get_task_repository)
) -> Task:
    """Mark task as completed with actual duration.
    
    Triggers learning feedback loop (ADR-004).
    
    Args:
        task_id: Task ID
        completion_data: Completion data with actual_duration
        repo: Task repository
        
    Returns:
        Completed task
    """
    
    try:
        task = await repo.complete(task_id, completion_data.actual_duration)
        
        logger.info(
            "task_completed_via_api",
            task_id=task_id,
            actual_duration=completion_data.actual_duration,
            accuracy=task.estimation_accuracy
        )
        
        return task
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int,
    repo: TaskRepository = Depends(get_task_repository)
) -> None:
    """Delete task (soft delete to archived).
    
    Args:
        task_id: Task ID
        repo: Task repository
    """
    
    try:
        await repo.delete(task_id)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

