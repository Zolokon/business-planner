# Pydantic Models - Business Planner

> **Type-safe data models with validation**  
> **Created**: 2025-10-17  
> **Framework**: Pydantic v2

---

## 🎯 Purpose

**Pydantic Models** = Type-safe data contracts with automatic validation

**Benefits**:
- ✅ Type safety (mypy compliance)
- ✅ Automatic validation
- ✅ JSON serialization/deserialization
- ✅ OpenAPI schema generation (for FastAPI)
- ✅ Clear API contracts

---

## 📋 Model Categories

```
src/domain/models/
├── base.py           # Base models
├── tasks.py          # Task models
├── projects.py       # Project models  
├── users.py          # User models
├── members.py        # Team member models
├── businesses.py     # Business models
├── analytics.py      # Analytics models
└── ai.py             # AI-specific models
```

---

## 1️⃣ Base Models

### BaseModel Configuration

```python
from pydantic import BaseModel, ConfigDict
from datetime import datetime

class AppBaseModel(BaseModel):
    """Base model for all domain models."""
    
    model_config = ConfigDict(
        # Pydantic v2 configuration
        strict=True,              # Strict type checking
        validate_assignment=True, # Validate on attribute set
        from_attributes=True,     # Support ORM mode (SQLAlchemy)
        json_encoders={
            datetime: lambda v: v.isoformat()
        }
    )
```

---

## 2️⃣ Task Models

### TaskBase (Shared Fields)

```python
from pydantic import Field, field_validator

class TaskBase(AppBaseModel):
    """Base task fields (shared between Create/Update/Response)."""
    
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
        description="Business context: 1=Inventum, 2=Lab, 3=R&D, 4=Trade"
    )
    
    project_id: int | None = Field(
        None,
        description="Optional project grouping"
    )
    
    assigned_to: int | None = Field(
        None,
        description="Member ID to assign task to"
    )
    
    priority: int = Field(
        default=2,
        ge=1,
        le=4,
        description="Priority: 1=DO NOW, 2=SCHEDULE, 3=DELEGATE, 4=BACKLOG"
    )
```

### TaskCreate (Input)

```python
class TaskCreate(TaskBase):
    """Create task request."""
    
    deadline: datetime | None = Field(
        None,
        description="Explicit deadline (ISO 8601)"
    )
    
    deadline_text: str | None = Field(
        None,
        max_length=100,
        description="Natural language deadline for AI parsing",
        examples=["завтра утром", "до конца недели", "послезавтра"]
    )
    
    created_via: str = Field(
        default="api",
        pattern="^(voice|text|api)$",
        description="How task was created"
    )
    
    @field_validator('title')
    @classmethod
    def validate_title(cls, v: str) -> str:
        """Validate title."""
        v = v.strip()
        if not v:
            raise ValueError("Title cannot be empty")
        return v
    
    @field_validator('deadline', 'deadline_text')
    @classmethod
    def validate_deadline_fields(cls, v, info):
        """Ensure at least one deadline field if provided."""
        # Can have deadline OR deadline_text, not both
        values = info.data
        if 'deadline' in values and 'deadline_text' in values:
            if values['deadline'] and values['deadline_text']:
                raise ValueError("Provide either deadline or deadline_text, not both")
        return v
```

### TaskUpdate (Partial Update)

```python
class TaskUpdate(AppBaseModel):
    """Update task request (all fields optional)."""
    
    title: str | None = Field(None, min_length=1, max_length=500)
    description: str | None = None
    status: str | None = Field(None, pattern="^(open|done|archived)$")
    priority: int | None = Field(None, ge=1, le=4)
    deadline: datetime | None = None
    assigned_to: int | None = None
    
    @field_validator('status')
    @classmethod
    def validate_status_transition(cls, v, info):
        """Validate status transition is allowed."""
        # Validation happens in service layer (needs current state)
        return v
```

### Task (Response)

```python
class Task(TaskBase):
    """Task response model."""
    
    id: int = Field(..., description="Unique task ID")
    user_id: int
    
    status: str = Field(
        default="open",
        pattern="^(open|done|archived)$"
    )
    
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
        description="Actual duration for learning"
    )
    
    deadline: datetime | None = None
    created_at: datetime
    updated_at: datetime
    completed_at: datetime | None = None
    
    @property
    def estimation_accuracy(self) -> float | None:
        """Calculate estimation accuracy."""
        if not self.estimated_duration or not self.actual_duration:
            return None
        
        error = abs(self.estimated_duration - self.actual_duration)
        accuracy = 1 - (error / self.actual_duration)
        return max(0.0, min(1.0, accuracy))


class TaskDetailed(Task):
    """Task with related entities."""
    
    business: "Business"
    project: "Project | None" = None
    assigned_member: "Member | None" = None
```

### TaskComplete (Action)

```python
class TaskComplete(AppBaseModel):
    """Complete task request."""
    
    actual_duration: int = Field(
        ...,
        ge=1,
        le=480,
        description="How long it actually took (minutes)"
    )
```

---

## 3️⃣ Project Models

### ProjectCreate

```python
class ProjectCreate(AppBaseModel):
    """Create project request."""
    
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
```

### Project

```python
class Project(AppBaseModel):
    """Project response model."""
    
    id: int
    user_id: int
    business_id: int
    name: str
    description: str | None
    status: str = Field(pattern="^(active|on_hold|completed)$")
    deadline: datetime | None
    created_at: datetime
    completed_at: datetime | None


class ProjectDetailed(Project):
    """Project with tasks."""
    
    tasks: list[Task] = []
    task_count: int
    completed_task_count: int
```

---

## 4️⃣ Business Models

```python
class Business(AppBaseModel):
    """Business context model (4 fixed businesses)."""
    
    id: int = Field(..., ge=1, le=4)
    name: str = Field(..., pattern="^(inventum|lab|r&d|trade)$")
    display_name: str
    description: str | None
    keywords: list[str] = []
    color: str | None = Field(None, pattern="^#[0-9A-Fa-f]{6}$")
    is_active: bool = True
```

---

## 5️⃣ Member Models

```python
class Member(AppBaseModel):
    """Team member model."""
    
    id: int
    name: str = Field(..., min_length=1, max_length=100)
    role: str
    business_ids: list[int] = Field(
        ...,
        description="Businesses this member works in"
    )
    skills: list[str] = []
    is_cross_functional: bool = False
    notes: str | None = None
    
    @field_validator('business_ids')
    @classmethod
    def validate_business_ids(cls, v: list[int]) -> list[int]:
        """Validate all business IDs are valid."""
        if not v:
            raise ValueError("Member must work in at least one business")
        
        for bid in v:
            if bid not in [1, 2, 3, 4]:
                raise ValueError(f"Invalid business_id: {bid}")
        
        return v
    
    def works_in_business(self, business_id: int) -> bool:
        """Check if member works in specific business."""
        return business_id in self.business_ids
```

---

## 6️⃣ User Models

```python
class User(AppBaseModel):
    """User model."""
    
    id: int
    telegram_id: int = Field(..., description="Telegram user ID")
    name: str
    username: str | None = None
    timezone: str = Field(default="Asia/Almaty")
    preferences: dict = Field(default_factory=dict)
    created_at: datetime
    last_active: datetime
```

---

## 7️⃣ Analytics Models

### TodayTasks

```python
class TodayTaskGroup(AppBaseModel):
    """Tasks grouped for today view."""
    
    business_name: str
    urgent: list[Task] = []
    scheduled: list[Task] = []
    total_time_minutes: int


class TodayTasks(AppBaseModel):
    """Today's tasks response."""
    
    date: datetime
    by_business: dict[str, TodayTaskGroup]
    total_tasks: int
    total_time_minutes: int
```

### WeeklyReport

```python
class BusinessWeeklySummary(AppBaseModel):
    """Weekly summary for one business."""
    
    tasks_completed: int
    time_spent_minutes: int
    average_duration_minutes: float
    estimation_accuracy: float | None


class WeeklyReport(AppBaseModel):
    """Weekly analytics report (GPT-5 generated)."""
    
    week_start: datetime
    week_end: datetime
    
    summary: dict[str, BusinessWeeklySummary]
    total_tasks_completed: int
    total_time_spent_minutes: int
    
    insights: list[str] = Field(
        ...,
        description="AI-generated insights (GPT-5)",
        examples=[
            "Наибольшая продуктивность во вторник",
            "R&D задачи занимают на 20% больше времени"
        ]
    )
    
    recommendations: list[str] = Field(
        ...,
        description="Strategic recommendations (GPT-5)",
        examples=[
            "Рассмотреть делегирование задач Inventum",
            "Запланировать больше времени на R&D"
        ]
    )
    
    estimation_accuracy: dict[str, float] = Field(
        ...,
        description="Accuracy by business (0-1, target: 0.8)"
    )
```

---

## 8️⃣ AI-Specific Models

### ParsedTask (GPT-5 Nano Output)

```python
class ParsedTask(AppBaseModel):
    """Task parsed from voice/text by GPT-5 Nano."""
    
    title: str = Field(..., min_length=1, max_length=500)
    business_id: int = Field(..., ge=1, le=4)
    deadline_text: str | None = None
    project_name: str | None = None
    assigned_to_name: str | None = None
    priority: int = Field(default=2, ge=1, le=4)
    description: str | None = None
    
    @classmethod
    def from_gpt_json(cls, gpt_response: dict) -> "ParsedTask":
        """Parse from GPT-5 Nano JSON response."""
        return cls(
            title=gpt_response["title"],
            business_id=gpt_response["business_id"],
            deadline_text=gpt_response.get("deadline"),
            project_name=gpt_response.get("project"),
            assigned_to_name=gpt_response.get("assigned_to"),
            priority=gpt_response.get("priority", 2),
            description=gpt_response.get("description")
        )


class TimeEstimateAI(AppBaseModel):
    """Time estimate from RAG + GPT-5 Nano."""
    
    estimated_minutes: int = Field(..., ge=1, le=480)
    confidence: str = Field(..., pattern="^(high|medium|low)$")
    similar_tasks_count: int = Field(..., ge=0)
    reasoning: str | None = Field(
        None,
        description="Why this estimate (for transparency)"
    )
```

### VoiceProcessingResult

```python
class VoiceProcessingResult(AppBaseModel):
    """Complete voice processing result."""
    
    transcript: str = Field(..., description="Whisper transcription")
    transcript_confidence: float = Field(..., ge=0, le=1)
    
    parsed_task: ParsedTask
    time_estimate: TimeEstimateAI
    
    processing_time_ms: int = Field(..., description="Total processing time")
    
    task_id: int | None = Field(
        None,
        description="Created task ID (if successful)"
    )
```

---

## 9️⃣ Response Models

### Success Response

```python
class SuccessResponse(AppBaseModel):
    """Generic success response."""
    
    success: bool = True
    message: str
    data: dict | None = None


class TaskCreatedResponse(AppBaseModel):
    """Task creation success response."""
    
    task: Task
    message: str = Field(
        default="Задача создана",
        description="Confirmation message"
    )
    telegram_message: str = Field(
        ...,
        description="Formatted message for Telegram"
    )
```

### Error Response

```python
class ErrorResponse(AppBaseModel):
    """Generic error response."""
    
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Human-readable message")
    details: dict | None = Field(None, description="Additional error details")
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": "ValidationError",
                "message": "business_id is required",
                "details": {
                    "field": "business_id",
                    "constraint": "required"
                }
            }
        }


class ValidationErrorResponse(AppBaseModel):
    """Validation error response."""
    
    error: str = "ValidationError"
    message: str
    validation_errors: list[dict] = Field(
        ...,
        description="List of validation errors"
    )
```

---

## 🔟 Request/Response Examples

### POST /tasks

**Request**:
```json
{
  "title": "Позвонить поставщику фрез",
  "business_id": 4,
  "deadline_text": "завтра утром",
  "created_via": "voice"
}
```

**Response 201**:
```json
{
  "id": 124,
  "user_id": 1,
  "business_id": 4,
  "project_id": null,
  "assigned_to": 7,
  "title": "Позвонить поставщику фрез",
  "description": null,
  "status": "open",
  "priority": 2,
  "estimated_duration": 45,
  "actual_duration": null,
  "deadline": "2025-10-18T09:00:00+05:00",
  "created_at": "2025-10-17T15:30:00+05:00",
  "updated_at": "2025-10-17T15:30:00+05:00",
  "completed_at": null
}
```

### POST /tasks/{id}/complete

**Request**:
```json
{
  "actual_duration": 50
}
```

**Response 200**:
```json
{
  "id": 124,
  "status": "done",
  "actual_duration": 50,
  "completed_at": "2025-10-18T10:50:00+05:00",
  ...
}
```

### GET /analytics/weekly

**Response 200**:
```json
{
  "week_start": "2025-10-14",
  "week_end": "2025-10-20",
  "summary": {
    "inventum": {
      "tasks_completed": 12,
      "time_spent_minutes": 1080,
      "average_duration_minutes": 90,
      "estimation_accuracy": 0.82
    },
    "lab": { ... },
    "r&d": { ... },
    "trade": { ... }
  },
  "total_tasks_completed": 28,
  "total_time_spent_minutes": 2520,
  "insights": [
    "Наибольшая продуктивность во вторник (8 задач)",
    "R&D задачи занимают на 15% больше времени чем оценивалось",
    "Точность оценок улучшилась с 68% до 78% за неделю"
  ],
  "recommendations": [
    "Планировать сложные R&D задачи на вторник",
    "Закладывать +20% времени для R&D задач",
    "Отличная динамика! Продолжайте фиксировать фактическое время"
  ],
  "estimation_accuracy": {
    "inventum": 0.85,
    "lab": 0.78,
    "r&d": 0.65,
    "trade": 0.82,
    "overall": 0.78
  }
}
```

---

## 🎯 Validation Examples

### Business ID Validation

```python
# ✅ Valid
task = TaskCreate(
    title="Test",
    business_id=1  # OK: 1-4
)

# ❌ Invalid
task = TaskCreate(
    title="Test",
    business_id=99  # Error: must be 1-4
)
# Raises: ValidationError
```

### Duration Validation

```python
# ✅ Valid
complete = TaskComplete(actual_duration=120)  # 2 hours

# ❌ Invalid
complete = TaskComplete(actual_duration=0)     # Too short
complete = TaskComplete(actual_duration=500)   # Too long (>8h)
# Raises: ValidationError
```

### Title Validation

```python
# ✅ Valid
task = TaskCreate(title="Починить фрезер", business_id=1)

# ❌ Invalid
task = TaskCreate(title="", business_id=1)    # Empty
task = TaskCreate(title="  ", business_id=1)  # Whitespace only
# Raises: ValidationError
```

---

## 🔄 Model Conversion

### From ORM to Pydantic

```python
# SQLAlchemy model → Pydantic model
from sqlalchemy import select

async def get_task(task_id: int) -> Task:
    """Get task from database."""
    
    result = await session.execute(
        select(TaskORM).where(TaskORM.id == task_id)
    )
    task_orm = result.scalar_one()
    
    # Automatic conversion (from_attributes=True)
    return Task.model_validate(task_orm)
```

### From Pydantic to ORM

```python
# Pydantic model → SQLAlchemy model
def create_task(task_data: TaskCreate) -> TaskORM:
    """Create ORM instance from Pydantic."""
    
    task_orm = TaskORM(
        **task_data.model_dump(exclude_unset=True)
    )
    
    return task_orm
```

---

## 📝 FastAPI Integration

### Automatic Validation

```python
from fastapi import FastAPI, HTTPException

app = FastAPI()

@app.post("/tasks", response_model=Task, status_code=201)
async def create_task(
    task_data: TaskCreate,  # ← Automatic validation!
    user_id: int = Depends(get_current_user)
) -> Task:
    """Create task endpoint.
    
    Pydantic automatically:
    - Validates input
    - Returns 422 if invalid
    - Generates OpenAPI schema
    """
    
    # If we're here, task_data is valid ✅
    task = await task_service.create(task_data, user_id)
    
    return task  # ← Automatic serialization!
```

### Error Handling

```python
from fastapi import HTTPException, status

@app.post("/tasks")
async def create_task(task_data: TaskCreate):
    try:
        task = await task_service.create(task_data)
        return task
    
    except ValueError as e:
        # Business logic error
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=ErrorResponse(
                error="BusinessRuleViolation",
                message=str(e)
            ).model_dump()
        )
```

---

## 🧪 Testing Models

```python
import pytest
from pydantic import ValidationError

def test_task_create_valid():
    """Test valid task creation."""
    task = TaskCreate(
        title="Test task",
        business_id=1
    )
    assert task.title == "Test task"
    assert task.business_id == 1
    assert task.priority == 2  # Default


def test_task_create_invalid_business():
    """Test invalid business_id."""
    with pytest.raises(ValidationError) as exc_info:
        TaskCreate(
            title="Test",
            business_id=99  # Invalid!
        )
    
    errors = exc_info.value.errors()
    assert any(
        e['loc'] == ('business_id',) and 'less than or equal to 4' in e['msg']
        for e in errors
    )


def test_duration_validation():
    """Test duration constraints."""
    # Valid
    task = Task(actual_duration=120)  # OK
    
    # Invalid: too short
    with pytest.raises(ValidationError):
        Task(actual_duration=0)
    
    # Invalid: too long
    with pytest.raises(ValidationError):
        Task(actual_duration=500)


def test_model_serialization():
    """Test JSON serialization."""
    task = Task(
        id=1,
        user_id=1,
        business_id=1,
        title="Test",
        created_at=datetime.now()
    )
    
    # To JSON
    json_str = task.model_dump_json()
    
    # From JSON
    task_restored = Task.model_validate_json(json_str)
    
    assert task_restored.id == task.id
```

---

## 📖 References

- Pydantic V2 Docs: https://docs.pydantic.dev/latest/
- FastAPI: https://fastapi.tiangolo.com/
- OpenAPI: `docs/03-api/openapi.yaml`
- Domain Entities: `docs/04-domain/entities.md`

---

**Status**: ✅ Pydantic Models Specification Complete  
**Total Models**: ~15 models (Create, Update, Response variants)  
**Validation**: Comprehensive with field validators  
**Next**: LangGraph State Machines

