"""
Task Repository - Business Planner.

Repository pattern for Task aggregate root.
All database access for tasks goes through this repository.

Reference:
- .cursorrules (Repository Pattern section)
- docs/04-domain/entities.md (Task Entity)
- ADR-003 (Business Isolation - CRITICAL)
"""

from datetime import date, datetime
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.models import Task, TaskCreate, TaskUpdate
from src.infrastructure.database.models import TaskORM
from src.utils.logger import logger


class TaskRepository:
    """Repository for Task aggregate.
    
    Handles all database operations for tasks.
    Enforces business isolation (ADR-003).
    """
    
    def __init__(self, session: AsyncSession):
        """Initialize repository with database session.
        
        Args:
            session: SQLAlchemy async session
        """
        self.session = session
    
    async def create(self, task_data: TaskCreate, user_id: int) -> Task:
        """Create new task.
        
        Args:
            task_data: Task creation data
            user_id: Task owner ID
            
        Returns:
            Created task
            
        Example:
            >>> task = await repo.create(
            ...     TaskCreate(title="Test", business_id=1),
            ...     user_id=1
            ... )
        """
        task_orm = TaskORM(
            user_id=user_id,
            **task_data.model_dump(exclude_unset=True, exclude={"created_via", "deadline_text"})
        )
        
        self.session.add(task_orm)
        await self.session.commit()
        await self.session.refresh(task_orm)
        
        logger.info(
            "task_created",
            task_id=task_orm.id,
            business_id=task_orm.business_id,
            user_id=user_id,
            title=task_orm.title
        )
        
        return Task.model_validate(task_orm)
    
    async def get_by_id(self, task_id: int) -> Task | None:
        """Get task by ID.
        
        Args:
            task_id: Task ID
            
        Returns:
            Task or None if not found
        """
        result = await self.session.execute(
            select(TaskORM).where(TaskORM.id == task_id)
        )
        task_orm = result.scalar_one_or_none()
        
        if task_orm is None:
            return None
        
        return Task.model_validate(task_orm)
    
    async def find_by_business(
        self,
        user_id: int,
        business_id: int,
        status: str | None = None,
        limit: int = 100
    ) -> list[Task]:
        """Find tasks by business context.
        
        CRITICAL: Filters by business_id for isolation (ADR-003).
        
        Args:
            user_id: User ID
            business_id: Business context (1-4)
            status: Optional status filter
            limit: Maximum results
            
        Returns:
            List of tasks in this business context
        """
        query = select(TaskORM).where(
            and_(
                TaskORM.user_id == user_id,
                TaskORM.business_id == business_id  # CRITICAL: Business isolation
            )
        )
        
        if status:
            query = query.where(TaskORM.status == status)
        
        query = query.limit(limit).order_by(TaskORM.created_at.desc())
        
        result = await self.session.execute(query)
        tasks_orm = result.scalars().all()
        
        return [Task.model_validate(t) for t in tasks_orm]
    
    async def find_similar(
        self,
        embedding: list[float],
        business_id: int,  # MANDATORY (ADR-003)
        limit: int = 5,
        similarity_threshold: float = 0.7
    ) -> list[Task]:
        """Find similar tasks using vector similarity (RAG).
        
        CRITICAL: MUST filter by business_id to prevent cross-context contamination.
        This is a fundamental architectural constraint (ADR-003).
        
        Args:
            embedding: Task embedding vector (1536 dimensions)
            business_id: Business context for isolation (MANDATORY)
            limit: Number of results
            similarity_threshold: Minimum similarity (0-1)
            
        Returns:
            List of similar tasks (same business only)
            
        Reference:
            - ADR-003 (Business Isolation)
            - ADR-004 (RAG Strategy)
            - docs/02-database/schema.sql (find_similar_tasks function)
        """
        # Validate business_id
        if business_id not in [1, 2, 3, 4]:
            raise ValueError(f"Invalid business_id: {business_id}")
        
        # Query using pgvector cosine distance
        # 1 - (embedding <=> other) = similarity (0-1)
        query = select(TaskORM).where(
            and_(
                TaskORM.business_id == business_id,  # CRITICAL: Business isolation!
                TaskORM.embedding.isnot(None),
                TaskORM.actual_duration.isnot(None),  # Only completed tasks
                TaskORM.status == "done"
            )
        ).order_by(
            TaskORM.embedding.cosine_distance(embedding)
        ).limit(limit)
        
        result = await self.session.execute(query)
        tasks_orm = result.scalars().all()
        
        # Convert to domain models
        tasks = [Task.model_validate(t) for t in tasks_orm]
        
        # Paranoid validation (ADR-003)
        for task in tasks:
            assert task.business_id == business_id, \
                f"RAG isolation breach! Expected business {business_id}, got {task.business_id}"
        
        logger.info(
            "rag_search_completed",
            business_id=business_id,
            similar_tasks_found=len(tasks),
            limit=limit
        )
        
        return tasks
    
    async def update(self, task_id: int, task_data: TaskUpdate) -> Task:
        """Update task.
        
        Args:
            task_id: Task ID
            task_data: Updated fields
            
        Returns:
            Updated task
            
        Raises:
            ValueError: If task not found
        """
        result = await self.session.execute(
            select(TaskORM).where(TaskORM.id == task_id)
        )
        task_orm = result.scalar_one_or_none()
        
        if task_orm is None:
            raise ValueError(f"Task {task_id} not found")
        
        # Update fields
        update_data = task_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(task_orm, field, value)
        
        await self.session.commit()
        await self.session.refresh(task_orm)
        
        logger.info("task_updated", task_id=task_id)
        
        return Task.model_validate(task_orm)
    
    async def complete(self, task_id: int, actual_duration: int) -> Task:
        """Mark task as completed with actual duration.
        
        Triggers learning feedback loop (ADR-004).
        
        Args:
            task_id: Task ID
            actual_duration: Actual time spent (minutes)
            
        Returns:
            Completed task
        """
        task = await self.get_by_id(task_id)
        if task is None:
            raise ValueError(f"Task {task_id} not found")
        
        if task.status == "done":
            raise ValueError("Task already completed")

        # Update in database
        result = await self.session.execute(
            select(TaskORM).where(TaskORM.id == task_id)
        )
        task_orm = result.scalar_one()

        task_orm.status = "done"
        task_orm.actual_duration = actual_duration
        task_orm.completed_at = func.now()
        
        await self.session.commit()
        await self.session.refresh(task_orm)
        
        # Log learning data
        completed_task = Task.model_validate(task_orm)
        
        logger.info(
            "task_completed_learning",
            task_id=task_id,
            business_id=completed_task.business_id,
            estimated_duration=completed_task.estimated_duration,
            actual_duration=actual_duration,
            accuracy=completed_task.estimation_accuracy
        )
        
        return completed_task
    
    async def delete(self, task_id: int) -> None:
        """Delete task (soft delete to archived).
        
        Args:
            task_id: Task ID
        """
        result = await self.session.execute(
            select(TaskORM).where(TaskORM.id == task_id)
        )
        task_orm = result.scalar_one_or_none()
        
        if task_orm is None:
            raise ValueError(f"Task {task_id} not found")
        
        # Soft delete (archive)
        task_orm.status = "archived"
        
        await self.session.commit()
        
        logger.info("task_deleted", task_id=task_id)
    
    async def update_embedding(self, task_id: int, embedding: list[float]) -> None:
        """Update task embedding (async, after task created).
        
        Args:
            task_id: Task ID
            embedding: Vector embedding (1536 dimensions)
        """
        result = await self.session.execute(
            select(TaskORM).where(TaskORM.id == task_id)
        )
        task_orm = result.scalar_one_or_none()
        
        if task_orm:
            task_orm.embedding = embedding
            await self.session.commit()
            
            logger.debug("task_embedding_updated", task_id=task_id)
    
    async def find_by_deadline(
        self,
        user_id: int,
        date: date,
        status: str = "open"
    ) -> list[Task]:
        """Find tasks with deadline on specific date.
        
        Used for /today command.
        
        Args:
            user_id: User ID
            date: Deadline date
            status: Task status (default: "open")
            
        Returns:
            List of tasks with this deadline
        """
        # Convert date to datetime range (start of day to end of day)
        start_datetime = datetime.combine(date, datetime.min.time())
        end_datetime = datetime.combine(date, datetime.max.time())
        
        query = select(TaskORM).where(
            and_(
                TaskORM.user_id == user_id,
                TaskORM.status == status,
                TaskORM.deadline >= start_datetime,
                TaskORM.deadline <= end_datetime
            )
        ).order_by(TaskORM.priority, TaskORM.deadline)
        
        result = await self.session.execute(query)
        tasks_orm = result.scalars().all()
        
        return [Task.model_validate(t) for t in tasks_orm]
    
    async def find_by_date_range(
        self,
        user_id: int,
        start_date: date,
        end_date: date,
        status: str = "open"
    ) -> list[Task]:
        """Find tasks with deadline in date range.
        
        Used for /week command.
        
        Args:
            user_id: User ID
            start_date: Range start (inclusive)
            end_date: Range end (inclusive)
            status: Task status (default: "open")
            
        Returns:
            List of tasks in this date range
        """
        # Convert dates to datetime
        start_datetime = datetime.combine(start_date, datetime.min.time())
        end_datetime = datetime.combine(end_date, datetime.max.time())
        
        query = select(TaskORM).where(
            and_(
                TaskORM.user_id == user_id,
                TaskORM.status == status,
                TaskORM.deadline >= start_datetime,
                TaskORM.deadline <= end_datetime
            )
        ).order_by(TaskORM.deadline, TaskORM.priority)
        
        result = await self.session.execute(query)
        tasks_orm = result.scalars().all()
        
        return [Task.model_validate(t) for t in tasks_orm]

