# Value Objects - Business Planner

> **Immutable objects defined by attributes, not identity**  
> **Created**: 2025-10-17  
> **Pattern**: Domain-Driven Design (DDD)

---

## 🎯 What is a Value Object?

**Value Object** = Object without identity, defined only by its attributes

**Characteristics**:
- **Immutable** - Cannot change after creation
- **No identity** - Two value objects with same attributes are equal
- **Self-validating** - Validates on construction
- **Side-effect free methods** - Operations return new values

**Example**: 
- Priority(1) == Priority(1) ✅ (same value)
- Task(id=1) != Task(id=2) ❌ (different identity, even if same title)

---

## 📋 Value Objects in Business Planner

### Core Value Objects

1. **Priority** - Eisenhower matrix priority (1-4)
2. **TaskStatus** - Task state (open, done, archived)
3. **ProjectStatus** - Project state (active, on_hold, completed)
4. **Duration** - Time duration in minutes
5. **Deadline** - Parsed deadline with timezone
6. **BusinessContext** - One of 4 business contexts
7. **TimeEstimate** - AI estimate with confidence

---

## 1️⃣ Priority (Eisenhower Matrix)

### Definition
```python
from enum import IntEnum

class Priority(IntEnum):
    """Task priority based on Eisenhower Matrix.
    
    Combines importance and urgency into 4 levels:
    - 1: DO NOW (Important + Urgent)
    - 2: SCHEDULE (Important + Not Urgent)
    - 3: DELEGATE (Not Important + Urgent)
    - 4: BACKLOG (Not Important + Not Urgent)
    """
    
    DO_NOW = 1      # 🔴 Important + Urgent
    SCHEDULE = 2    # 🟡 Important + Not Urgent (default)
    DELEGATE = 3    # 🟠 Not Important + Urgent
    BACKLOG = 4     # 🟢 Not Important + Not Urgent
    
    @property
    def display_name(self) -> str:
        """Human-readable name."""
        names = {
            Priority.DO_NOW: "Срочно",
            Priority.SCHEDULE: "Запланировать",
            Priority.DELEGATE: "Делегировать",
            Priority.BACKLOG: "Когда-нибудь"
        }
        return names[self]
    
    @property
    def emoji(self) -> str:
        """Emoji for Telegram display."""
        emojis = {
            Priority.DO_NOW: "🔴",
            Priority.SCHEDULE: "🟡",
            Priority.DELEGATE: "🟠",
            Priority.BACKLOG: "🟢"
        }
        return emojis[self]
    
    @property
    def description(self) -> str:
        """Description of priority level."""
        descriptions = {
            Priority.DO_NOW: "Важно и срочно - сделать сегодня",
            Priority.SCHEDULE: "Важно, но не срочно - запланировать",
            Priority.DELEGATE: "Не важно, но срочно - делегировать",
            Priority.BACKLOG: "Не важно и не срочно - потом"
        }
        return descriptions[self]
    
    @classmethod
    def from_importance_urgency(
        cls, 
        is_important: bool, 
        is_urgent: bool
    ) -> "Priority":
        """Calculate priority from importance and urgency."""
        if is_important and is_urgent:
            return cls.DO_NOW
        elif is_important and not is_urgent:
            return cls.SCHEDULE
        elif not is_important and is_urgent:
            return cls.DELEGATE
        else:
            return cls.BACKLOG


# Usage
priority = Priority.DO_NOW
print(f"{priority.emoji} {priority.display_name}")
# Output: "🔴 Срочно"
```

---

## 2️⃣ TaskStatus

### Definition
```python
from enum import Enum

class TaskStatus(str, Enum):
    """Task status - where in lifecycle."""
    
    OPEN = "open"          # 🔵 Active, not done
    DONE = "done"          # ✅ Completed
    ARCHIVED = "archived"  # 📦 Completed and archived
    
    @property
    def emoji(self) -> str:
        emojis = {
            TaskStatus.OPEN: "🔵",
            TaskStatus.DONE: "✅",
            TaskStatus.ARCHIVED: "📦"
        }
        return emojis[self]
    
    @property
    def is_active(self) -> bool:
        """Check if task needs action."""
        return self == TaskStatus.OPEN
    
    @property
    def is_completed(self) -> bool:
        """Check if task is done."""
        return self in [TaskStatus.DONE, TaskStatus.ARCHIVED]
    
    def can_transition_to(self, new_status: "TaskStatus") -> bool:
        """Check if transition is allowed."""
        allowed_transitions = {
            TaskStatus.OPEN: [TaskStatus.DONE],
            TaskStatus.DONE: [TaskStatus.ARCHIVED, TaskStatus.OPEN],
            TaskStatus.ARCHIVED: []  # Final state
        }
        return new_status in allowed_transitions.get(self, [])
```

---

## 3️⃣ Duration

### Definition
```python
from dataclasses import dataclass

@dataclass(frozen=True)  # Immutable
class Duration:
    """Time duration value object.
    
    Represents task duration in minutes with validation.
    Immutable - create new instance for different duration.
    """
    
    minutes: int
    
    def __post_init__(self):
        """Validate duration on creation."""
        if self.minutes < 1:
            raise ValueError("Duration must be at least 1 minute")
        if self.minutes > 480:  # 8 hours max
            raise ValueError("Duration cannot exceed 480 minutes (8 hours)")
    
    @classmethod
    def from_hours(cls, hours: float) -> "Duration":
        """Create from hours."""
        return cls(minutes=int(hours * 60))
    
    @property
    def hours(self) -> float:
        """Get duration in hours."""
        return self.minutes / 60
    
    @property
    def display(self) -> str:
        """Human-readable format."""
        if self.minutes < 60:
            return f"{self.minutes} мин"
        else:
            hours = self.minutes // 60
            mins = self.minutes % 60
            if mins == 0:
                return f"{hours} ч"
            else:
                return f"{hours} ч {mins} мин"
    
    def __str__(self) -> str:
        return self.display
    
    def __add__(self, other: "Duration") -> "Duration":
        """Add two durations."""
        return Duration(self.minutes + other.minutes)
    
    def __mul__(self, factor: float) -> "Duration":
        """Multiply duration."""
        return Duration(int(self.minutes * factor))


# Usage
duration = Duration(90)
print(duration.display)  # "1 ч 30 мин"
print(duration.hours)    # 1.5

long_task = Duration.from_hours(2.5)
print(long_task.minutes)  # 150
```

---

## 4️⃣ Deadline

### Definition
```python
from dataclasses import dataclass
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

@dataclass(frozen=True)
class Deadline:
    """Deadline value object with timezone awareness.
    
    Parses natural language deadlines and handles workday logic.
    Always in UTC+5 (Almaty, Kazakhstan).
    """
    
    dt: datetime  # Always timezone-aware
    
    def __post_init__(self):
        """Validate deadline."""
        # Ensure timezone-aware
        if self.dt.tzinfo is None:
            raise ValueError("Deadline must be timezone-aware")
    
    @classmethod
    def from_natural_language(
        cls,
        text: str,
        reference_time: datetime | None = None
    ) -> "Deadline":
        """Parse natural language deadline.
        
        Examples:
        - "завтра утром" → tomorrow 09:00
        - "послезавтра" → day after tomorrow 23:59
        - "на следующей неделе" → next Monday 09:00
        - "до конца недели" → Friday 18:00
        """
        if reference_time is None:
            reference_time = datetime.now(ZoneInfo("Asia/Almaty"))
        
        text_lower = text.lower()
        
        # Tomorrow
        if "завтра" in text_lower:
            base = reference_time + timedelta(days=1)
            hour = cls._parse_time_of_day(text_lower)
            deadline = base.replace(hour=hour, minute=0, second=0)
        
        # Day after tomorrow
        elif "послезавтра" in text_lower:
            base = reference_time + timedelta(days=2)
            hour = cls._parse_time_of_day(text_lower)
            deadline = base.replace(hour=hour, minute=0, second=0)
        
        # Next week
        elif "следующ" in text_lower and "недел" in text_lower:
            days_ahead = 7 - reference_time.weekday()  # Next Monday
            base = reference_time + timedelta(days=days_ahead)
            deadline = base.replace(hour=9, minute=0, second=0)
        
        # End of week
        elif "конец" in text_lower and "недел" in text_lower:
            days_to_friday = (4 - reference_time.weekday()) % 7
            base = reference_time + timedelta(days=days_to_friday)
            deadline = base.replace(hour=18, minute=0, second=0)
        
        # Default: +7 days
        else:
            deadline = reference_time + timedelta(days=7)
            deadline = deadline.replace(hour=23, minute=59, second=0)
        
        # Adjust for weekend (move to Monday)
        deadline = cls._adjust_for_workday(deadline)
        
        return cls(dt=deadline)
    
    @staticmethod
    def _parse_time_of_day(text: str) -> int:
        """Parse time from text."""
        if "утр" in text:
            return 9   # 09:00
        elif "дн" in text or "обед" in text:
            return 13  # 13:00
        elif "вечер" in text:
            return 18  # 18:00
        else:
            return 23  # 23:59 (end of day)
    
    @staticmethod
    def _adjust_for_workday(dt: datetime) -> datetime:
        """Move weekend deadlines to Monday."""
        # Saturday (5) → Monday
        if dt.weekday() == 5:
            dt = dt + timedelta(days=2)
        # Sunday (6) → Monday
        elif dt.weekday() == 6:
            dt = dt + timedelta(days=1)
        
        return dt.replace(hour=9, minute=0)
    
    @property
    def is_today(self) -> bool:
        """Check if deadline is today."""
        now = datetime.now(ZoneInfo("Asia/Almaty"))
        return self.dt.date() == now.date()
    
    @property
    def is_overdue(self) -> bool:
        """Check if deadline has passed."""
        now = datetime.now(ZoneInfo("Asia/Almaty"))
        return self.dt < now
    
    @property
    def hours_until(self) -> float:
        """Hours until deadline."""
        now = datetime.now(ZoneInfo("Asia/Almaty"))
        delta = self.dt - now
        return delta.total_seconds() / 3600
    
    def __str__(self) -> str:
        """Human-readable deadline."""
        return self.dt.strftime("%A %d.%m в %H:%M")


# Usage
deadline = Deadline.from_natural_language("завтра утром")
print(deadline)  # "Понедельник 21.10 в 09:00"
```

---

## 5️⃣ TimeEstimate

### Definition
```python
from dataclasses import dataclass
from enum import Enum

class Confidence(str, Enum):
    """Confidence in time estimate."""
    HIGH = "high"      # Based on 3+ similar tasks
    MEDIUM = "medium"  # Based on 1-2 similar tasks
    LOW = "low"        # No similar tasks (default)

@dataclass(frozen=True)
class TimeEstimate:
    """Time estimation value object with confidence.
    
    Represents AI-generated time estimate for a task.
    Includes confidence based on historical data availability.
    """
    
    duration: Duration
    confidence: Confidence
    similar_tasks_count: int
    reasoning: str | None = None
    
    def __post_init__(self):
        """Validate estimate."""
        if self.similar_tasks_count < 0:
            raise ValueError("similar_tasks_count cannot be negative")
    
    @classmethod
    def default(cls) -> "TimeEstimate":
        """Default estimate when no history."""
        return cls(
            duration=Duration(60),  # 1 hour default
            confidence=Confidence.LOW,
            similar_tasks_count=0,
            reasoning="No similar tasks found, using default"
        )
    
    @classmethod
    def from_similar_tasks(
        cls,
        similar_tasks: list,
        estimated_minutes: int
    ) -> "TimeEstimate":
        """Create estimate from RAG results."""
        count = len(similar_tasks)
        
        if count == 0:
            return cls.default()
        elif count >= 3:
            confidence = Confidence.HIGH
        else:
            confidence = Confidence.MEDIUM
        
        durations = [t.actual_duration for t in similar_tasks]
        avg_duration = sum(durations) / len(durations)
        
        return cls(
            duration=Duration(estimated_minutes),
            confidence=confidence,
            similar_tasks_count=count,
            reasoning=f"Based on {count} similar tasks (avg: {avg_duration:.0f} min)"
        )
    
    @property
    def display(self) -> str:
        """Display for Telegram."""
        confidence_emoji = {
            Confidence.HIGH: "🎯",
            Confidence.MEDIUM: "📊",
            Confidence.LOW: "❓"
        }
        return f"{confidence_emoji[self.confidence]} ~{self.duration.display}"


# Usage
estimate = TimeEstimate.from_similar_tasks(
    similar_tasks=[...],
    estimated_minutes=90
)
print(estimate.display)  # "🎯 ~1 ч 30 мин"
```

---

## 6️⃣ BusinessContext

### Definition
```python
from enum import IntEnum
from dataclasses import dataclass

class BusinessID(IntEnum):
    """The 4 business context identifiers."""
    INVENTUM = 1
    LAB = 2
    R_D = 3
    TRADE = 4

@dataclass(frozen=True)
class BusinessContext:
    """Business context value object.
    
    Represents one of 4 bounded contexts (ADR-003).
    """
    
    id: BusinessID
    name: str
    display_name: str
    keywords: tuple[str, ...]  # Immutable tuple
    
    def __post_init__(self):
        """Validate business context."""
        if self.id not in BusinessID:
            raise ValueError(f"Invalid business_id: {self.id}")
    
    def matches_text(self, text: str) -> int:
        """Count keyword matches (for AI detection)."""
        text_lower = text.lower()
        return sum(1 for keyword in self.keywords if keyword in text_lower)
    
    @property
    def emoji(self) -> str:
        """Emoji representation."""
        emojis = {
            BusinessID.INVENTUM: "🔧",
            BusinessID.LAB: "🦷",
            BusinessID.R_D: "🔬",
            BusinessID.TRADE: "💼"
        }
        return emojis[self.id]


# Predefined contexts (immutable)
INVENTUM_CONTEXT = BusinessContext(
    id=BusinessID.INVENTUM,
    name="inventum",
    display_name="Inventum",
    keywords=("фрезер", "ремонт", "диагностика", "Иванов", "выезд")
)

LAB_CONTEXT = BusinessContext(
    id=BusinessID.LAB,
    name="lab",
    display_name="Inventum Lab",
    keywords=("коронка", "моделирование", "CAD", "CAM", "фрезеровка")
)

R_D_CONTEXT = BusinessContext(
    id=BusinessID.R_D,
    name="r&d",
    display_name="R&D",
    keywords=("прототип", "разработка", "workshop", "тест")
)

TRADE_CONTEXT = BusinessContext(
    id=BusinessID.TRADE,
    name="trade",
    display_name="Import & Trade",
    keywords=("поставщик", "Китай", "контракт", "таможня")
)


# Registry
BUSINESS_CONTEXTS = {
    BusinessID.INVENTUM: INVENTUM_CONTEXT,
    BusinessID.LAB: LAB_CONTEXT,
    BusinessID.R_D: R_D_CONTEXT,
    BusinessID.TRADE: TRADE_CONTEXT
}
```

---

## 7️⃣ ParsedTask (AI Output)

### Definition
```python
@dataclass(frozen=True)
class ParsedTask:
    """Parsed task data from AI (GPT-5 Nano output).
    
    Represents structured extraction from voice/text.
    Immutable - created once from AI response.
    """
    
    title: str
    business_id: int
    deadline: Deadline | None
    project_name: str | None
    assigned_to_name: str | None
    priority: Priority
    description: str | None = None
    
    def __post_init__(self):
        """Validate parsed data."""
        if not self.title or len(self.title) < 3:
            raise ValueError("Title too short")
        
        if self.business_id not in [1, 2, 3, 4]:
            raise ValueError("Invalid business_id")
    
    @classmethod
    def from_gpt_response(cls, response: dict) -> "ParsedTask":
        """Create from GPT-5 Nano JSON response."""
        return cls(
            title=response["title"],
            business_id=response["business_id"],
            deadline=Deadline.from_natural_language(response.get("deadline_text")) 
                if response.get("deadline_text") else None,
            project_name=response.get("project"),
            assigned_to_name=response.get("assigned_to"),
            priority=Priority(response.get("priority", 2)),
            description=response.get("description")
        )
```

---

## 8️⃣ ProjectStatus

### Definition
```python
class ProjectStatus(str, Enum):
    """Project status value object."""
    
    ACTIVE = "active"        # 🟢 Currently working on
    ON_HOLD = "on_hold"      # ⏸️ Paused
    COMPLETED = "completed"  # ✅ Done
    
    @property
    def emoji(self) -> str:
        emojis = {
            ProjectStatus.ACTIVE: "🟢",
            ProjectStatus.ON_HOLD: "⏸️",
            ProjectStatus.COMPLETED: "✅"
        }
        return emojis[self]
```

---

## 9️⃣ HistoryAction

### Definition
```python
class HistoryAction(str, Enum):
    """Action types for task history."""
    
    CREATED = "created"      # Task created
    UPDATED = "updated"      # Task modified
    COMPLETED = "completed"  # Task marked done
    DELETED = "deleted"      # Task deleted
    ARCHIVED = "archived"    # Task archived
```

---

## 🎯 Value Object Principles

### Immutability
```python
# ✅ GOOD: Create new instance
duration = Duration(60)
longer_duration = Duration(90)  # New instance

# ❌ BAD: Try to mutate (won't work with frozen=True)
duration.minutes = 90  # Error!
```

### Equality by Value
```python
# Value objects equal if attributes equal
priority1 = Priority.DO_NOW
priority2 = Priority.DO_NOW
assert priority1 == priority2  # True (same value)

# Entities equal only if ID equal
task1 = Task(id=1, title="Test")
task2 = Task(id=1, title="Different")
assert task1 == task2  # True (same ID)

task3 = Task(id=2, title="Test")
assert task1 != task3  # False (different ID)
```

### Self-Validation
```python
# Validates on construction
try:
    invalid_duration = Duration(-10)  # Raises ValueError
except ValueError as e:
    print(e)  # "Duration must be at least 1 minute"

try:
    invalid_priority = Priority(99)  # Raises ValueError
except ValueError:
    print("Invalid priority")
```

---

## 💡 Usage Examples

### Creating Task with Value Objects
```python
from datetime import datetime
from zoneinfo import ZoneInfo

# Parse deadline from voice
deadline = Deadline.from_natural_language("завтра утром")

# Default estimate
estimate = TimeEstimate.default()

# Create task
task = Task(
    id=1,
    user_id=1,
    business_id=BusinessID.INVENTUM,
    title="Починить фрезер",
    priority=Priority.DO_NOW,
    deadline=deadline.dt,
    estimated_duration=estimate.duration.minutes,
    status=TaskStatus.OPEN
)

# Display in Telegram
message = f"""
✅ Создал задачу:
{task.priority.emoji} {task.title}
🔧 {BUSINESS_CONTEXTS[task.business_id].display_name}
📅 {deadline}
{estimate.display}
"""
```

### Calculating Priority from Urgency/Importance
```python
# AI determines importance and urgency
is_important = True   # Mentioned "важно" or has client name
is_urgent = True      # Mentioned "срочно" or deadline today

# Calculate priority
priority = Priority.from_importance_urgency(is_important, is_urgent)
# Result: Priority.DO_NOW (1)
```

---

## 🧪 Testing Value Objects

```python
def test_duration_creation():
    """Test duration value object."""
    duration = Duration(90)
    assert duration.minutes == 90
    assert duration.hours == 1.5
    assert duration.display == "1 ч 30 мин"


def test_duration_immutable():
    """Test duration is immutable."""
    duration = Duration(60)
    
    with pytest.raises(AttributeError):
        duration.minutes = 90  # Cannot mutate


def test_duration_invalid():
    """Test duration validation."""
    with pytest.raises(ValueError):
        Duration(0)  # Too short
    
    with pytest.raises(ValueError):
        Duration(500)  # Too long (> 8 hours)


def test_deadline_parsing():
    """Test deadline natural language parsing."""
    reference = datetime(2025, 10, 17, 15, 0, tzinfo=ZoneInfo("Asia/Almaty"))
    
    # Tomorrow morning
    deadline = Deadline.from_natural_language("завтра утром", reference)
    assert deadline.dt.hour == 9
    assert deadline.dt.day == 18
    
    # Weekend adjustment (if tomorrow is Saturday)
    reference_friday = datetime(2025, 10, 18, 15, 0, tzinfo=ZoneInfo("Asia/Almaty"))
    deadline = Deadline.from_natural_language("завтра", reference_friday)
    assert deadline.dt.weekday() == 0  # Monday


def test_priority_from_urgency():
    """Test priority calculation."""
    assert Priority.from_importance_urgency(True, True) == Priority.DO_NOW
    assert Priority.from_importance_urgency(True, False) == Priority.SCHEDULE
    assert Priority.from_importance_urgency(False, True) == Priority.DELEGATE
    assert Priority.from_importance_urgency(False, False) == Priority.BACKLOG
```

---

## 📊 Value Objects Summary

| Value Object | Immutable | Validated | Usage |
|--------------|-----------|-----------|-------|
| **Priority** | ✅ | ✅ | Task prioritization |
| **TaskStatus** | ✅ | ✅ | Task lifecycle |
| **ProjectStatus** | ✅ | ✅ | Project lifecycle |
| **Duration** | ✅ | ✅ | Time tracking |
| **Deadline** | ✅ | ✅ | Deadline parsing |
| **BusinessContext** | ✅ | ✅ | Context isolation |
| **TimeEstimate** | ✅ | ✅ | AI estimates |
| **ParsedTask** | ✅ | ✅ | AI output |

---

## 📖 References

- Eric Evans - DDD (Value Objects chapter)
- Martin Fowler - ValueObject pattern
- ADR-003: Business Isolation
- Entities: `docs/04-domain/entities.md`

---

**Status**: ✅ Value Objects Defined  
**Total**: 8 value objects  
**Next**: Define Domain Events

