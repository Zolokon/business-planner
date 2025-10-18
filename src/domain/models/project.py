"""
Project Domain Models - Business Planner.

Projects are user-created task groupings (NOT auto-created).

Reference: docs/04-domain/entities.md (Project Entity)
"""

from datetime import datetime
from pydantic import BaseModel, Field, field_validator, ConfigDict

from src.domain.models.enums import ProjectStatus


class ProjectCreate(BaseModel):
    """Create project request."""
    
    model_config = ConfigDict(from_attributes=True)
    
    name: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Project name",
        examples=["Ремонт фрезера Иванова", "Декабрьская поставка"]
    )
    
    description: str | None = Field(None, max_length=2000)
    
    business_id: int = Field(
        ...,
        ge=1,
        le=4,
        description="Which business this project belongs to"
    )
    
    deadline: datetime | None = None


class Project(BaseModel):
    """Project entity - task grouping.
    
    Projects are explicitly created by user (not auto-generated).
    Belong to one business context.
    
    Reference: docs/04-domain/entities.md
    """
    
    model_config = ConfigDict(from_attributes=True)
    
    # Identity
    id: int
    user_id: int
    business_id: int = Field(..., ge=1, le=4)
    
    # Content
    name: str = Field(..., min_length=1, max_length=200)
    description: str | None = None
    
    # Status
    status: str = Field(
        default="active",
        pattern="^(active|on_hold|completed)$"
    )
    
    # Dates
    deadline: datetime | None = None
    created_at: datetime
    completed_at: datetime | None = None


class ProjectDetailed(Project):
    """Project with tasks and statistics."""
    
    tasks: list["Task"] = Field(default_factory=list)
    task_count: int = 0
    completed_task_count: int = 0


# Forward reference
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.domain.models.task import Task

