"""Domain Models - Pydantic models for Business Planner.

All models are type-safe with validation.

Reference: docs/03-api/pydantic-models.md
"""

from src.domain.models.enums import (
    BusinessID,
    Priority,
    TaskStatus,
    ProjectStatus,
    HistoryAction,
    Confidence
)

from src.domain.models.task import (
    Task,
    TaskCreate,
    TaskUpdate,
    TaskDetailed,
    TaskComplete
)

from src.domain.models.project import (
    Project,
    ProjectCreate,
    ProjectDetailed
)

from src.domain.models.member import Member
from src.domain.models.business import Business
from src.domain.models.user import User


__all__ = [
    # Enums
    "BusinessID",
    "Priority",
    "TaskStatus",
    "ProjectStatus",
    "HistoryAction",
    "Confidence",
    
    # Task models
    "Task",
    "TaskCreate",
    "TaskUpdate",
    "TaskDetailed",
    "TaskComplete",
    
    # Project models
    "Project",
    "ProjectCreate",
    "ProjectDetailed",
    
    # Other models
    "Member",
    "Business",
    "User",
]

