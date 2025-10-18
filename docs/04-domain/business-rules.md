# Business Rules - Business Planner

> **Domain logic and constraints**  
> **Created**: 2025-10-17  
> **Source**: User requirements, ADR-003

---

## 🎯 What are Business Rules?

**Business Rules** = Constraints and logic that reflect real business requirements

**Types**:
- **Invariants** - Must always be true
- **Validation Rules** - Check input validity
- **Calculation Rules** - How to compute values
- **Workflow Rules** - Process constraints

---

## 📋 Core Business Rules

---

## 1️⃣ Task Creation Rules

### Rule 1.1: Business Context is Mandatory

**Rule**: Every task MUST have a business context (business_id)

**Rationale**: ADR-003 - Business isolation is critical

**Implementation**:
```python
def create_task(title: str, business_id: int | None, ...) -> Task:
    if business_id is None:
        raise ValueError(
            "business_id is mandatory. Every task must belong to one of 4 businesses."
        )
    
    if business_id not in [1, 2, 3, 4]:
        raise ValueError(f"Invalid business_id: {business_id}")
    
    return Task(business_id=business_id, ...)
```

**Database Enforcement**:
```sql
ALTER TABLE tasks 
ALTER COLUMN business_id SET NOT NULL;
```

---

### Rule 1.2: Project is Optional

**Rule**: Projects are NOT auto-created, user must explicitly create them

**Rationale**: Keep simple, avoid over-structuring

**Implementation**:
```python
# ✅ CORRECT: project_id can be None
task = Task(title="Test", business_id=1, project_id=None)

# ❌ WRONG: Don't auto-create projects
# if not project_id:
#     project_id = auto_create_project(title)  # Don't do this!
```

---

### Rule 1.3: Default Deadline

**Rule**: If no deadline specified, default to +7 days at 23:59

**Rationale**: User preference for week planning

**Implementation**:
```python
def create_task(deadline: datetime | None = None, ...) -> Task:
    if deadline is None:
        deadline = datetime.now(ZoneInfo("Asia/Almaty")) + timedelta(days=7)
        deadline = deadline.replace(hour=23, minute=59, second=0)
    
    return Task(deadline=deadline, ...)
```

---

### Rule 1.4: Auto-Assign Based on Context

**Rule**: Suggest team member based on business and task type (but don't force)

**Rationale**: Help user delegate, but user has final say

**Implementation**:
```python
def suggest_assignee(task: Task) -> Member | None:
    """Suggest team member for task."""
    
    # Get members who work in this business
    eligible_members = [
        m for m in all_members 
        if task.business_id in m.business_ids
    ]
    
    # Match by skills (if task has keywords)
    title_lower = task.title.lower()
    
    for member in eligible_members:
        for skill in member.skills:
            if skill in title_lower:
                return member
    
    # No match, return most common assignee for this business
    return get_most_common_assignee(task.business_id)
```

---

## 2️⃣ Deadline Parsing Rules

### Rule 2.1: Workday Only

**Rule**: Deadlines on weekends automatically move to Monday 09:00

**Rationale**: User works Monday-Friday

**Implementation**:
```python
def adjust_deadline_for_workday(deadline: datetime) -> datetime:
    """Move weekend deadlines to Monday."""
    
    # Saturday (5) → Monday
    if deadline.weekday() == 5:
        deadline = deadline + timedelta(days=2)
        deadline = deadline.replace(hour=9, minute=0)
    
    # Sunday (6) → Monday
    elif deadline.weekday() == 6:
        deadline = deadline + timedelta(days=1)
        deadline = deadline.replace(hour=9, minute=0)
    
    return deadline
```

**Example**:
```
Voice: "Сделать это в субботу"
Parsed: Saturday 10:00
Adjusted: Monday 09:00 ✅
```

---

### Rule 2.2: Time of Day Defaults

**Rule**: Natural language time converts to specific hours

| Russian | Hour | English |
|---------|------|---------|
| "утром" | 09:00 | Morning |
| "днем" / "обед" | 13:00 | Afternoon |
| "вечером" | 18:00 | Evening |
| (not specified) | 23:59 | End of day |

**Implementation**:
```python
TIME_OF_DAY = {
    "утр": 9,
    "дн": 13,
    "обед": 13,
    "вечер": 18
}

def parse_time_of_day(text: str) -> int:
    """Parse hour from Russian text."""
    text_lower = text.lower()
    
    for keyword, hour in TIME_OF_DAY.items():
        if keyword in text_lower:
            return hour
    
    return 23  # Default: end of day
```

---

### Rule 2.3: Timezone is Always UTC+5

**Rule**: All times in Almaty timezone (UTC+5)

**Rationale**: User location (Almaty, Kazakhstan)

**Implementation**:
```python
from zoneinfo import ZoneInfo

ALMATY_TZ = ZoneInfo("Asia/Almaty")

def parse_deadline(text: str) -> datetime:
    """Parse deadline in Almaty timezone."""
    deadline = parse_natural_language(text)
    
    # Ensure timezone
    if deadline.tzinfo is None:
        deadline = deadline.replace(tzinfo=ALMATY_TZ)
    
    return deadline
```

---

## 3️⃣ Priority Calculation Rules

### Rule 3.1: Eisenhower Matrix

**Rule**: Priority calculated from importance × urgency

```
           Urgent       Not Urgent
Important    1 (DO)      2 (SCHEDULE)
Not Imp.     3 (DELEG)   4 (BACKLOG)
```

**Urgency Signals**:
- Deadline today/tomorrow → Urgent
- Words: "срочно", "быстро", "сегодня" → Urgent
- Client name mentioned → Urgent (for Inventum)

**Importance Signals**:
- Words: "важно", "критично" → Important
- Project mentioned → Important
- CEO creates task → Important

**Implementation**:
```python
def calculate_priority(
    deadline: datetime | None,
    text: str,
    has_project: bool
) -> Priority:
    """Calculate priority from signals."""
    
    # Determine urgency
    is_urgent = False
    if deadline:
        hours_until = (deadline - datetime.now()).total_seconds() / 3600
        is_urgent = hours_until < 48  # Within 2 days
    
    text_lower = text.lower()
    if any(word in text_lower for word in ["срочно", "быстро", "сегодня"]):
        is_urgent = True
    
    # Determine importance
    is_important = False
    if has_project:
        is_important = True
    
    if any(word in text_lower for word in ["важно", "критично"]):
        is_important = True
    
    # Calculate
    return Priority.from_importance_urgency(is_important, is_urgent)
```

---

### Rule 3.2: User Can Override

**Rule**: AI suggests priority, but user can change it

**Rationale**: User knows context best

**Implementation**:
```python
# AI suggests
suggested_priority = calculate_priority(...)

# User can override
task = Task(
    priority=suggested_priority,  # Default
    ...
)

# Later, user changes
await task_service.update_priority(task_id, new_priority=Priority.DO_NOW)
```

---

## 4️⃣ Time Estimation Rules

### Rule 4.1: RAG Must Filter by Business

**Rule**: When finding similar tasks, MUST filter by business_id

**Rationale**: ADR-003 - Prevent context contamination

**Implementation**:
```python
async def estimate_time(task: Task) -> TimeEstimate:
    """Estimate time using RAG."""
    
    # Generate embedding
    embedding = await generate_embedding(task.title)
    
    # Find similar tasks (MUST filter by business!)
    similar_tasks = await task_repo.find_similar(
        embedding=embedding,
        business_id=task.business_id,  # CRITICAL!
        limit=5
    )
    
    # Estimate from similar
    if similar_tasks:
        avg_duration = sum(t.actual_duration for t in similar_tasks) / len(similar_tasks)
        return TimeEstimate.from_similar_tasks(similar_tasks, int(avg_duration))
    else:
        return TimeEstimate.default()
```

**Validation**:
```python
# Assert business isolation
for similar_task in similar_tasks:
    assert similar_task.business_id == task.business_id, \
        f"RAG isolation breach! Expected {task.business_id}, got {similar_task.business_id}"
```

---

### Rule 4.2: Similarity Threshold

**Rule**: Only use tasks with similarity > 0.7 for estimation

**Rationale**: Low similarity = wrong context, hurts accuracy

**Implementation**:
```python
SIMILARITY_THRESHOLD = 0.7

async def find_similar_tasks(...) -> list[Task]:
    """Find similar tasks above threshold."""
    
    results = await vector_search(...)
    
    # Filter by similarity
    filtered = [
        task for task in results
        if task.similarity >= SIMILARITY_THRESHOLD
    ]
    
    return filtered
```

---

### Rule 4.3: Learning Feedback Loop

**Rule**: When task completed, store actual_duration for future learning

**Rationale**: System improves over time (50% → 80% accuracy goal)

**Implementation**:
```python
async def complete_task(task_id: int, actual_duration: int):
    """Complete task with learning."""
    
    task = await task_repo.get_by_id(task_id)
    
    # Store actual duration
    task.complete(actual_duration)
    
    # Publish learning event
    event = TimeEstimationLearned(
        task_id=task.id,
        business_id=task.business_id,
        estimated_duration=task.estimated_duration,
        actual_duration=actual_duration,
        accuracy=task.estimation_accuracy,
        similar_tasks_used=...
    )
    await event_bus.publish(event)
    
    # Future searches will now include this task!
    # No explicit retraining needed (RAG searches in real-time)
```

---

## 5️⃣ Business Context Detection Rules

### Rule 5.1: Keyword Matching

**Rule**: AI detects business from keywords in voice transcript

**Implementation**:
```python
def detect_business_context(transcript: str) -> BusinessID:
    """Detect business from transcript."""
    
    scores = {}
    
    for business in BUSINESS_CONTEXTS.values():
        scores[business.id] = business.matches_text(transcript)
    
    # Get business with most matches
    best_business_id = max(scores, key=scores.get)
    
    # If no matches, ask user or use default
    if scores[best_business_id] == 0:
        return None  # AI will ask user
    
    return best_business_id
```

**Examples**:
```
"Нужно починить фрезер для Иванова"
→ Keywords match: "починить" (repair), "фрезер", "Иванов" (client)
→ Business: INVENTUM ✅

"Смоделировать коронку в CAD"
→ Keywords match: "моделировать", "коронку", "CAD"
→ Business: LAB ✅

"Позвонить поставщику из Китая"
→ Keywords match: "поставщику", "Китая"
→ Business: TRADE ✅
```

---

## 6️⃣ Team Assignment Rules

### Rule 6.1: Member Must Work in Business

**Rule**: Can only assign task to member who works in that business

**Validation**:
```python
def assign_task(task: Task, member: Member):
    """Assign task to member."""
    
    if task.business_id not in member.business_ids:
        raise ValueError(
            f"Cannot assign {member.name} to {task.business_id} task. "
            f"Member only works in: {member.business_ids}"
        )
    
    task.assigned_to = member.id
```

**Example**:
```python
# ✅ OK: Мария works in Lab (business_id=2)
lab_task = Task(business_id=2, ...)
assign_task(lab_task, maria)  # Works

# ❌ ERROR: Мария doesn't work in Inventum (business_id=1)
inventum_task = Task(business_id=1, ...)
assign_task(inventum_task, maria)  # Raises ValueError
```

---

### Rule 6.2: Auto-Suggestion Logic

**Rule**: Suggest assignee based on task type and business

**Logic**:
```python
ASSIGNMENT_RULES = {
    BusinessID.INVENTUM: {
        "keywords": {
            "выезд": "Максут",      # Field service → Максут
            "ремонт": "Дима",        # Repairs → Дима
            "диагностика": "Дима",   # Diagnostics → Дима
            "управ": "Максим"        # Management → Максим
        },
        "default": "Дима"
    },
    
    BusinessID.LAB: {
        "keywords": {
            "модел": "Мария",        # Modeling → Мария
            "CAD": "Мария",
            "CAM": "Мария",
            "фрезер": "Мария",
            "управ": "Юрий Владимирович"
        },
        "default": "Мария"
    },
    
    BusinessID.R_D: {
        "keywords": {
            "тест": "Дима",
            "прототип": "Дима",
            "дизайн": "Максим",
            "документ": "Максим"
        },
        "default": "Максим"
    },
    
    BusinessID.TRADE: {
        "keywords": {},
        "default": "Слава"  # All trade tasks → Слава
    }
}
```

---

## 7️⃣ Deadline Rules

### Rule 7.1: Weekend Adjustment

**Rule**: Deadlines on Saturday/Sunday move to Monday 09:00

**Rationale**: User works Monday-Friday only

**Implementation**: See Rule 2.1 above

---

### Rule 7.2: Past Deadlines Not Allowed

**Rule**: Cannot set deadline in the past

**Validation**:
```python
def validate_deadline(deadline: datetime) -> datetime:
    """Validate and adjust deadline."""
    
    now = datetime.now(ZoneInfo("Asia/Almaty"))
    
    if deadline < now:
        raise ValueError("Cannot set deadline in the past")
    
    # Adjust for weekend
    deadline = adjust_for_workday(deadline)
    
    return deadline
```

**Exception**: When editing existing task, past deadline allowed (to fix mistakes)

---

## 8️⃣ Priority Rules

### Rule 8.1: Today + No Time = High Priority

**Rule**: If deadline is today and no specific time, mark as DO_NOW (Priority 1)

**Rationale**: Likely urgent if must be done today

**Implementation**:
```python
def calculate_priority_from_deadline(deadline: datetime | None) -> Priority:
    """Calculate priority from deadline."""
    
    if deadline is None:
        return Priority.SCHEDULE  # Default
    
    now = datetime.now(ZoneInfo("Asia/Almaty"))
    hours_until = (deadline - now).total_seconds() / 3600
    
    if hours_until < 4:  # Less than 4 hours
        return Priority.DO_NOW
    elif hours_until < 48:  # Less than 2 days
        return Priority.SCHEDULE
    else:
        return Priority.SCHEDULE  # More than 2 days
```

---

## 9️⃣ Project Rules

### Rule 9.1: Projects Belong to One Business

**Rule**: Projects cannot span multiple businesses

**Rationale**: Business isolation (ADR-003)

**Validation**:
```python
def create_project(name: str, business_id: int, ...) -> Project:
    """Create project."""
    
    if business_id not in [1, 2, 3, 4]:
        raise ValueError("Project must belong to one business")
    
    return Project(business_id=business_id, ...)
```

---

### Rule 9.2: Cannot Delete Project with Active Tasks

**Rule**: Must complete/delete all tasks before deleting project

**Validation**:
```python
async def delete_project(project_id: int):
    """Delete project."""
    
    # Check for active tasks
    active_tasks = await task_repo.find_by_project(
        project_id, 
        status=TaskStatus.OPEN
    )
    
    if active_tasks:
        raise ValueError(
            f"Cannot delete project with {len(active_tasks)} active tasks. "
            "Complete or delete tasks first."
        )
    
    await project_repo.delete(project_id)
```

---

## 🔟 RAG (Learning) Rules

### Rule 10.1: Business Isolation in RAG

**Rule**: Vector search MUST filter by business_id

**Rationale**: ADR-003 - Prevent cross-context contamination

**Implementation**: See Rule 4.1 above

**Validation**:
```python
# Every RAG search must include this assert
async def find_similar_tasks(embedding, business_id, ...) -> list[Task]:
    results = await vector_search(...)
    
    # Paranoid validation
    for task in results:
        assert task.business_id == business_id, \
            f"RAG isolation breach: expected {business_id}, got {task.business_id}"
    
    return results
```

---

### Rule 10.2: Minimum Similarity Threshold

**Rule**: Only use tasks with similarity ≥ 0.7 for estimation

**Rationale**: Low similarity = different task type, wrong estimate

**Implementation**:
```python
SIMILARITY_THRESHOLD = 0.7

similar_tasks = [
    task for task in candidates
    if task.similarity >= SIMILARITY_THRESHOLD
]
```

---

### Rule 10.3: Completed Tasks Only for Learning

**Rule**: Only use tasks with actual_duration for RAG estimation

**Rationale**: Can't learn from incomplete tasks

**Implementation**:
```sql
SELECT * FROM tasks
WHERE business_id = $1
  AND embedding IS NOT NULL
  AND actual_duration IS NOT NULL  -- Only completed
  AND status = 'done'
ORDER BY embedding <=> $2
LIMIT 5;
```

---

## 1️⃣1️⃣ Voice Processing Rules

### Rule 11.1: Voice Length Limit

**Rule**: Voice messages max 2 minutes (120 seconds)

**Rationale**: Cost control, focus encouragement

**Validation**:
```python
MAX_VOICE_LENGTH = 120  # seconds

async def process_voice(voice_file) -> Task:
    """Process voice message."""
    
    if voice_file.duration > MAX_VOICE_LENGTH:
        raise ValueError(
            f"Voice message too long ({voice_file.duration}s). "
            f"Maximum {MAX_VOICE_LENGTH}s. Please be concise."
        )
    
    # Process...
```

---

### Rule 11.2: Russian Language Only

**Rule**: System processes Russian language only

**Validation**:
```python
async def validate_transcript(transcript: str) -> bool:
    """Check if transcript is in Russian."""
    
    # Simple heuristic: Check for Cyrillic characters
    cyrillic_count = sum(1 for c in transcript if '\u0400' <= c <= '\u04FF')
    total_letters = sum(1 for c in transcript if c.isalpha())
    
    if total_letters == 0:
        return False
    
    cyrillic_ratio = cyrillic_count / total_letters
    
    if cyrillic_ratio < 0.5:  # Less than 50% Cyrillic
        raise ValueError(
            "Пожалуйста, используйте русский язык. "
            "Please use Russian language."
        )
    
    return True
```

---

## 1️⃣2️⃣ Duration Validation Rules

### Rule 12.1: Duration Range

**Rule**: Task duration must be 1-480 minutes (1 min to 8 hours)

**Rationale**: Reasonable bounds, prevents errors

**Validation**:
```python
def validate_duration(minutes: int | None) -> int | None:
    """Validate duration is in valid range."""
    
    if minutes is None:
        return None
    
    if minutes < 1:
        raise ValueError("Duration must be at least 1 minute")
    
    if minutes > 480:  # 8 hours
        raise ValueError(
            "Duration cannot exceed 480 minutes (8 hours). "
            "Consider breaking into smaller tasks."
        )
    
    return minutes
```

---

### Rule 12.2: Actual Duration for Learning

**Rule**: actual_duration only set when status = done

**Validation**:
```python
def complete_task(task: Task, actual_duration: int):
    """Complete task with duration."""
    
    if task.status == TaskStatus.DONE:
        raise ValueError("Task already completed")
    
    # Validate duration
    validate_duration(actual_duration)
    
    # Complete
    task.status = TaskStatus.DONE
    task.actual_duration = actual_duration
    task.completed_at = datetime.now()
```

---

## 1️⃣3️⃣ Status Transition Rules

### Rule 13.1: Allowed Transitions

**Rule**: Status can only transition in valid ways

```
OPEN → DONE ✅
DONE → ARCHIVED ✅
DONE → OPEN ✅ (reopen)
OPEN → ARCHIVED ❌ (must complete first)
ARCHIVED → anything ❌ (final state)
```

**Validation**:
```python
def transition_status(task: Task, new_status: TaskStatus):
    """Transition task status."""
    
    if not task.status.can_transition_to(new_status):
        raise ValueError(
            f"Invalid transition: {task.status} → {new_status}. "
            f"Allowed: {ALLOWED_TRANSITIONS[task.status]}"
        )
    
    task.status = new_status
```

---

## 🎯 Business Rules Summary

### Critical Rules (MUST ENFORCE)

| Rule | Enforcement | Severity |
|------|-------------|----------|
| Business context mandatory | DB + App | 🔴 Critical |
| RAG filters by business_id | App | 🔴 Critical |
| Weekend → Monday | App | 🟡 Important |
| Duration 1-480 minutes | DB + App | 🟡 Important |
| Priority 1-4 | DB + App | 🟡 Important |
| Valid status transitions | App | 🟡 Important |

### Soft Rules (SHOULD FOLLOW)

| Rule | Enforcement | Severity |
|------|-------------|----------|
| Default deadline +7 days | App | 🟢 Nice to have |
| Auto-assign suggestion | App | 🟢 Nice to have |
| Time of day defaults | App | 🟢 Nice to have |
| Voice length limit | App | 🟢 Nice to have |

---

## 🧪 Testing Business Rules

```python
async def test_business_context_mandatory():
    """Test that business_id is required."""
    
    with pytest.raises(ValueError, match="business_id is mandatory"):
        task = Task(
            title="Test",
            user_id=1,
            business_id=None  # Error!
        )


async def test_weekend_deadline_adjustment():
    """Test weekend deadlines move to Monday."""
    
    # Saturday deadline
    saturday = datetime(2025, 10, 18, 10, 0, tzinfo=ALMATY_TZ)  # Saturday
    
    deadline = Deadline(saturday)
    adjusted = deadline._adjust_for_workday(saturday)
    
    assert adjusted.weekday() == 0  # Monday
    assert adjusted.hour == 9  # 09:00


async def test_rag_business_isolation():
    """Test RAG respects business boundaries."""
    
    task = Task(business_id=BusinessID.INVENTUM, ...)
    
    similar = await find_similar_tasks(task)
    
    # All results must be from same business
    for similar_task in similar:
        assert similar_task.business_id == BusinessID.INVENTUM
```

---

## 📖 References

- Project Brief: `docs/00-project-brief.md` (Business Rules section)
- ADR-003: Business Context Isolation
- Entities: `docs/04-domain/entities.md`
- Value Objects: `docs/04-domain/value-objects.md`

---

**Status**: ✅ Business Rules Documented  
**Total Rules**: 13 major rules + sub-rules  
**Critical Rules**: 6  
**Implementation**: Code examples provided for all

