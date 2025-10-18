# ADR-004: RAG (Retrieval-Augmented Generation) Implementation Strategy

**Status**: ✅ Accepted  
**Date**: 2025-10-17  
**Deciders**: Константин (CEO), Development Team  
**Tags**: ai, rag, learning, self-improvement

---

## Context

Business Planner's key innovation is **self-learning time estimation**. When a user creates a task, the system should:

1. Find similar past tasks
2. Look at actual completion times
3. Provide increasingly accurate time estimates

**Example Learning Cycle**:
```
Week 1: User creates "Позвонить поставщику"
System: No history → estimates 30 min (default)
User completes in: 45 min

Week 2: User creates "Звонок новому поставщику"  
System: Finds similar task → estimates 45 min ✅
User completes in: 40 min

Week 3: User creates "Позвонить поставщику по контракту"
System: Finds 2 similar tasks → estimates 42 min (avg) ✅
```

**Over time**: 50% accuracy → 80% accuracy (project goal)

### The Challenge

Traditional keyword search won't work:
- "Позвонить поставщику" ≠ "Звонок поставщику" (exact match fails)
- "Diagnostic of equipment" ≠ "Диагностика фрезера" (semantic meaning same)
- Need to understand **meaning**, not just words

**Solution**: Use RAG (Retrieval-Augmented Generation) with vector embeddings.

---

## Decision

We will implement **RAG-based time estimation** using:
- **OpenAI text-embedding-3-small** for generating embeddings
- **pgvector** for storing and searching embeddings
- **Cosine similarity** for finding similar tasks
- **Strict business_id filtering** (per ADR-003)
- **Continuous learning** from actual completion times

---

## What is RAG?

**RAG** = Retrieval-Augmented Generation

### Traditional AI Approach (No Memory)
```
User: "Estimate time for task X"
AI: *generates estimate from general knowledge*
Result: Generic, not personalized
```

### RAG Approach (With Memory)
```
User: "Estimate time for task X"
System: 
  1. Convert task X to embedding (vector)
  2. Search for similar past tasks (vector similarity)
  3. Retrieve actual completion times
  4. AI uses this context to estimate
Result: Personalized, learns from history
```

### Example in Business Planner

```
New Task: "Ремонт фрезера для клиента Петрова"

1. Generate Embedding:
   [0.123, -0.456, 0.789, ...] (1536 dimensions)

2. Vector Search (cosine similarity):
   Task: "Ремонт фрезера Иванова" - similarity: 0.92 - actual: 2h
   Task: "Починить фрезер" - similarity: 0.89 - actual: 1.5h
   Task: "Диагностика фрезера" - similarity: 0.75 - actual: 1h
   
3. AI Context:
   "Similar repairs took 1.5-2 hours"
   
4. AI Estimates: 1h 45min ✅
```

---

## Alternatives Considered

### 1. Keyword Matching
**Description**: Traditional text search (SQL LIKE, full-text search)

**Pros**:
- ✅ Simple to implement
- ✅ Fast queries
- ✅ No ML dependencies

**Cons**:
- ❌ Misses semantic similarity
- ❌ "Позвонить" ≠ "Звонок" (different words, same meaning)
- ❌ No Russian language understanding
- ❌ Can't learn from variations

**Example Failure**:
```sql
SELECT * FROM tasks 
WHERE title ILIKE '%позвонить%'
-- Misses: "Звонок поставщику", "Связаться с поставщиком"
```

**Verdict**: ❌ **Rejected** - Too simplistic

---

### 2. Manual Categorization
**Description**: User manually tags tasks with categories

**Pros**:
- ✅ Explicit categories
- ✅ User controls grouping
- ✅ No AI needed

**Cons**:
- ❌ Extra user effort (defeats "voice-first" goal)
- ❌ User might forget to categorize
- ❌ Limited categories (can't capture nuance)
- ❌ No automatic learning

**Verdict**: ❌ **Rejected** - Too much manual work

---

### 3. Separate Vector Database (Pinecone, Weaviate)
**Description**: Use dedicated vector DB service

**Pros**:
- ✅ Optimized for vector search
- ✅ Better performance at scale
- ✅ Advanced features

**Cons**:
- ❌ Additional cost ($45+/month)
- ❌ Extra infrastructure complexity
- ❌ Network latency (external service)
- ❌ Another service to maintain
- ❌ Overkill for 300-500 tasks/month

**Cost Comparison**:
```
pgvector (in PostgreSQL): $0 extra (included in $6 Droplet)
Pinecone: $45/month minimum
Weaviate: $25/month minimum
```

**Verdict**: ❌ **Rejected** - Cost and complexity not justified

---

### 4. RAG with pgvector ⭐
**Description**: Use PostgreSQL with pgvector extension

**Pros**:
- ✅ **Cost-effective**: No extra cost ($0)
- ✅ **Simplicity**: All in one database
- ✅ **Fast enough**: < 100ms queries for our scale
- ✅ **Transactional**: Vector + metadata in same DB
- ✅ **No network latency**: Local to application
- ✅ **Mature**: PostgreSQL reliability
- ✅ **Scalable**: Handles 10K+ tasks easily

**Cons**:
- ⚠️ Not as optimized as specialized vector DBs
- ⚠️ Performance degrades at 100K+ vectors (not our scale)

**Our Scale**: 300-500 tasks/month = ~6,000 tasks/year
- pgvector handles this easily

**Verdict**: ✅ **Accepted** - Best fit for our needs

---

## Implementation Design

### 1. Embedding Generation

#### When to Generate Embeddings
```python
# Generate embedding when task is created
async def create_task(task_data: TaskCreate) -> Task:
    # Create task
    task = Task(**task_data.dict())
    
    # Generate embedding
    task.embedding = await generate_embedding(task.title)
    
    # Save to database (with embedding)
    await task_repo.create(task)
    
    return task
```

#### What to Embed
**Option A**: Title only
- Pro: Simple, fast
- Con: Might miss context

**Option B**: Title + Description
- Pro: More context
- Con: Longer text, higher cost

**Decision**: **Title only** (with option to add description later)
- Most tasks have descriptive titles
- User speaks title naturally
- Can extend if needed

#### Embedding Model
**Model**: `text-embedding-3-small`
- **Dimensions**: 1536
- **Cost**: $0.02 / 1M tokens
- **Speed**: ~100ms per embedding
- **Quality**: Excellent for Russian

**Cost Calculation** (300 tasks/month):
```
300 tasks × 10 tokens avg × $0.02 / 1M = $0.00006/month
Essentially free!
```

---

### 2. Vector Storage (pgvector)

#### Schema
```sql
-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Tasks table with embedding column
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    business_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    estimated_duration INTEGER,  -- in minutes
    actual_duration INTEGER,     -- learned from completion
    embedding vector(1536),      -- OpenAI embedding
    created_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP,
    -- ... other fields
);

-- Vector index for fast similarity search
-- Using HNSW (Hierarchical Navigable Small World)
CREATE INDEX idx_tasks_embedding_hnsw 
ON tasks 
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

-- Composite index for business-filtered search
CREATE INDEX idx_tasks_business_embedding
ON tasks (business_id, embedding)
WHERE embedding IS NOT NULL;
```

#### Index Types

**Option 1: IVFFlat** (Inverted File Index)
- Faster build time
- Good for < 100K vectors
- Less memory

**Option 2: HNSW** (Hierarchical Navigable Small World) ⭐
- Faster search
- Better recall
- More memory (acceptable for our scale)

**Decision**: **HNSW** - Better search performance

---

### 3. Similarity Search

#### Search Query
```python
async def find_similar_tasks(
    task: Task,
    business_id: int,  # MANDATORY (ADR-003)
    top_k: int = 5,
    similarity_threshold: float = 0.7
) -> list[Task]:
    """Find similar tasks using vector similarity.
    
    Args:
        task: Task with embedding
        business_id: Business context for isolation
        top_k: Number of results to return
        similarity_threshold: Minimum similarity score (0-1)
        
    Returns:
        List of similar tasks, sorted by similarity
    """
    
    # SQL with pgvector
    query = """
        SELECT 
            id,
            title,
            actual_duration,
            completed_at,
            1 - (embedding <=> $1) as similarity
        FROM tasks
        WHERE 
            business_id = $2
            AND embedding IS NOT NULL
            AND actual_duration IS NOT NULL  -- Only completed tasks
            AND 1 - (embedding <=> $1) >= $3  -- Similarity threshold
        ORDER BY embedding <=> $1  -- Cosine distance
        LIMIT $4
    """
    
    results = await db.fetch_all(
        query,
        task.embedding,
        business_id,
        similarity_threshold,
        top_k
    )
    
    return [Task(**row) for row in results]
```

#### Similarity Metrics

**Cosine Distance**: `embedding <=> other_embedding`
- Range: 0 (identical) to 2 (opposite)
- Similarity = 1 - distance
- Best for text embeddings

**L2 Distance**: `embedding <-> other_embedding`
- Euclidean distance
- Less common for text

**Inner Product**: `embedding <#> other_embedding`
- Dot product
- Useful for normalized vectors

**Decision**: **Cosine Distance** (standard for text embeddings)

---

### 4. Time Estimation with RAG

#### LangGraph Node
```python
from langgraph.graph import StateGraph

async def estimate_time_with_rag_node(state: VoiceTaskState) -> VoiceTaskState:
    """Estimate task duration using RAG."""
    
    task = state["parsed_task"]
    
    # 1. Find similar past tasks
    similar_tasks = await find_similar_tasks(
        task=task,
        business_id=task.business_id,
        top_k=5,
        similarity_threshold=0.7
    )
    
    if not similar_tasks:
        # No similar tasks, use default
        logger.info("No similar tasks found, using default estimate")
        estimated_duration = DEFAULT_TASK_DURATION  # 60 minutes
        confidence = "low"
    else:
        # 2. Build context for GPT-5 Nano
        context = build_rag_context(task, similar_tasks)
        
        # 3. Ask GPT-5 Nano to estimate
        estimated_duration = await gpt_estimate_time(context)
        confidence = "high"
    
    # 4. Update state
    return {
        **state,
        "estimated_duration": estimated_duration,
        "similar_tasks": similar_tasks,
        "confidence": confidence
    }


def build_rag_context(task: Task, similar_tasks: list[Task]) -> str:
    """Build context for GPT-5 Nano."""
    
    similar_info = []
    for sim_task in similar_tasks:
        similar_info.append(
            f"- \"{sim_task.title}\" "
            f"(similarity: {sim_task.similarity:.0%}) "
            f"→ actual: {sim_task.actual_duration} min"
        )
    
    return f"""
Business: {task.business_name}

New task: "{task.title}"

Similar past tasks in {task.business_name}:
{chr(10).join(similar_info)}

Based on these similar tasks, estimate the duration in minutes.
Consider:
- Task similarity (higher similarity = more relevant)
- Actual completion times from history
- Business context ({task.business_name})

Return ONLY a number (minutes).
"""


async def gpt_estimate_time(context: str) -> int:
    """Use GPT-5 Nano to estimate time."""
    
    response = await openai.chat.completions.create(
        model="gpt-5-nano",
        messages=[
            {
                "role": "system",
                "content": "You estimate task duration in minutes based on historical data."
            },
            {
                "role": "user", 
                "content": context
            }
        ],
        temperature=0.3,  # Low temperature for consistency
        max_tokens=10
    )
    
    # Parse response
    duration_text = response.choices[0].message.content.strip()
    duration = int(duration_text)
    
    # Sanity check
    if duration < 1 or duration > 480:  # 1 min to 8 hours
        logger.warning(f"Unusual duration: {duration}, using default")
        return 60
    
    return duration
```

---

### 5. Learning Loop (Feedback)

#### When Task is Completed
```python
async def complete_task(
    task_id: int,
    actual_duration: int
) -> Task:
    """Mark task as complete and learn from actual duration."""
    
    # 1. Update task with actual duration
    task = await task_repo.get_by_id(task_id)
    task.actual_duration = actual_duration
    task.completed_at = datetime.now()
    
    await task_repo.update(task)
    
    # 2. Log for analytics
    logger.info(
        "task_completed_learning",
        task_id=task_id,
        business_id=task.business_id,
        estimated=task.estimated_duration,
        actual=actual_duration,
        accuracy=calculate_accuracy(task.estimated_duration, actual_duration)
    )
    
    # 3. Future searches will now include this task
    # (No explicit retraining needed - RAG searches in real-time)
    
    return task


def calculate_accuracy(estimated: int, actual: int) -> float:
    """Calculate estimation accuracy percentage."""
    if estimated == 0:
        return 0.0
    
    error = abs(estimated - actual) / actual
    accuracy = max(0, 1 - error)
    return accuracy
```

#### How Learning Works

**Week 1**: No history
```python
find_similar_tasks("Позвонить поставщику")
→ No results
→ Use default: 60 min
```

**Week 2**: After first task completed (actual: 45 min)
```python
find_similar_tasks("Звонок поставщику")
→ Finds: "Позвонить поставщику" (similarity: 0.89, actual: 45 min)
→ GPT-5 Nano: "Based on similar task (45 min), estimate: 45 min"
```

**Week 4**: After multiple similar tasks
```python
find_similar_tasks("Позвонить новому поставщику")
→ Finds 3 similar:
   - "Позвонить поставщику" (sim: 0.92, actual: 45 min)
   - "Звонок поставщику" (sim: 0.89, actual: 40 min)
   - "Связаться с поставщиком" (sim: 0.85, actual: 50 min)
→ GPT-5 Nano: "Average of similar: 45 min, estimate: 45 min"
```

**Result**: Estimates improve from 50% → 80% accuracy over time ✅

---

## Configuration Parameters

### Tunable Values
```python
class RAGConfig:
    # Embedding
    EMBEDDING_MODEL = "text-embedding-3-small"
    EMBEDDING_DIMENSIONS = 1536
    
    # Search
    TOP_K = 5  # Number of similar tasks to retrieve
    SIMILARITY_THRESHOLD = 0.7  # Minimum similarity (0-1)
    MIN_TASKS_FOR_RAG = 1  # Minimum history needed
    
    # Estimation
    DEFAULT_DURATION = 60  # minutes (when no history)
    MIN_DURATION = 1  # minutes
    MAX_DURATION = 480  # minutes (8 hours)
    
    # Index
    HNSW_M = 16  # HNSW parameter (higher = better recall)
    HNSW_EF_CONSTRUCTION = 64  # HNSW build quality
```

### Performance Expectations

| Scale | Search Time | Accuracy (Cosine) |
|-------|-------------|-------------------|
| 100 tasks | < 10ms | 99%+ |
| 1,000 tasks | < 50ms | 98%+ |
| 10,000 tasks | < 100ms | 95%+ |
| 100,000 tasks | < 500ms | 90%+ |

**Our scale**: ~500 tasks/month = 6,000/year → **< 100ms** ✅

---

## Business Isolation in RAG

**Critical** (per ADR-003): RAG MUST filter by business_id

```python
# ✅ CORRECT: Always filter by business
similar_tasks = await find_similar_tasks(
    task=task,
    business_id=task.business_id,  # MANDATORY
    top_k=5
)

# ❌ WRONG: Cross-business contamination
similar_tasks = await db.fetch_all(
    "SELECT * FROM tasks ORDER BY embedding <=> $1 LIMIT 5",
    task.embedding
)
# This violates ADR-003!
```

**Why Critical**:
- "Диагностика" in Inventum (equipment) ≠ "Диагностика" in R&D (prototype)
- Different durations, different contexts
- Must stay isolated

---

## Testing Strategy

### Unit Tests
```python
async def test_embedding_generation():
    """Test embedding generation."""
    embedding = await generate_embedding("Позвонить поставщику")
    assert len(embedding) == 1536
    assert all(isinstance(x, float) for x in embedding)


async def test_similar_tasks_returns_same_business():
    """Test RAG respects business isolation."""
    # Create tasks in different businesses
    inventum_task = await create_task(
        "Ремонт фрезера", business_id=BusinessID.INVENTUM
    )
    rd_task = await create_task(
        "Ремонт прототипа", business_id=BusinessID.R_AND_D
    )
    
    # Search from Inventum
    similar = await find_similar_tasks(
        inventum_task, business_id=BusinessID.INVENTUM
    )
    
    # Verify: Only Inventum tasks
    for task in similar:
        assert task.business_id == BusinessID.INVENTUM
```

### Integration Tests
```python
async def test_rag_learning_cycle():
    """Test that RAG improves over time."""
    
    # Week 1: No history
    task1 = await create_task("Позвонить поставщику")
    assert task1.estimated_duration == 60  # Default
    
    # Complete with actual time
    await complete_task(task1.id, actual_duration=45)
    
    # Week 2: With history
    task2 = await create_task("Звонок поставщику")
    # Should use RAG now
    assert 40 <= task2.estimated_duration <= 50  # Near 45 min
```

---

## Monitoring & Metrics

### Key Metrics
```python
# Estimation accuracy
accuracy = abs(estimated - actual) / actual
# Target: 50% → 80% over 1 month

# RAG usage rate  
rag_usage = tasks_with_similar / total_tasks
# Target: > 60% after 1 month

# Average similarity score
avg_similarity = mean(similarity_scores)
# Target: > 0.75

# Search performance
search_time_p95 = percentile_95(search_times)
# Target: < 100ms
```

### Logging
```python
logger.info(
    "rag_estimation",
    task_id=task.id,
    business_id=task.business_id,
    similar_tasks_found=len(similar_tasks),
    avg_similarity=avg_similarity,
    estimated_duration=estimated_duration,
    search_time_ms=search_time_ms
)
```

---

## Consequences

### Positive
- ✅ **Self-improving**: Accuracy increases over time
- ✅ **Personalized**: Based on user's actual history
- ✅ **Cost-effective**: $0 infrastructure, $0.0006/month embeddings
- ✅ **Fast**: < 100ms searches
- ✅ **Semantic**: Understands meaning, not just keywords
- ✅ **Business-isolated**: Respects ADR-003
- ✅ **Transparent**: User sees why estimate was given

### Negative
- ⚠️ **Cold start**: First tasks have no history (use defaults)
- ⚠️ **Data quality**: Bad actual_duration affects learning
- ⚠️ **Complexity**: More moving parts than simple averages

### Mitigation
- **Cold start**: Acceptable, improves quickly (50% accuracy goal start)
- **Data quality**: Validate actual_duration input (1-480 min range)
- **Complexity**: Worth it for 50% → 80% accuracy improvement

---

## Success Criteria

Will be considered successful if:
- [ ] Estimation accuracy improves 50% → 80% over 1 month
- [ ] Search queries < 100ms (p95)
- [ ] RAG used in > 60% of tasks after 1 month
- [ ] Business isolation maintained 100%
- [ ] User satisfaction with estimates

---

## References

- [pgvector Documentation](https://github.com/pgvector/pgvector)
- [OpenAI Embeddings Guide](https://platform.openai.com/docs/guides/embeddings)
- [HNSW Algorithm Paper](https://arxiv.org/abs/1603.09320)
- ADR-003: Business Context Isolation
- Project Brief: `docs/00-project-brief.md`

---

## Review History

- **2025-10-17**: Initial version - RAG with pgvector strategy accepted
- **Status**: ✅ Accepted and ready for implementation

---

**Decision**: Implement RAG using pgvector for time estimation  
**Confidence**: High (9/10)  
**Risk**: Low (proven technology)  
**Impact**: High (core feature - self-learning)  
**Expected Improvement**: 50% → 80% accuracy over 1 month



