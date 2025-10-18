# ADR-003: Business Context Isolation Strategy

**Status**: ✅ Accepted  
**Date**: 2025-10-17  
**Deciders**: Константин (CEO), Development Team  
**Tags**: architecture, domain, critical, data-isolation

⚠️ **CRITICAL DECISION** - This is a fundamental architectural constraint

---

## Context

Business Planner serves one user (Константин) who manages **4 distinct businesses**:

1. **Inventum** - Dental equipment repair
   - Keywords: фрезер, ремонт, диагностика, Иванов (client)
   - Tasks: repairs, diagnostics, client visits
   
2. **Inventum Lab** - Dental laboratory
   - Keywords: коронка, моделирование, CAD/CAM, зуб
   - Tasks: modeling, milling, crown production
   
3. **R&D** - Prototype development
   - Keywords: прототип, разработка, workshop, тест
   - Tasks: design, testing, documentation
   
4. **Import & Trade** - Equipment import from China
   - Keywords: поставщик, Китай, контракт, таможня
   - Tasks: supplier calls, logistics, customs

### The Problem

The same words mean **different things** in different business contexts:

| Word | Inventum | R&D | Meaning Overlap |
|------|----------|-----|-----------------|
| "диагностика" | Equipment diagnostics | Prototype diagnostics | ❌ Different workflows |
| "ремонт" | Client equipment repair | Workshop tool repair | ❌ Different urgency |
| "тест" | Test repaired equipment | Test new prototype | ❌ Different procedures |
| "звонок" | Call client about repair | Call supplier about parts | ❌ Different contacts |

**Critical Issue**: If RAG (Retrieval-Augmented Generation) searches across all businesses without filtering:
- "диагностика" task in Inventum might retrieve R&D diagnostics history
- Time estimates would be contaminated (different durations)
- AI suggestions would be wrong (different team members)
- User experience degrades (wrong context)

---

## Decision

We will implement **STRICT BUSINESS CONTEXT ISOLATION** throughout the system:

1. **Every task MUST have a business_id** (NOT NULL constraint)
2. **All RAG searches MUST filter by business_id**
3. **All embeddings include business context**
4. **Analytics are per-business by default**
5. **No cross-business data leakage**

---

## Alternatives Considered

### 1. No Isolation (Single Context)
**Description**: Treat all tasks as one pool

**Pros**:
- ✅ Simpler database schema
- ✅ Easier to implement
- ✅ Faster development

**Cons**:
- ❌ **FATAL**: Word ambiguity causes wrong suggestions
- ❌ Time estimates contaminated across businesses
- ❌ AI cannot distinguish context
- ❌ Analytics meaningless (mixed data)
- ❌ Breaks core user requirement

**Example failure**:
```
User: "Нужна диагностика"
AI searches all tasks, finds:
- Inventum: Equipment diagnostics (2 hours)
- R&D: Prototype diagnostics (4 hours)
AI suggests: 3 hours (average)
WRONG: Context matters!
```

**Verdict**: ❌ **Rejected** - Fundamentally breaks requirements

---

### 2. Soft Isolation (Tags/Labels)
**Description**: Use tags for businesses, but don't enforce

**Pros**:
- ✅ Flexible
- ✅ Could combine when needed
- ✅ Easy to add new "categories"

**Cons**:
- ❌ Not enforced (can forget to filter)
- ❌ Bugs are silent (wrong results, not errors)
- ❌ RAG contamination still possible
- ❌ Hard to debug "why is this suggestion wrong?"

**Example failure**:
```python
# Developer forgets to filter
similar_tasks = await vector_search(embedding)
# Returns mixed results from all businesses
# Bug is silent - code works but results wrong
```

**Verdict**: ❌ **Rejected** - Too easy to make mistakes

---

### 3. Separate Databases per Business
**Description**: 4 different PostgreSQL databases

**Pros**:
- ✅ Complete isolation
- ✅ Impossible to mix data
- ✅ Could scale businesses independently

**Cons**:
- ❌ 4x infrastructure complexity
- ❌ Cross-business queries impossible (user overview)
- ❌ 4x migration effort
- ❌ Overkill for single-user system
- ❌ Higher costs

**Verdict**: ❌ **Rejected** - Over-engineering

---

### 4. Strict Context Isolation with Validation ⭐
**Description**: Single database, strict filtering, enforced at multiple levels

**Pros**:
- ✅ **Single source of truth**
- ✅ **Database constraints** enforce rules
- ✅ **Application-level validation**
- ✅ **RAG filtering mandatory**
- ✅ **Fails fast** (errors, not silent bugs)
- ✅ **Can do cross-business queries** (for CEO overview)
- ✅ **Testable** (can verify isolation)

**Cons**:
- ⚠️ Requires discipline in development
- ⚠️ More code (but safer code)

**Verdict**: ✅ **Accepted** - Best balance of isolation and practicality

---

## Implementation Strategy

### 1. Database Level

#### Schema Constraints
```sql
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    business_id INTEGER NOT NULL,  -- MUST NOT BE NULL
    user_id INTEGER NOT NULL,
    embedding vector(1536),
    -- ... other fields
    
    CONSTRAINT fk_business 
        FOREIGN KEY (business_id) 
        REFERENCES businesses(id)
        ON DELETE RESTRICT,  -- Cannot delete business with tasks
        
    CONSTRAINT valid_business
        CHECK (business_id IN (1, 2, 3, 4))  -- Only 4 businesses
);

-- Index for fast filtering
CREATE INDEX idx_tasks_business 
    ON tasks(business_id);

-- Composite index for RAG queries
CREATE INDEX idx_tasks_business_embedding
    ON tasks USING ivfflat (embedding vector_cosine_ops)
    WHERE business_id IS NOT NULL;
```

#### Business Reference Table
```sql
CREATE TABLE businesses (
    id INTEGER PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    keywords TEXT[]
);

INSERT INTO businesses VALUES
    (1, 'inventum', 'Dental equipment repair', 
     ARRAY['фрезер', 'ремонт', 'диагностика', 'Иванов']),
    (2, 'lab', 'Dental laboratory', 
     ARRAY['коронка', 'моделирование', 'CAD', 'CAM']),
    (3, 'r&d', 'R&D and prototypes', 
     ARRAY['прототип', 'разработка', 'workshop']),
    (4, 'trade', 'Import and trade', 
     ARRAY['поставщик', 'Китай', 'контракт', 'таможня']);
```

---

### 2. Application Level

#### Domain Model
```python
from enum import IntEnum

class BusinessID(IntEnum):
    INVENTUM = 1
    LAB = 2
    R_AND_D = 3
    TRADE = 4

class Task(BaseModel):
    id: int
    title: str
    business_id: BusinessID  # Required, strongly typed
    user_id: int
    embedding: list[float] | None
    # ...
    
    @validator('business_id')
    def validate_business(cls, v):
        if v not in BusinessID:
            raise ValueError(f"Invalid business_id: {v}")
        return v
```

#### Repository Pattern with Mandatory Filtering
```python
class TaskRepository(Protocol):
    async def find_similar(
        self,
        embedding: list[float],
        business_id: BusinessID,  # MANDATORY parameter
        top_k: int = 5
    ) -> list[Task]:
        """Find similar tasks.
        
        Args:
            embedding: Task embedding vector
            business_id: REQUIRED - Business context for isolation
            top_k: Number of results
            
        Note:
            business_id is mandatory to prevent cross-business contamination.
            This is a CRITICAL architectural constraint.
        """
        ...
```

#### RAG Service with Validation
```python
class RAGService:
    async def find_similar_tasks(
        self, 
        task: Task,
        top_k: int = 5
    ) -> list[Task]:
        """Find similar tasks with STRICT business isolation."""
        
        # Validation
        if not task.business_id:
            raise ValueError(
                "CRITICAL: business_id required for RAG search. "
                "This prevents cross-business contamination."
            )
        
        if not task.embedding:
            raise ValueError("Task must have embedding for similarity search")
        
        # Search with mandatory business filter
        similar = await self.repo.find_similar(
            embedding=task.embedding,
            business_id=task.business_id,  # CRITICAL: Filter by business
            top_k=top_k
        )
        
        # Double-check (paranoid validation)
        for similar_task in similar:
            assert similar_task.business_id == task.business_id, \
                f"RAG isolation breach: got {similar_task.business_id}, " \
                f"expected {task.business_id}"
        
        return similar
```

---

### 3. AI/LangGraph Level

#### Context in Prompts
```python
async def estimate_time_with_rag(state: TaskState) -> TaskState:
    """Estimate time using RAG with business context."""
    
    task = state["task"]
    
    # Get similar tasks (automatically filtered by business)
    similar_tasks = await rag_service.find_similar_tasks(task)
    
    # Build context for GPT-5 Nano
    context = f"""
    Business context: {task.business_name} ({task.business_id})
    
    This is for {task.business_name} specifically.
    DO NOT use data from other businesses.
    
    Similar past tasks in {task.business_name}:
    {format_similar_tasks(similar_tasks)}
    
    New task: {task.title}
    
    Estimate duration in minutes based ONLY on similar {task.business_name} tasks.
    """
    
    estimated_duration = await gpt_estimate(context)
    
    return {**state, "estimated_duration": estimated_duration}
```

---

### 4. Testing Level

#### Integration Tests
```python
async def test_rag_isolation_inventum_vs_rd():
    """Test that RAG does not mix Inventum and R&D contexts."""
    
    # Create tasks in different businesses
    inventum_task = await create_task(
        title="Диагностика фрезера",
        business_id=BusinessID.INVENTUM
    )
    
    rd_task = await create_task(
        title="Диагностика прототипа",
        business_id=BusinessID.R_AND_D
    )
    
    # Search from Inventum task
    similar_to_inventum = await rag_service.find_similar_tasks(inventum_task)
    
    # Verify: Should ONLY get Inventum tasks
    for task in similar_to_inventum:
        assert task.business_id == BusinessID.INVENTUM, \
            f"RAG isolation breach: Found {task.business_id} task when searching Inventum"
    
    # Search from R&D task
    similar_to_rd = await rag_service.find_similar_tasks(rd_task)
    
    # Verify: Should ONLY get R&D tasks
    for task in similar_to_rd:
        assert task.business_id == BusinessID.R_AND_D, \
            f"RAG isolation breach: Found {task.business_id} task when searching R&D"
```

---

## Enforcement Mechanisms

### 1. Database Constraints
- ✅ NOT NULL on business_id
- ✅ Foreign key to businesses table
- ✅ CHECK constraint for valid IDs

### 2. Type System
- ✅ Enum for BusinessID (compile-time safety)
- ✅ Pydantic validation
- ✅ Mandatory parameters

### 3. Runtime Validation
- ✅ Assert statements in critical paths
- ✅ Exceptions for violations
- ✅ Logging of business context

### 4. Code Review
- ✅ Checklist item: "Business isolation maintained?"
- ✅ Any vector search must have business_id filter
- ✅ Any analytics must specify business or aggregate properly

### 5. Monitoring
- ✅ Log business_id with every operation
- ✅ Alert if cross-business queries detected
- ✅ Metrics per business

---

## Edge Cases & Solutions

### Cross-Business Team Members

**Problem**: Максим and Дима work in both Inventum and R&D

**Solution**:
- Tasks still have single business_id
- Team members can have multiple business associations
- When creating task, business context determines isolation
- Same person, different contexts

```python
# Максим in Inventum context
inventum_task = Task(
    title="Починить фрезер",
    business_id=BusinessID.INVENTUM,
    assigned_to="Максим"
)

# Максим in R&D context (DIFFERENT business)
rd_task = Task(
    title="Тест прототипа",
    business_id=BusinessID.R_AND_D,
    assigned_to="Максим"
)

# These are isolated despite same person
```

### CEO Overview

**Problem**: Константин needs to see all businesses

**Solution**:
- Explicit cross-business queries allowed
- But default is always single-business
- Clear indication when aggregating

```python
# Default: Single business
async def get_today_tasks(business_id: BusinessID) -> list[Task]:
    return await repo.find_by_business(business_id)

# Explicit: All businesses
async def get_today_tasks_all_businesses() -> dict[BusinessID, list[Task]]:
    return {
        business: await get_today_tasks(business)
        for business in BusinessID
    }
```

### Analytics Across Businesses

**Problem**: Weekly analytics for all businesses

**Solution**:
- Analyze each business separately first
- Then aggregate results
- Never mix raw data

```python
async def weekly_analytics() -> WeeklyReport:
    # Analyze each business separately
    inventum_stats = await analyze_business(BusinessID.INVENTUM)
    lab_stats = await analyze_business(BusinessID.LAB)
    rd_stats = await analyze_business(BusinessID.R_AND_D)
    trade_stats = await analyze_business(BusinessID.TRADE)
    
    # Aggregate results (not raw data)
    return WeeklyReport(
        per_business={
            "inventum": inventum_stats,
            "lab": lab_stats,
            "r&d": rd_stats,
            "trade": trade_stats
        },
        totals=aggregate_stats([inventum_stats, lab_stats, rd_stats, trade_stats])
    )
```

---

## Consequences

### Positive
- ✅ **No context contamination** - Each business stays pure
- ✅ **Accurate RAG results** - Time estimates match business reality
- ✅ **Clear semantics** - No ambiguity in "диагностика"
- ✅ **Testable** - Can verify isolation
- ✅ **Fail-fast** - Errors instead of silent bugs
- ✅ **Scalable** - Easy to add 5th business
- ✅ **Debuggable** - Clear which business context

### Negative
- ⚠️ **More code** - Validation at multiple levels
- ⚠️ **Stricter constraints** - Can't be lazy
- ⚠️ **Cross-business queries harder** - Must be explicit

### Mitigation
- **Code generation**: Use templates for repository methods
- **Linting**: Custom rules to detect missing business_id
- **Documentation**: Clear examples in .cursorrules

---

## Validation Criteria

Will be considered successful if:
- [ ] 100% of RAG searches include business_id filter
- [ ] 0 cross-business contamination bugs in testing
- [ ] Time estimate accuracy improves within-business
- [ ] User never sees "wrong context" suggestions
- [ ] All integration tests pass isolation checks

---

## Critical Reminders

⚠️ **FOR ALL DEVELOPERS**:

1. **NEVER** do vector search without business_id filter
2. **ALWAYS** validate business_id is present
3. **ALWAYS** include business context in AI prompts
4. **TEST** isolation in integration tests
5. **ASSERT** business_id matches in RAG results

This is not optional - it's a **fundamental architectural constraint**.

---

## References

- Project Brief: `docs/00-project-brief.md` (Business Isolation section)
- Planning: `planning/PROJECT_PLAN.md`
- Code Rules: `.cursorrules` (Business-Specific Rules section)

---

## Review History

- **2025-10-17**: Initial version - Strict isolation strategy accepted
- **Status**: ✅ Accepted and mandatory for all development

---

**Decision**: Strict business context isolation at all levels  
**Confidence**: Absolute (10/10)  
**Risk**: Critical if not followed, Low if followed  
**Impact**: Critical (affects all features)  
**Priority**: ⚠️ **HIGHEST** - Non-negotiable architectural constraint



