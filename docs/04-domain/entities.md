# Domain Entities - Business Planner

> **Core domain objects with identity**  
> **Created**: 2025-10-17  
> **Pattern**: Domain-Driven Design (DDD)

---

## 🎯 What is an Entity?

**Entity** = Object with unique identity that persists over time

**Key Characteristics**:
- Has unique ID
- Identity is important (not just attributes)
- Mutable (can change over time)
- Has lifecycle

---

## 📋 Core Entities

### Entity Hierarchy

```
Root Aggregates (have repositories):
├── User (Константин and team)
├── Business (4 contexts)
├── Member (8 people)
├── Project (user-created groupings)
└── Task ⭐ (main aggregate root)

Child Entities:
└── TaskHistory (part of Task aggregate)
```

---

## 1️⃣ Task Entity ⭐ (Main Aggregate Root)

### Definition
```python
from pydantic import BaseModel, Field, validator
from datetime import datetime

class Task(BaseModel):
    """Task entity - main aggregate root.
    
    A task is a unit of work in one of 4 business contexts.
    Tasks have unique identity, lifecycle, and business rules.
    """
    
    # Identity
    id: int = Field(..., description="Unique task identifier")
    
    # Ownership
    user_id: int = Field(..., description="Creator (Константин)")
    business_id: int = Field(..., description="Business context (1-4) - MANDATORY")
    project_id: int | None = Field(None, description="Optional project grouping")
    assigned_to: int | None = Field(None, description="Team member assigned")
    
    # Content
    title: str = Field(..., min_length=1, max_length=500, description="What to do")
    description: str | None = Field(None, max_length=5000, description="Optional details")
    
    # Status & Priority
    status: TaskStatus = Field(default=TaskStatus.OPEN, description="Current status")
    priority: Priority = Field(default=Priority.SCHEDULE, description="Eisenhower priority 1-4")
    
    # Time Tracking
    estimated_duration: int | None = Field(None, ge=1, le=480, description="AI estimate (minutes)")
    actual_duration: int | None = Field(None, ge=1, le=480, description="Actual time (learning)")
    
    # Dates
    deadline: datetime | None = Field(None, description="When task should be done")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    completed_at: datetime | None = Field(None, description="When marked done")
    
    # AI/ML
    embedding: list[float] | None = Field(None, description="Vector(1536) for RAG")
    
    # Metadata
    metadata: dict = Field(default_factory=dict, description="Flexible JSON data")
    
    class Config:
        orm_mode = True
    
    # Validators
    @validator('business_id')
    def validate_business_context(cls, v):
        """Business ID must be 1-4 (ADR-003)."""
        if v not in [1, 2, 3, 4]:
            raise ValueError(f"Invalid business_id: {v}. Must be 1-4")
        return v
    
    @validator('deadline')
    def validate_deadline_future(cls, v, values):
        """Deadline must be in future (if set)."""
        if v and v < values.get('created_at', datetime.now()):
            raise ValueError("Deadline cannot be in the past")
        return v
    
    # Business logic methods
    def complete(self, actual_duration: int) -> None:
        """Mark task as complete with actual duration."""
        if self.status == TaskStatus.DONE:
            raise ValueError("Task already completed")
        
        self.status = TaskStatus.DONE
        self.actual_duration = actual_duration
        self.completed_at = datetime.now()
    
    def archive(self) -> None:
        """Archive completed task."""
        if self.status != TaskStatus.DONE:
            raise ValueError("Can only archive completed tasks")
        
        self.status = TaskStatus.ARCHIVED
    
    def assign_to_member(self, member_id: int) -> None:
        """Assign task to team member."""
        # Business rule: Member must work in this business
        # Validation happens in service layer
        self.assigned_to = member_id
    
    def update_estimate(self, duration: int) -> None:
        """Update time estimate (from RAG)."""
        if duration < 1 or duration > 480:
            raise ValueError("Duration must be 1-480 minutes")
        
        self.estimated_duration = duration
    
    @property
    def is_overdue(self) -> bool:
        """Check if task is past deadline."""
        if not self.deadline or self.status != TaskStatus.OPEN:
            return False
        return datetime.now() > self.deadline
    
    @property
    def estimation_accuracy(self) -> float | None:
        """Calculate how accurate estimate was (0-1)."""
        if not self.estimated_duration or not self.actual_duration:
            return None
        
        error = abs(self.estimated_duration - self.actual_duration)
        accuracy = 1 - (error / self.actual_duration)
        return max(0, min(1, accuracy))  # Clamp to 0-1
```

### Task Invariants
- Task MUST have business_id (ADR-003)
- Task MUST have user_id
- Task MUST have title
- Status can only transition: open → done → archived
- Actual duration only set when status = done
- Embedding generated async after creation

---

## 2️⃣ Project Entity (Aggregate Root)

### Definition
```python
class Project(BaseModel):
    """Project entity - groups related tasks.
    
    Projects are user-created containers for organizing tasks.
    NOT auto-created - user explicitly creates them.
    """
    
    # Identity
    id: int
    
    # Ownership
    user_id: int = Field(..., description="Project owner")
    business_id: int = Field(..., description="Business context (1-4)")
    
    # Content
    name: str = Field(..., min_length=1, max_length=200, description="Project name")
    description: str | None = Field(None, max_length=2000)
    
    # Status
    status: ProjectStatus = Field(default=ProjectStatus.ACTIVE)
    
    # Dates
    deadline: datetime | None = None
    created_at: datetime = Field(default_factory=datetime.now)
    completed_at: datetime | None = None
    
    @validator('business_id')
    def validate_business(cls, v):
        if v not in [1, 2, 3, 4]:
            raise ValueError(f"Invalid business_id: {v}")
        return v
    
    def complete(self) -> None:
        """Mark project as completed."""
        if self.status == ProjectStatus.COMPLETED:
            raise ValueError("Project already completed")
        
        self.status = ProjectStatus.COMPLETED
        self.completed_at = datetime.now()
    
    def pause(self) -> None:
        """Put project on hold."""
        if self.status != ProjectStatus.ACTIVE:
            raise ValueError("Can only pause active projects")
        
        self.status = ProjectStatus.ON_HOLD
    
    def resume(self) -> None:
        """Resume paused project."""
        if self.status != ProjectStatus.ON_HOLD:
            raise ValueError("Can only resume on-hold projects")
        
        self.status = ProjectStatus.ACTIVE
```

### Project Invariants
- Project MUST belong to one business
- Project name unique per (user_id, business_id)
- Cannot delete project with active tasks
- Status transitions: active ↔ on_hold → completed

---

## 3️⃣ Member Entity (Aggregate Root)

### Definition
```python
class Member(BaseModel):
    """Team member entity.
    
    Represents people working in one or more businesses.
    Can be cross-functional (work in multiple contexts).
    """
    
    # Identity
    id: int
    
    # Profile
    name: str = Field(..., min_length=1, max_length=100)
    role: str = Field(..., description="Директор, Мастер, CAD/CAM, etc.")
    
    # Business associations
    business_ids: list[int] = Field(..., description="Businesses this member works in")
    
    # Skills
    skills: list[str] = Field(default_factory=list, description="For task assignment")
    
    # Flags
    is_cross_functional: bool = Field(default=False, description="Works in 2+ businesses")
    
    # Notes
    notes: str | None = None
    
    created_at: datetime = Field(default_factory=datetime.now)
    
    @validator('business_ids')
    def validate_businesses(cls, v):
        """Validate business IDs."""
        if not v:
            raise ValueError("Member must work in at least one business")
        
        for bid in v:
            if bid not in [1, 2, 3, 4]:
                raise ValueError(f"Invalid business_id: {bid}")
        
        return v
    
    @property
    def business_count(self) -> int:
        """Number of businesses member works in."""
        return len(self.business_ids)
    
    def works_in_business(self, business_id: int) -> bool:
        """Check if member works in specific business."""
        return business_id in self.business_ids
    
    def can_be_assigned_task(self, task: Task) -> bool:
        """Check if member can be assigned this task."""
        return task.business_id in self.business_ids
```

### Member Invariants
- Must work in at least 1 business
- is_cross_functional = True if len(business_ids) > 1
- Cannot assign task if member doesn't work in that business

---

## 4️⃣ User Entity (Aggregate Root)

### Definition
```python
class User(BaseModel):
    """User entity - Telegram users of the system.
    
    Currently: Single user (Константин)
    Future: Can add more users (team members with accounts)
    """
    
    # Identity
    id: int
    telegram_id: int = Field(..., description="Telegram user ID (unique)")
    
    # Profile
    name: str = Field(..., min_length=1, max_length=100)
    username: str | None = Field(None, description="Telegram username")
    
    # Settings
    timezone: str = Field(default="Asia/Almaty", description="User timezone (UTC+5)")
    preferences: dict = Field(default_factory=dict, description="User preferences")
    
    # Activity
    created_at: datetime = Field(default_factory=datetime.now)
    last_active: datetime = Field(default_factory=datetime.now)
    
    def update_activity(self) -> None:
        """Update last active timestamp."""
        self.last_active = datetime.now()
    
    def set_preference(self, key: str, value: any) -> None:
        """Set user preference."""
        self.preferences[key] = value
    
    def get_preference(self, key: str, default: any = None) -> any:
        """Get user preference with default."""
        return self.preferences.get(key, default)
```

### User Invariants
- telegram_id must be unique
- timezone must be valid IANA timezone
- last_active updated on any interaction

---

## 5️⃣ Business Entity (Aggregate Root)

### Definition
```python
class Business(BaseModel):
    """Business entity - one of 4 fixed business contexts.
    
    Represents a bounded context (DDD).
    Fixed at 4, not user-created.
    """
    
    # Identity
    id: int = Field(..., ge=1, le=4, description="1-4 only")
    
    # Names
    name: str = Field(..., description="Internal: inventum, lab, r&d, trade")
    display_name: str = Field(..., description="Display: Inventum, Inventum Lab, etc.")
    
    # Description
    description: str | None = None
    
    # AI Detection
    keywords: list[str] = Field(default_factory=list, description="For AI context detection")
    
    # UI
    color: str | None = Field(None, description="Hex color for UI")
    
    # Status
    is_active: bool = Field(default=True)
    
    created_at: datetime = Field(default_factory=datetime.now)
    
    @validator('id')
    def validate_fixed_id(cls, v):
        """Business IDs are fixed 1-4."""
        if v not in [1, 2, 3, 4]:
            raise ValueError("Business ID must be 1, 2, 3, or 4")
        return v
    
    @validator('name')
    def validate_name(cls, v):
        """Business names are fixed."""
        valid_names = ['inventum', 'lab', 'r&d', 'trade']
        if v not in valid_names:
            raise ValueError(f"Business name must be one of: {valid_names}")
        return v
    
    def matches_keywords(self, text: str) -> int:
        """Count keyword matches in text (for AI detection)."""
        text_lower = text.lower()
        return sum(1 for keyword in self.keywords if keyword in text_lower)
```

### Business Invariants
- Only 4 businesses exist (fixed)
- IDs are 1, 2, 3, 4 (never change)
- Names are inventum, lab, r&d, trade (never change)
- Cannot delete business (referenced by tasks)

---

## 6️⃣ TaskHistory Entity (Part of Task Aggregate)

### Definition
```python
class TaskHistory(BaseModel):
    """Task history event - audit trail.
    
    Part of Task aggregate - not accessed directly.
    Tracks all changes to tasks for learning and analytics.
    """
    
    # Identity
    id: int
    
    # References
    task_id: int = Field(..., description="Parent task")
    user_id: int = Field(..., description="Who made the change")
    
    # Event
    action: HistoryAction = Field(..., description="What happened")
    changes: dict = Field(default_factory=dict, description="What changed (JSON)")
    duration: int | None = Field(None, description="Actual duration if completed")
    
    # Timestamp
    occurred_at: datetime = Field(default_factory=datetime.now)
    
    @property
    def is_completion(self) -> bool:
        """Check if this is a task completion event."""
        return self.action == HistoryAction.COMPLETED
```

---

## 🎯 Entity Lifecycle

### Task Lifecycle

```
NEW
 ├→ CREATE → [OPEN] ←─────────────┐
 │              │                  │
 │              │ complete()       │ reopen()
 │              ▼                  │
 │           [DONE] ────────────→  │
 │              │                  
 │              │ archive()        
 │              ▼                  
 └──────→  [ARCHIVED]              
```

**State Transitions**:
- NEW → OPEN (on creation)
- OPEN → DONE (on completion)
- DONE → ARCHIVED (on archive)
- DONE → OPEN (on reopen - rare)

**Forbidden**:
- ❌ OPEN → ARCHIVED (must complete first)
- ❌ ARCHIVED → OPEN (archived is final)

### Project Lifecycle

```
NEW
 └→ CREATE → [ACTIVE] ←───────┐
                │              │
                │ pause()      │ resume()
                ▼              │
            [ON_HOLD] ─────────┘
                │
                │ complete()
                ▼
            [COMPLETED]
```

---

## 📐 Entity Relationships

### Aggregate Boundaries

```
┌─────────────────────────────────────────┐
│  Task Aggregate (Root: Task)            │
│  ├── Task (root entity)                 │
│  └── TaskHistory (child entities)       │
│                                          │
│  Accessed via: TaskRepository           │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│  Project Aggregate (Root: Project)      │
│  └── Project (root entity)              │
│                                          │
│  Accessed via: ProjectRepository        │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│  Member Aggregate (Root: Member)        │
│  └── Member (root entity)               │
│                                          │
│  Accessed via: MemberRepository         │
└─────────────────────────────────────────┘
```

**Key Principle**: Only access aggregates through their root entity

---

## 🔍 Entity vs Value Object

### Entities (Have Identity)
- ✅ **Task** - Identity matters (task #123 ≠ task #124 even if identical)
- ✅ **Project** - Each project is unique
- ✅ **Member** - Each person is unique
- ✅ **User** - Each user is unique

### Value Objects (No Identity)
- ✅ **Priority** - Priority 1 is same everywhere
- ✅ **Deadline** - datetime value
- ✅ **Duration** - minutes value
- ✅ **BusinessContext** - enum value

**Rule**: If two things with same attributes are **interchangeable** → Value Object  
If they need to be **distinguished** → Entity

---

## 💾 Persistence (Repository Pattern)

### Task Repository Interface
```python
from typing import Protocol

class TaskRepository(Protocol):
    """Repository for Task aggregate."""
    
    async def create(self, task: Task) -> Task:
        """Create new task."""
        ...
    
    async def get_by_id(self, task_id: int) -> Task | None:
        """Get task by ID."""
        ...
    
    async def find_by_business(
        self, 
        user_id: int, 
        business_id: int
    ) -> list[Task]:
        """Find tasks in specific business context."""
        ...
    
    async def find_similar(
        self,
        embedding: list[float],
        business_id: int,  # MANDATORY (ADR-003)
        limit: int = 5
    ) -> list[Task]:
        """Find similar tasks using RAG (within same business)."""
        ...
    
    async def update(self, task: Task) -> Task:
        """Update existing task."""
        ...
    
    async def delete(self, task_id: int) -> None:
        """Delete task (soft delete to ARCHIVED)."""
        ...
```

**Implementation**: `src/infrastructure/database/repositories/task_repository.py`

---

## 🎯 Entity Invariants Summary

### Task
- ✅ Must have business_id (1-4)
- ✅ Must have user_id
- ✅ Must have title
- ✅ Status only: open, done, archived
- ✅ Priority only: 1-4
- ✅ Duration: 1-480 minutes (if set)
- ✅ Deadline must be future (if set)

### Project
- ✅ Must have business_id (1-4)
- ✅ Must have user_id
- ✅ Must have name
- ✅ Status only: active, on_hold, completed
- ✅ Cannot delete with active tasks

### Member
- ✅ Must have at least 1 business_id
- ✅ All business_ids must be valid (1-4)
- ✅ is_cross_functional = (len(business_ids) > 1)
- ✅ Name must be unique

### User
- ✅ telegram_id must be unique
- ✅ Must have name
- ✅ Timezone must be valid

### Business
- ✅ Only 4 businesses exist (fixed)
- ✅ IDs are 1-4 (immutable)
- ✅ Names are fixed (immutable)
- ✅ Cannot be deleted

---

## 🧪 Testing Entities

### Unit Tests
```python
def test_task_creation():
    """Test task entity creation."""
    task = Task(
        id=1,
        user_id=1,
        business_id=1,
        title="Починить фрезер"
    )
    
    assert task.status == TaskStatus.OPEN
    assert task.priority == Priority.SCHEDULE
    assert task.business_id == 1


def test_task_completion():
    """Test task completion logic."""
    task = Task(id=1, user_id=1, business_id=1, title="Test")
    
    # Complete task
    task.complete(actual_duration=60)
    
    assert task.status == TaskStatus.DONE
    assert task.actual_duration == 60
    assert task.completed_at is not None


def test_task_invalid_business():
    """Test business validation."""
    with pytest.raises(ValueError, match="Invalid business_id"):
        Task(
            id=1,
            user_id=1,
            business_id=99,  # Invalid!
            title="Test"
        )


def test_member_cross_functional():
    """Test cross-functional member."""
    # Максим works in Inventum and R&D
    maxim = Member(
        id=1,
        name="Максим",
        role="Директор",
        business_ids=[1, 3],  # Inventum + R&D
        skills=["management", "diagnostics"]
    )
    
    assert maxim.is_cross_functional == False  # Set manually
    assert maxim.business_count == 2
    assert maxim.works_in_business(1) == True
    assert maxim.works_in_business(2) == False
    assert maxim.can_be_assigned_task(Task(business_id=1)) == True
```

---

## 📖 References

- Eric Evans - Domain-Driven Design (Entities chapter)
- Martin Fowler - Patterns of Enterprise Application Architecture
- ADR-003: Business Context Isolation
- Database: `docs/02-database/schema.sql`
- Bounded Contexts: `docs/04-domain/bounded-contexts.md`

---

**Status**: ✅ Entities Defined  
**Total Entities**: 6 (Task, Project, Member, User, Business, TaskHistory)  
**Aggregate Roots**: 5 (Task, Project, Member, User, Business)  
**Next**: Define Value Objects

