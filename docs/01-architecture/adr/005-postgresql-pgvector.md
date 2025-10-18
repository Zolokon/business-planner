# ADR-005: Use PostgreSQL with pgvector Extension

**Status**: ✅ Accepted  
**Date**: 2025-10-17  
**Deciders**: Константин (CEO), Development Team  
**Tags**: database, infrastructure, vectors, cost-optimization

---

## Context

Business Planner needs a database that supports:

### Core Requirements
1. **Relational data** - Users, tasks, projects, businesses, team members
2. **Vector embeddings** - For RAG similarity search (ADR-004)
3. **Full-text search** - For task titles and descriptions (Russian language)
4. **ACID transactions** - Data integrity
5. **Async support** - For FastAPI async/await
6. **Cost-effective** - Budget constraint ($6/month Droplet)
7. **Reliable** - Battle-tested technology

### Scale
- **Tasks**: ~500/month = ~6,000/year
- **Users**: 1 (Константин)
- **Team members**: 8 people
- **Businesses**: 4 (fixed)
- **Vector operations**: ~500 searches/month

### Critical Constraint
Must fit within **$6/month Digital Ocean Droplet** (ADR-006).

---

## Decision

We will use **PostgreSQL 15** with **pgvector extension** as our primary database.

No separate vector database. Everything in one PostgreSQL instance.

---

## Alternatives Considered

### 1. PostgreSQL + Separate Vector DB (Pinecone)
**Description**: PostgreSQL for data, Pinecone for vectors

**Pros**:
- ✅ Specialized vector search (optimized)
- ✅ Better performance at massive scale (1M+ vectors)
- ✅ Advanced features (namespaces, metadata filtering)

**Cons**:
- ❌ **Cost**: $45/month minimum (7.5x our infrastructure budget!)
- ❌ **Complexity**: Two databases to manage
- ❌ **Sync issues**: Need to keep vector DB in sync with PostgreSQL
- ❌ **Network latency**: External API calls
- ❌ **Data duplication**: Same data in two places
- ❌ **Overkill**: Optimized for millions of vectors (we have thousands)

**Cost Comparison**:
```
PostgreSQL + pgvector: $0 extra (included in $6 Droplet)
PostgreSQL + Pinecone: $6 + $45 = $51/month
Difference: $45/month = $540/year
```

**Verdict**: ❌ **Rejected** - Cost prohibitive, unnecessary complexity

---

### 2. PostgreSQL + Weaviate
**Description**: PostgreSQL for data, Weaviate for vectors

**Pros**:
- ✅ Open-source vector database
- ✅ Good performance
- ✅ GraphQL API

**Cons**:
- ❌ **Cost**: Requires separate server (~$10-25/month)
- ❌ **Complexity**: Another service to deploy and manage
- ❌ **Resource usage**: Needs dedicated memory (500MB+)
- ❌ **Doesn't fit in $6 Droplet**: Not enough resources for both
- ❌ **Sync complexity**: Same as Pinecone

**Verdict**: ❌ **Rejected** - Doesn't fit budget, adds complexity

---

### 3. MongoDB with Vector Search
**Description**: Use MongoDB Atlas with vector search feature

**Pros**:
- ✅ Document database (flexible schema)
- ✅ Built-in vector search (recently added)
- ✅ Horizontal scaling

**Cons**:
- ❌ **Cost**: Atlas starts at $9/month (over budget)
- ❌ **Less mature**: Vector search is newer
- ❌ **No ACID for multi-document**: Weaker transactions
- ❌ **Learning curve**: Different query language
- ❌ **Overkill**: Designed for massive scale
- ❌ **Russian full-text**: Less robust than PostgreSQL

**Verdict**: ❌ **Rejected** - Cost and maturity concerns

---

### 4. SQLite with sqlite-vss
**Description**: Lightweight SQLite with vector extension

**Pros**:
- ✅ Ultra-lightweight (no server)
- ✅ Zero cost
- ✅ Simple deployment (single file)

**Cons**:
- ❌ **No concurrent writes**: Single writer limitation
- ❌ **No async support**: Poor fit for FastAPI async
- ❌ **Limited scalability**: Not designed for web apps
- ❌ **No replication**: Single point of failure
- ❌ **Production concerns**: Not recommended for web services

**Verdict**: ❌ **Rejected** - Not suitable for web application

---

### 5. PostgreSQL 15 + pgvector ⭐
**Description**: Single PostgreSQL instance with pgvector extension

**Pros**:
- ✅ **Zero extra cost**: Included in $6 Droplet
- ✅ **Single database**: No sync issues
- ✅ **Transactional**: Vector + metadata in same transaction
- ✅ **Mature**: PostgreSQL is battle-tested (30+ years)
- ✅ **Async support**: asyncpg library excellent
- ✅ **Full-text search**: Built-in, great for Russian
- ✅ **Rich ecosystem**: Tools, extensions, expertise
- ✅ **Scalable**: Handles 100K+ vectors easily
- ✅ **Fast enough**: < 100ms for our scale
- ✅ **Reliable**: ACID transactions, replication
- ✅ **pgvector mature**: Used in production by many companies

**Cons**:
- ⚠️ Not as fast as specialized vector DBs at 1M+ scale
  - (But we have ~6K vectors, not 1M)
- ⚠️ Vector search not as optimized as Pinecone
  - (But < 100ms is fast enough for us)

**Performance** at our scale (6,000 vectors):
- Search time: **< 50ms** (with HNSW index)
- Insert time: **< 10ms**
- Total storage: **< 100MB** (all data + vectors)

**Verdict**: ✅ **Accepted** - Perfect fit for our needs and budget

---

## Detailed Rationale

### 1. Cost Efficiency 💰

#### Infrastructure Costs
```
Option A: PostgreSQL + pgvector
Droplet: $6/month
Database: $0 (included)
Total: $6/month ✅

Option B: PostgreSQL + Pinecone
Droplet: $6/month
Database: $0 (included)
Pinecone: $45/month
Total: $51/month ❌

Option C: Managed PostgreSQL + pgvector (Digital Ocean)
Managed DB: $15/month
Droplet: $6/month
Total: $21/month ⚠️

Savings: $6 vs $51 = $45/month = $540/year
```

**Winner**: PostgreSQL + pgvector saves **$540/year** vs Pinecone!

---

### 2. Simplicity 🎯

#### Single Database
```python
# ✅ SIMPLE: One database connection
async with db.transaction():
    # Create task
    task = await tasks.insert(task_data)
    
    # Generate embedding
    embedding = await generate_embedding(task.title)
    
    # Store embedding (same transaction!)
    await tasks.update(task.id, embedding=embedding)
    
    # Atomic: Both succeed or both fail
```

#### vs. Dual Database
```python
# ❌ COMPLEX: Two databases to sync
try:
    # Create task in PostgreSQL
    task = await pg_tasks.insert(task_data)
    
    try:
        # Generate embedding
        embedding = await generate_embedding(task.title)
        
        # Store in Pinecone
        await pinecone.upsert(task.id, embedding)
        
    except PineconeError:
        # Rollback PostgreSQL? Manual cleanup!
        await pg_tasks.delete(task.id)
        raise
        
except Exception:
    # Complex error handling
    pass
```

**Winner**: Single database = simpler, fewer bugs

---

### 3. Performance at Our Scale ⚡

#### Our Workload
- **Inserts**: ~500 tasks/month = 0.02 tasks/minute (very low)
- **Vector searches**: ~500/month = 0.02 searches/minute
- **Data size**: 6,000 tasks/year × 10KB = ~60MB/year

#### pgvector Performance Benchmarks

| Vector Count | Search Time (HNSW) | Recall |
|--------------|-------------------|--------|
| 1,000 | < 10ms | 99% |
| 10,000 | < 50ms | 98% |
| 100,000 | < 100ms | 95% |
| 1,000,000 | < 500ms | 90% |

**Our scale**: 6,000 vectors → **< 50ms** ✅

**Comparison**:
- Pinecone: ~20ms (2.5x faster)
- pgvector: ~50ms

**Is 30ms difference worth $540/year?** NO! ❌

---

### 4. Transactional Integrity 🔒

#### Atomic Operations
```sql
BEGIN;
    -- Insert task
    INSERT INTO tasks (title, business_id, user_id) 
    VALUES ('Позвонить поставщику', 4, 1)
    RETURNING id;
    
    -- Update with embedding (same transaction)
    UPDATE tasks 
    SET embedding = vector_from_text('Позвонить поставщику')
    WHERE id = 123;
COMMIT;
```

**Benefits**:
- ✅ Task + embedding created atomically
- ✅ No orphaned data
- ✅ Rollback works for both
- ✅ Consistent state guaranteed

**With separate vector DB**: Manual sync, race conditions, complex error handling

---

### 5. Russian Full-Text Search 🇷🇺

PostgreSQL has excellent Russian support:

```sql
-- Create full-text search index for Russian
CREATE INDEX idx_tasks_title_fts 
ON tasks 
USING gin(to_tsvector('russian', title));

-- Search in Russian
SELECT * FROM tasks
WHERE to_tsvector('russian', title) @@ to_tsquery('russian', 'ремонт & фрезер')
ORDER BY ts_rank(to_tsvector('russian', title), to_tsquery('russian', 'ремонт & фрезер')) DESC;
```

**Supports**:
- Stemming (ремонт, ремонтировать → same root)
- Stop words (и, в, на filtered)
- Morphology (падежи, склонения)

**Alternative**: Elasticsearch
- Good but overkill for our scale
- Additional $10-15/month
- More complexity

**Winner**: PostgreSQL built-in full-text search

---

### 6. pgvector Maturity 🛡️

pgvector is **production-ready**:

**Used by**:
- Supabase (vector database feature)
- Timescale (time-series + vectors)
- Many startups and enterprises

**Stats**:
- 6,000+ GitHub stars
- Active development (PostgreSQL team support)
- Used in production at scale

**Features**:
- HNSW index (state-of-the-art)
- IVFFlat index (faster build)
- Multiple distance metrics (cosine, L2, inner product)
- Exact + approximate search

**Reliability**: Backed by PostgreSQL's ACID guarantees

---

### 7. Development Experience 👨‍💻

#### Excellent Async Support
```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

# asyncpg driver (fastest Python PostgreSQL driver)
engine = create_async_engine(
    "postgresql+asyncpg://user:pass@localhost/planner"
)

async def get_similar_tasks(embedding: list[float]) -> list[Task]:
    async with AsyncSession(engine) as session:
        result = await session.execute(
            select(Task)
            .order_by(Task.embedding.cosine_distance(embedding))
            .limit(5)
        )
        return result.scalars().all()
```

**Benefits**:
- ✅ Native async support (perfect for FastAPI)
- ✅ Fast (asyncpg is fastest Python driver)
- ✅ Type-safe (SQLAlchemy 2.0)
- ✅ Well-documented

---

## Implementation Details

### 1. Setup

#### Install pgvector Extension
```sql
-- On Droplet (one-time setup)
CREATE EXTENSION IF NOT EXISTS vector;

-- Verify
SELECT * FROM pg_extension WHERE extname = 'vector';
```

#### Schema
```sql
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    business_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    assigned_to VARCHAR(100),
    
    -- Time tracking
    estimated_duration INTEGER,  -- minutes
    actual_duration INTEGER,     -- minutes (learned)
    
    -- Status
    status VARCHAR(20) DEFAULT 'open',
    priority INTEGER CHECK (priority BETWEEN 1 AND 4),
    
    -- Dates
    deadline TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    
    -- Vector embedding (1536 dimensions for text-embedding-3-small)
    embedding vector(1536),
    
    -- Foreign keys
    CONSTRAINT fk_business FOREIGN KEY (business_id) 
        REFERENCES businesses(id),
    CONSTRAINT fk_user FOREIGN KEY (user_id) 
        REFERENCES users(id)
);

-- Indexes
CREATE INDEX idx_tasks_business ON tasks(business_id);
CREATE INDEX idx_tasks_user ON tasks(user_id);
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_deadline ON tasks(deadline);

-- Vector index (HNSW for best search performance)
CREATE INDEX idx_tasks_embedding 
ON tasks 
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

-- Full-text search index
CREATE INDEX idx_tasks_title_fts 
ON tasks 
USING gin(to_tsvector('russian', title));
```

---

### 2. Configuration

#### PostgreSQL Settings for Vectors
```ini
# postgresql.conf

# Memory
shared_buffers = 256MB          # For Droplet (1GB RAM)
effective_cache_size = 768MB    # 75% of RAM
work_mem = 4MB                  # Per operation

# Vector-specific
max_parallel_workers_per_gather = 2
maintenance_work_mem = 64MB     # For index building

# Connections
max_connections = 20            # Low (single user)
```

#### Connection Pool
```python
# SQLAlchemy async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_size=5,          # Small pool (low concurrency)
    max_overflow=10,      # Can burst to 15 connections
    pool_pre_ping=True,   # Check connection health
    pool_recycle=3600     # Recycle after 1 hour
)
```

---

### 3. Vector Operations

#### Insert with Embedding
```python
async def create_task_with_embedding(
    task_data: TaskCreate,
    session: AsyncSession
) -> Task:
    # Generate embedding
    embedding = await generate_embedding(task_data.title)
    
    # Create task
    task = Task(
        **task_data.dict(),
        embedding=embedding
    )
    
    session.add(task)
    await session.commit()
    await session.refresh(task)
    
    return task
```

#### Similarity Search
```python
from sqlalchemy import select, func

async def find_similar_tasks(
    embedding: list[float],
    business_id: int,
    session: AsyncSession,
    limit: int = 5
) -> list[Task]:
    # Cosine distance query
    stmt = (
        select(
            Task,
            (1 - Task.embedding.cosine_distance(embedding)).label('similarity')
        )
        .where(Task.business_id == business_id)
        .where(Task.embedding.isnot(None))
        .where(Task.actual_duration.isnot(None))  # Only completed
        .order_by(Task.embedding.cosine_distance(embedding))
        .limit(limit)
    )
    
    result = await session.execute(stmt)
    return result.all()
```

---

### 4. Backup Strategy

#### Automated Backups
```bash
# Daily backup script
#!/bin/bash
BACKUP_DIR="/var/backups/postgres"
DATE=$(date +%Y%m%d_%H%M%S)

# Dump database
pg_dump -U planner -d planner -F c -f "$BACKUP_DIR/planner_$DATE.dump"

# Keep last 7 days
find $BACKUP_DIR -name "planner_*.dump" -mtime +7 -delete

# Upload to Digital Ocean Spaces (optional)
s3cmd put "$BACKUP_DIR/planner_$DATE.dump" s3://planner-backups/
```

#### Restore
```bash
# Restore from backup
pg_restore -U planner -d planner -c planner_20251017.dump
```

---

## Scaling Strategy

### Current Scale (Year 1)
- **Tasks**: 6,000
- **Storage**: < 100MB
- **Performance**: < 50ms searches
- **Infrastructure**: $6 Droplet ✅

### Growth (Year 2-3)
- **Tasks**: 20,000
- **Storage**: ~300MB
- **Performance**: < 100ms searches (still good)
- **Infrastructure**: Same $6 Droplet ✅

### If Outgrow (Year 4+)
- **Tasks**: 100,000+
- **Storage**: ~1.5GB
- **Options**:
  1. Upgrade Droplet ($12/month) - doubles resources
  2. Add read replicas for scaling reads
  3. Partition large tables by business
  4. Consider managed PostgreSQL ($15/month)

**Critical**: Don't need to decide now, can scale incrementally

---

## Monitoring

### Key Metrics
```sql
-- Vector index size
SELECT pg_size_pretty(pg_relation_size('idx_tasks_embedding'));

-- Query performance
EXPLAIN ANALYZE
SELECT * FROM tasks
ORDER BY embedding <=> '[0.1, 0.2, ...]'
LIMIT 5;

-- Index statistics
SELECT * FROM pg_stat_user_indexes 
WHERE indexrelname LIKE '%embedding%';
```

### Alerts
- Query time > 200ms (investigate)
- Database size > 800MB (70% of 1GB Droplet)
- Connection pool exhausted
- Failed queries > 1%

---

## Consequences

### Positive
- ✅ **Cost savings**: $540/year vs separate vector DB
- ✅ **Simplicity**: One database, one backup, one connection pool
- ✅ **Transactional**: ACID guarantees for vector + data
- ✅ **Fast enough**: < 100ms for our scale
- ✅ **Mature**: 30+ years of PostgreSQL reliability
- ✅ **Russian support**: Excellent full-text search
- ✅ **Async**: Perfect for FastAPI
- ✅ **Scalable**: Can handle 10x growth easily

### Negative
- ⚠️ **Not specialized**: Slower than dedicated vector DBs at massive scale
- ⚠️ **Single point**: Database is critical (but we have backups)
- ⚠️ **Resource sharing**: Vectors + data compete for memory

### Mitigation
- **Performance**: Our scale doesn't need specialized DB
- **Single point**: Daily backups + can add replicas if needed
- **Resources**: $6 Droplet has enough for our scale (can upgrade)

---

## Success Criteria

Will be considered successful if:
- [ ] Vector search queries < 100ms (p95)
- [ ] Database fits in $6 Droplet for Year 1
- [ ] Zero data loss or corruption
- [ ] Can handle 500 tasks/month consistently
- [ ] Backup/restore works reliably

---

## References

- [pgvector GitHub](https://github.com/pgvector/pgvector)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [SQLAlchemy Async](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- ADR-004: RAG Strategy
- ADR-006: Digital Ocean Droplet

---

## Review History

- **2025-10-17**: Initial version - PostgreSQL + pgvector accepted
- **Status**: ✅ Accepted and ready for implementation

---

**Decision**: Use PostgreSQL 15 with pgvector extension  
**Confidence**: Very High (10/10)  
**Risk**: Very Low (proven technology)  
**Impact**: High (core infrastructure)  
**Cost Savings**: $540/year vs alternatives  
**Performance**: More than adequate for our scale



