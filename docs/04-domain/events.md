# Domain Events - Business Planner

> **Events that occur in the domain**  
> **Created**: 2025-10-17  
> **Pattern**: Event-Driven Architecture within DDD

---

## 🎯 What are Domain Events?

**Domain Event** = Something that happened in the domain that domain experts care about

**Characteristics**:
- **Past tense naming** - TaskCreated, TaskCompleted (not CreateTask)
- **Immutable** - Event happened, cannot be changed
- **Timestamped** - When it occurred
- **Contains data** - What happened and relevant context

**Purpose**:
- Trigger side effects (send notification, update analytics)
- Enable event sourcing (audit trail)
- Decouple components (loose coupling)

---

## 📋 Domain Events in Business Planner

### Event Categories

1. **Task Lifecycle Events** - Task created, updated, completed
2. **Learning Events** - Time estimation feedback
3. **Analytics Events** - Weekly reports, insights
4. **System Events** - Errors, warnings

---

## 1️⃣ Task Lifecycle Events

### TaskCreated

```python
from dataclasses import dataclass
from datetime import datetime

@dataclass(frozen=True)
class TaskCreated:
    """Event: New task was created.
    
    Triggered when: User sends voice/text and task is created
    Handlers: 
    - Generate embedding (async)
    - Send confirmation to user
    - Log for analytics
    """
    
    task_id: int
    user_id: int
    business_id: int
    title: str
    deadline: datetime | None
    estimated_duration: int | None
    created_via: str  # "voice" or "text"
    occurred_at: datetime
    
    @classmethod
    def from_task(cls, task: Task, created_via: str) -> "TaskCreated":
        """Create event from task entity."""
        return cls(
            task_id=task.id,
            user_id=task.user_id,
            business_id=task.business_id,
            title=task.title,
            deadline=task.deadline,
            estimated_duration=task.estimated_duration,
            created_via=created_via,
            occurred_at=datetime.now()
        )
```

**Event Handlers**:
```python
async def on_task_created(event: TaskCreated):
    """Handle TaskCreated event."""
    
    # 1. Generate embedding (async, non-blocking)
    await generate_and_store_embedding(event.task_id, event.title)
    
    # 2. Send Telegram confirmation
    await send_task_confirmation(event.user_id, event.task_id)
    
    # 3. Log for analytics
    logger.info(
        "task_created",
        task_id=event.task_id,
        business_id=event.business_id,
        created_via=event.created_via
    )
```

---

### TaskCompleted

```python
@dataclass(frozen=True)
class TaskCompleted:
    """Event: Task was marked as completed.
    
    Triggered when: User marks task done with actual duration
    Handlers:
    - Update RAG learning (store actual duration)
    - Calculate estimation accuracy
    - Log for analytics
    - Trigger congratulations message (optional)
    """
    
    task_id: int
    user_id: int
    business_id: int
    title: str
    estimated_duration: int | None
    actual_duration: int
    estimation_accuracy: float | None
    occurred_at: datetime
    
    @classmethod
    def from_task(cls, task: Task) -> "TaskCompleted":
        """Create event from completed task."""
        return cls(
            task_id=task.id,
            user_id=task.user_id,
            business_id=task.business_id,
            title=task.title,
            estimated_duration=task.estimated_duration,
            actual_duration=task.actual_duration,
            estimation_accuracy=task.estimation_accuracy,
            occurred_at=task.completed_at
        )
```

**Event Handlers**:
```python
async def on_task_completed(event: TaskCompleted):
    """Handle TaskCompleted event."""
    
    # 1. Log learning data (for RAG improvement)
    await log_learning_data(
        task_id=event.task_id,
        business_id=event.business_id,
        estimated=event.estimated_duration,
        actual=event.actual_duration,
        accuracy=event.estimation_accuracy
    )
    
    # 2. Update analytics
    await update_completion_stats(
        user_id=event.user_id,
        business_id=event.business_id,
        duration=event.actual_duration
    )
    
    # 3. Check if estimation is improving
    accuracy = await get_estimation_accuracy(
        user_id=event.user_id,
        business_id=event.business_id
    )
    
    if accuracy > 0.8:  # 80% target
        await send_celebration_message(
            event.user_id,
            f"🎉 Точность оценок достигла {accuracy:.0%}!"
        )
```

---

### TaskUpdated

```python
@dataclass(frozen=True)
class TaskUpdated:
    """Event: Task was modified.
    
    Triggered when: Task fields changed
    Handlers:
    - Re-generate embedding (if title changed)
    - Log changes
    - Notify if assigned to changed
    """
    
    task_id: int
    user_id: int
    changes: dict  # {"field": {"old": ..., "new": ...}}
    occurred_at: datetime
```

---

### TaskDeleted

```python
@dataclass(frozen=True)
class TaskDeleted:
    """Event: Task was deleted/archived.
    
    Triggered when: User deletes task
    Handlers:
    - Remove from active lists
    - Keep in history (soft delete)
    - Log for analytics
    """
    
    task_id: int
    user_id: int
    business_id: int
    title: str
    was_completed: bool
    occurred_at: datetime
```

---

## 2️⃣ Learning Events

### TimeEstimationLearned

```python
@dataclass(frozen=True)
class TimeEstimationLearned:
    """Event: System learned from actual duration.
    
    Triggered when: Task completed with actual_duration
    Handlers:
    - Update learning metrics
    - Trigger re-training (future)
    - Log accuracy improvement
    """
    
    task_id: int
    business_id: int
    estimated_duration: int
    actual_duration: int
    accuracy: float
    similar_tasks_used: int
    occurred_at: datetime
```

**Event Handlers**:
```python
async def on_time_estimation_learned(event: TimeEstimationLearned):
    """Track learning progress."""
    
    # Log learning event
    logger.info(
        "learning_event",
        task_id=event.task_id,
        business_id=event.business_id,
        accuracy=event.accuracy,
        similar_tasks=event.similar_tasks_used
    )
    
    # Update metrics
    await update_learning_metrics(
        business_id=event.business_id,
        accuracy=event.accuracy
    )
```

---

## 3️⃣ Analytics Events

### WeeklyReportGenerated

```python
@dataclass(frozen=True)
class WeeklyReportGenerated:
    """Event: Weekly analytics report created.
    
    Triggered when: User requests /weekly or scheduled weekly
    Handlers:
    - Send report to user via Telegram
    - Store report for history
    - Log insights
    """
    
    user_id: int
    week_start: datetime
    week_end: datetime
    total_tasks_completed: int
    total_time_spent: int  # minutes
    insights: list[str]
    recommendations: list[str]
    occurred_at: datetime
```

---

### BusinessInsightDiscovered

```python
@dataclass(frozen=True)
class BusinessInsightDiscovered:
    """Event: AI discovered pattern or insight.
    
    Triggered when: GPT-5 analytics finds something notable
    Examples:
    - "R&D tasks taking 2x longer than estimated"
    - "Most productive day is Tuesday"
    - "Inventum tasks clustering around repairs"
    """
    
    user_id: int
    business_id: int | None  # None = cross-business insight
    insight_type: str
    description: str
    confidence: float
    occurred_at: datetime
```

---

## 4️⃣ System Events

### VoiceMessageProcessed

```python
@dataclass(frozen=True)
class VoiceMessageProcessed:
    """Event: Voice message was successfully processed.
    
    Triggered when: Voice → Task completed successfully
    Handlers:
    - Update voice processing metrics
    - Log for performance monitoring
    """
    
    user_id: int
    voice_duration_seconds: int
    processing_time_ms: int
    transcript_length: int
    task_created_id: int
    occurred_at: datetime
```

---

### AIOperationFailed

```python
@dataclass(frozen=True)
class AIOperationFailed:
    """Event: AI operation failed.
    
    Triggered when: Whisper, GPT-5 Nano, or embeddings API fails
    Handlers:
    - Alert monitoring
    - Log error
    - Fallback to manual input
    """
    
    operation: str  # "transcribe", "parse", "estimate"
    model: str      # "whisper-1", "gpt-5-nano"
    error_type: str
    error_message: str
    user_id: int
    occurred_at: datetime
```

---

## 🔄 Event Flow Example

### Voice-to-Task Complete Flow

```python
# 1. User sends voice message
# Telegram webhook received

# 2. Voice processing starts
voice_msg = VoiceMessageReceived(...)
await event_bus.publish(voice_msg)

# 3. LangGraph processes voice
# ... transcribe, parse, estimate ...

# 4. Task created
task = await task_repo.create(task_data)
event = TaskCreated.from_task(task, created_via="voice")
await event_bus.publish(event)

# 5. Event handlers execute (async)
# Handler 1: Generate embedding
await on_task_created_generate_embedding(event)

# Handler 2: Send confirmation
await on_task_created_send_confirmation(event)

# Handler 3: Log analytics
await on_task_created_log_analytics(event)

# 6. Voice processing complete
voice_processed = VoiceMessageProcessed(
    user_id=user_id,
    voice_duration_seconds=15,
    processing_time_ms=4500,
    transcript_length=50,
    task_created_id=task.id,
    occurred_at=datetime.now()
)
await event_bus.publish(voice_processed)
```

---

## 🚀 Event Bus Implementation

### Simple In-Memory Event Bus

```python
from collections import defaultdict
from typing import Callable, Awaitable

class EventBus:
    """Simple async event bus."""
    
    def __init__(self):
        self._handlers: dict[type, list[Callable]] = defaultdict(list)
    
    def subscribe(self, event_type: type, handler: Callable[[any], Awaitable[None]]):
        """Subscribe handler to event type."""
        self._handlers[event_type].append(handler)
    
    async def publish(self, event: any):
        """Publish event to all handlers."""
        event_type = type(event)
        handlers = self._handlers.get(event_type, [])
        
        # Execute all handlers (in parallel if possible)
        await asyncio.gather(*[
            self._safe_execute(handler, event)
            for handler in handlers
        ])
    
    async def _safe_execute(self, handler: Callable, event: any):
        """Execute handler with error handling."""
        try:
            await handler(event)
        except Exception as e:
            logger.exception(
                f"Event handler failed: {handler.__name__}",
                event_type=type(event).__name__,
                error=str(e)
            )


# Global event bus
event_bus = EventBus()

# Subscribe handlers
event_bus.subscribe(TaskCreated, on_task_created_generate_embedding)
event_bus.subscribe(TaskCreated, on_task_created_send_confirmation)
event_bus.subscribe(TaskCompleted, on_task_completed_learn)
```

---

## 📊 Event Catalog

### All Domain Events

| Event | Frequency | Critical | Handlers |
|-------|-----------|----------|----------|
| **TaskCreated** | ~500/month | ⭐⭐⭐ | 3 |
| **TaskCompleted** | ~400/month | ⭐⭐⭐ | 2 |
| **TaskUpdated** | ~50/month | ⭐ | 1 |
| **TaskDeleted** | ~20/month | ⭐ | 1 |
| **TimeEstimationLearned** | ~400/month | ⭐⭐ | 1 |
| **WeeklyReportGenerated** | 4/month | ⭐⭐ | 1 |
| **VoiceMessageProcessed** | ~500/month | ⭐ | 1 |
| **AIOperationFailed** | ~5/month | ⭐⭐⭐ | 1 |

---

## 🧪 Testing Events

```python
async def test_event_publishing():
    """Test event bus publishes to handlers."""
    
    handler_called = False
    event_received = None
    
    async def test_handler(event: TaskCreated):
        nonlocal handler_called, event_received
        handler_called = True
        event_received = event
    
    # Subscribe
    event_bus.subscribe(TaskCreated, test_handler)
    
    # Publish
    event = TaskCreated(
        task_id=1,
        user_id=1,
        business_id=1,
        title="Test",
        occurred_at=datetime.now()
    )
    await event_bus.publish(event)
    
    # Verify
    assert handler_called
    assert event_received.task_id == 1


async def test_multiple_handlers():
    """Test multiple handlers for same event."""
    
    call_count = 0
    
    async def handler1(event: TaskCreated):
        nonlocal call_count
        call_count += 1
    
    async def handler2(event: TaskCreated):
        nonlocal call_count
        call_count += 1
    
    event_bus.subscribe(TaskCreated, handler1)
    event_bus.subscribe(TaskCreated, handler2)
    
    event = TaskCreated(...)
    await event_bus.publish(event)
    
    assert call_count == 2  # Both handlers called
```

---

## 📖 References

- Martin Fowler - Domain Events
- Eric Evans - DDD (Domain Events pattern)
- Entities: `docs/04-domain/entities.md`
- Value Objects: `docs/04-domain/value-objects.md`

---

**Status**: ✅ Domain Events Defined  
**Total Events**: 8 core events  
**Pattern**: Event-driven architecture within DDD  
**Next**: Define Business Rules

