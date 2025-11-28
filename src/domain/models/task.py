"""
Task Domain Models - Business Planner.

Task is the main aggregate root in the system.

Reference: 
- docs/04-domain/entities.md (Task Entity)
- docs/03-api/pydantic-models.md (Pydantic Models)
"""

from datetime import datetime
from pydantic import BaseModel, Field, field_validator, ConfigDict

from src.domain.models.enums import BusinessID, Priority, TaskStatus


class TaskBase(BaseModel):
    """Base task fields (shared between Create/Update/Response).
    
    Reference: docs/03-api/pydantic-models.md
    """
    
    model_config = ConfigDict(
        from_attributes=True,  # Support ORM mode (SQLAlchemy)
        validate_assignment=True,
        strict=True
    )
    
    title: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="What needs to be done",
        examples=["Починить фрезер для Иванова"]
    )
    
    description: str | None = Field(
        None,
        max_length=5000,
        description="Optional details"
    )
    
    business_id: int = Field(
        ...,
        ge=1,
        le=4,
        description="Business context (1-4) - MANDATORY (ADR-003)"
    )
    
    project_id: int | None = Field(
        None,
        description="Optional project grouping"
    )
    
    assigned_to: int | None = Field(
        None,
        description="Member ID assigned to task"
    )
    
    priority: int = Field(
        default=2,
        ge=1,
        le=4,
        description="Priority: 1=DO NOW, 2=SCHEDULE, 3=DELEGATE, 4=BACKLOG"
    )
    
    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        """Validate and clean title."""
        v = v.strip()
        if not v:
            raise ValueError("Title cannot be empty or whitespace")
        return v


class TaskCreate(TaskBase):
    """Create task request model.
    
    Used when creating new task from API or Telegram.
    """
    
    deadline: datetime | None = Field(
        None,
        description="Explicit deadline (ISO 8601)"
    )
    
    deadline_text: str | None = Field(
        None,
        max_length=100,
        description="Natural language deadline for AI parsing",
        examples=["завтра утром", "до конца недели"]
    )
    
    created_via: str = Field(
        default="api",
        pattern="^(voice|text|api)$",
        description="How task was created"
    )

    task_metadata: dict | None = Field(
        default=None,
        description="Metadata including transcript for voice tasks"
    )

    @field_validator("deadline", "deadline_text")
    @classmethod
    def validate_deadline_fields(cls, v, info):
        """Validate deadline fields.
        
        Can have deadline OR deadline_text, not both.
        """
        values = info.data
        if "deadline" in values and "deadline_text" in values:
            if values.get("deadline") and values.get("deadline_text"):
                raise ValueError("Provide either deadline or deadline_text, not both")
        return v


class TaskUpdate(BaseModel):
    """Update task request (all fields optional - partial update)."""
    
    model_config = ConfigDict(from_attributes=True)
    
    title: str | None = Field(None, min_length=1, max_length=500)
    description: str | None = None
    status: str | None = Field(None, pattern="^(open|done|archived)$")
    priority: int | None = Field(None, ge=1, le=4)
    deadline: datetime | None = None
    assigned_to: int | None = None


class Task(TaskBase):
    """Task response model - complete task data.
    
    This is the main aggregate root entity.
    
    Reference: docs/04-domain/entities.md (Task Entity section)
    """
    
    # Identity
    id: int = Field(..., description="Unique task ID")
    user_id: int = Field(..., description="Task owner (Константин)")
    
    # Status
    status: str = Field(
        default="open",
        pattern="^(open|done|archived)$"
    )
    
    # Time Tracking
    estimated_duration: int | None = Field(
        None,
        ge=1,
        le=480,
        description="AI-estimated duration in minutes"
    )
    
    actual_duration: int | None = Field(
        None,
        ge=1,
        le=480,
        description="Actual duration for learning (RAG feedback)"
    )
    
    # Dates
    deadline: datetime | None = None
    created_at: datetime = Field(..., description="When task was created")
    updated_at: datetime = Field(..., description="Last update time")
    completed_at: datetime | None = Field(None, description="When marked done")
    
    # AI/ML (not exposed in API, used internally)
    # embedding: list[float] | None = None  # Handled separately
    
    @property
    def estimation_accuracy(self) -> float | None:
        """Calculate estimation accuracy (0-1).
        
        Returns:
            Accuracy ratio (0-1) or None if not completed
            
        Example:
            estimated=120, actual=100 → accuracy=0.833 (83.3%)
        """
        if not self.estimated_duration or not self.actual_duration:
            return None
        
        error = abs(self.estimated_duration - self.actual_duration)
        accuracy = 1 - (error / self.actual_duration)
        return max(0.0, min(1.0, accuracy))  # Clamp to 0-1
    
    @property
    def is_overdue(self) -> bool:
        """Check if task is past deadline.
        
        Returns:
            True if deadline passed and task still open
        """
        if not self.deadline or self.status != TaskStatus.OPEN:
            return False
        return datetime.now() > self.deadline


class TaskDetailed(Task):
    """Task with related entities (joined data).
    
    Used for detailed API responses with business/project/member info.
    """
    
    business: "Business | None" = None
    project: "Project | None" = None
    assigned_member: "Member | None" = None


class TaskComplete(BaseModel):
    """Complete task request.
    
    Used when user marks task as done.
    Triggers learning feedback loop (ADR-004).
    """
    
    actual_duration: int = Field(
        ...,
        ge=1,
        le=480,
        description="How long it actually took (minutes)"
    )
    
    @field_validator("actual_duration")
    @classmethod
    def validate_duration(cls, v: int) -> int:
        """Validate duration is reasonable."""
        if v < 1:
            raise ValueError("Duration must be at least 1 minute")
        if v > 480:  # 8 hours
            raise ValueError("Duration cannot exceed 480 minutes (8 hours)")
        return v


# Forward references (will be defined in other files)
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.domain.models.business import Business
    from src.domain.models.project import Project
    from src.domain.models.member import Member

