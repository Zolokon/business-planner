# Database Indexes Strategy - Business Planner

> **Index optimization for performance**  
> **Created**: 2025-10-17  
> **Database**: PostgreSQL 15 + pgvector

---

## 🎯 Indexing Philosophy

### Goals
1. **Fast queries** - All common queries < 100ms
2. **Minimal overhead** - Don't over-index (slows writes)
3. **RAG optimized** - Vector search < 50ms
4. **Business isolation** - Support filtered queries (ADR-003)

### Principles
- Index **foreign keys** (JOIN performance)
- Index **WHERE clauses** (filter performance)
- Index **ORDER BY columns** (sort performance)
- **Composite indexes** for common query patterns
- **Partial indexes** for filtered queries

---

## 📊 Index Inventory

### Summary

| Table | Total Indexes | Types |
|-------|---------------|-------|
| **users** | 3 | PK, UK, B-tree |
| **businesses** | 2 | PK, UK |
| **members** | 4 | PK, B-tree, GIN |
| **projects** | 5 | PK, B-tree, Composite |
| **tasks** | 13 | PK, B-tree, HNSW, GIN, Composite |
| **task_history** | 5 | PK, B-tree |
| **Total** | **32** | - |

---

## 🔍 Critical Indexes (MUST HAVE)

### 1. Vector Index (tasks.embedding) ⭐⭐⭐

**Most Critical Index** - Enables RAG (ADR-004)

```sql
CREATE INDEX idx_tasks_embedding_hnsw 
ON tasks 
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);
```

**Why HNSW**:
- Faster search than IVFFlat (< 50ms)
- Better recall (98%+)
- Worth the memory cost

**Parameters**:
- `m = 16` - Number of connections per layer (higher = better recall, more memory)
- `ef_construction = 64` - Build quality (higher = better index, slower build)

**Alternative**: IVFFlat (faster build, slower search)
```sql
-- Not using this, but for reference:
CREATE INDEX idx_tasks_embedding_ivfflat 
ON tasks 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);
```

**Performance**:
- **HNSW**: Search ~30-50ms, Build ~5 min for 10K vectors
- **IVFFlat**: Search ~100-200ms, Build ~1 min

**Choice**: HNSW (better for frequent searches)

---

### 2. Business Isolation Index (tasks.business_id) ⭐⭐⭐

**Critical for ADR-003** - Business context isolation

```sql
CREATE INDEX idx_tasks_business ON tasks(business_id);
```

**Used in**:
- Every RAG search (with embedding)
- /today command (filter by business)
- Analytics queries
- Task listing

**Cardinality**: 4 values (low) but critical for filtering

---

### 3. Status Index (tasks.status) ⭐⭐

**Frequently filtered**

```sql
CREATE INDEX idx_tasks_status ON tasks(status);
```

**Used in**:
- Get open tasks
- Get completed tasks
- Dashboard queries

**Cardinality**: 3 values (open, done, archived)

---

## 📈 Composite Indexes (Query Patterns)

### 1. User + Business + Status (Most Common)

```sql
CREATE INDEX idx_tasks_user_business_status 
ON tasks(user_id, business_id, status);
```

**Query Pattern**:
```sql
-- Get user's open tasks for specific business
SELECT * FROM tasks
WHERE user_id = 1
  AND business_id = 2
  AND status = 'open';
```

**Frequency**: Every /today command, very common

---

### 2. Business + Status + Deadline (Daily Planning)

```sql
CREATE INDEX idx_tasks_business_status_deadline 
ON tasks(business_id, status, deadline) 
WHERE status = 'open';
```

**Query Pattern**:
```sql
-- Get today's open tasks for business
SELECT * FROM tasks
WHERE business_id = 1
  AND status = 'open'
  AND deadline::date = CURRENT_DATE
ORDER BY deadline;
```

**Why Partial Index**: Only index open tasks (75% of table excluded)

**Benefits**:
- Smaller index
- Faster queries
- Less maintenance

---

### 3. User + Completed (Analytics)

```sql
CREATE INDEX idx_tasks_user_completed 
ON tasks(user_id, completed_at, status) 
WHERE status = 'done';
```

**Query Pattern**:
```sql
-- Weekly analytics
SELECT * FROM tasks
WHERE user_id = 1
  AND status = 'done'
  AND completed_at >= NOW() - INTERVAL '7 days';
```

**Why Partial**: Only completed tasks need this index

---

### 4. Business + Learning (RAG Filter)

```sql
CREATE INDEX idx_tasks_business_completed_embedding
ON tasks(business_id, actual_duration)
WHERE embedding IS NOT NULL AND actual_duration IS NOT NULL;
```

**Query Pattern**:
```sql
-- Find similar tasks with actual duration (for learning)
SELECT * FROM tasks
WHERE business_id = 1
  AND embedding IS NOT NULL
  AND actual_duration IS NOT NULL
ORDER BY embedding <=> $1
LIMIT 5;
```

**Why Important**: Combines business isolation + RAG + learning data

---

## 🚀 Array Indexes (members.business_ids)

### GIN Index for Array Search

```sql
CREATE INDEX idx_members_business_ids 
ON members 
USING gin(business_ids);
```

**Query Pattern**:
```sql
-- Find members who work in specific business
SELECT * FROM members
WHERE business_ids @> ARRAY[1];  -- Contains business_id 1 (Inventum)
```

**Use Case**: Task assignment suggestions

**Operator**: `@>` (contains)
- `business_ids @> ARRAY[1]` - Members working in Inventum
- `business_ids && ARRAY[1,3]` - Members in Inventum OR R&D

---

## 📝 Full-Text Search

### Russian Language Support

```sql
CREATE INDEX idx_tasks_title_fts 
ON tasks 
USING gin(to_tsvector('russian', title));
```

**Query Pattern**:
```sql
-- Search tasks by keywords
SELECT * FROM tasks
WHERE to_tsvector('russian', title) @@ to_tsquery('russian', 'ремонт & фрезер')
ORDER BY ts_rank(to_tsvector('russian', title), to_tsquery('russian', 'ремонт & фрезер')) DESC;
```

**Features**:
- Stemming: "ремонт", "ремонтировать" → same root
- Stop words: "и", "в", "на" ignored
- Morphology: handles Russian cases

**Alternative**: `pg_trgm` for fuzzy search (not needed yet)

---

## ⚡ Performance Optimization

### Index Maintenance

#### Auto-Vacuum Configuration
```sql
-- For tasks table (high churn)
ALTER TABLE tasks SET (
    autovacuum_vacuum_scale_factor = 0.1,  -- Vacuum at 10% dead rows
    autovacuum_analyze_scale_factor = 0.05  -- Analyze at 5% changes
);
```

#### Reindex Strategy
```bash
# Monthly maintenance (cron job)
#!/bin/bash
# Reindex concurrently (no downtime)
psql -U planner -d planner -c "REINDEX INDEX CONCURRENTLY idx_tasks_embedding_hnsw;"
```

**Why**: HNSW index can degrade with many updates

**Frequency**: Monthly (low write volume = rarely needed)

---

### Index Usage Monitoring

```sql
-- Check index usage
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan as scans,
    idx_tup_read as tuples_read,
    idx_tup_fetch as tuples_fetched,
    pg_size_pretty(pg_relation_size(indexrelid)) as size
FROM pg_stat_user_indexes
ORDER BY idx_scan DESC;

-- Find unused indexes
SELECT 
    schemaname,
    tablename,
    indexname,
    pg_size_pretty(pg_relation_size(indexrelid)) as size
FROM pg_stat_user_indexes
WHERE idx_scan = 0
  AND indexrelname NOT LIKE 'pg_toast%';
```

**Action**: If index has 0 scans after 1 month → consider dropping

---

## 📐 Index Size Estimates

### At Scale (6,000 tasks)

| Index | Type | Size | Critical |
|-------|------|------|----------|
| `idx_tasks_embedding_hnsw` | HNSW | ~40 MB | ⭐⭐⭐ |
| `idx_tasks_business` | B-tree | ~200 KB | ⭐⭐⭐ |
| `idx_tasks_status` | B-tree | ~200 KB | ⭐⭐ |
| `idx_tasks_user_business_status` | B-tree | ~300 KB | ⭐⭐⭐ |
| `idx_tasks_title_fts` | GIN | ~5 MB | ⭐ |
| Others | B-tree | ~2 MB | ⭐ |
| **Total** | - | **~50 MB** | - |

**Storage**:
- Tasks data: ~40 MB
- Indexes: ~50 MB
- **Total**: ~90 MB (fits easily in $6 Droplet)

---

## 🎯 Query Optimization Examples

### Before Index
```sql
EXPLAIN ANALYZE
SELECT * FROM tasks
WHERE business_id = 1 AND status = 'open'
ORDER BY deadline;

-- Result: Seq Scan (slow)
-- Execution time: ~500ms (for 6,000 rows)
```

### After Index
```sql
-- Same query
EXPLAIN ANALYZE
SELECT * FROM tasks
WHERE business_id = 1 AND status = 'open'
ORDER BY deadline;

-- Result: Index Scan using idx_tasks_business_status_deadline
-- Execution time: ~5ms ✅
```

**Improvement**: 100x faster!

---

### Vector Search Performance

#### Without HNSW Index
```sql
-- Brute force (exact but slow)
SELECT * FROM tasks
ORDER BY embedding <=> $1
LIMIT 5;

-- Execution time: ~500ms (scans all 6,000 rows)
```

#### With HNSW Index
```sql
-- Same query
SELECT * FROM tasks
ORDER BY embedding <=> $1
LIMIT 5;

-- Execution time: ~30ms ✅
-- Uses: idx_tasks_embedding_hnsw
```

**Improvement**: 16x faster!

---

## 🔧 Index Maintenance Scripts

### Monthly Maintenance
```sql
-- Analyze tables (update statistics)
ANALYZE users;
ANALYZE businesses;
ANALYZE members;
ANALYZE projects;
ANALYZE tasks;
ANALYZE task_history;

-- Vacuum (clean dead rows)
VACUUM ANALYZE tasks;

-- Reindex HNSW (if needed)
REINDEX INDEX CONCURRENTLY idx_tasks_embedding_hnsw;
```

### Check Index Health
```sql
-- Check index bloat
SELECT
    schemaname,
    tablename,
    indexname,
    pg_size_pretty(pg_relation_size(indexrelid)) AS index_size,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
ORDER BY pg_relation_size(indexrelid) DESC;
```

---

## ⚠️ Anti-Patterns to Avoid

### 1. Over-Indexing
```sql
-- ❌ DON'T: Index every column
CREATE INDEX idx_tasks_title ON tasks(title);  -- Rarely used alone
CREATE INDEX idx_tasks_description ON tasks(description);  -- Almost never filtered
CREATE INDEX idx_tasks_created_at ON tasks(created_at);  -- Rarely queried

-- Better: Use composite indexes for actual query patterns
```

### 2. Redundant Indexes
```sql
-- ❌ DON'T: Create redundant indexes
CREATE INDEX idx_a ON tasks(business_id);
CREATE INDEX idx_b ON tasks(business_id, status);  -- idx_a is redundant!

-- PostgreSQL can use idx_b for business_id queries alone
```

### 3. Function Indexes Without Need
```sql
-- ❌ DON'T: Create function index without proof of need
CREATE INDEX idx_tasks_deadline_date ON tasks(deadline::date);

-- ✅ DO: Only if query pattern is proven frequent
```

---

## 📈 Scaling Considerations

### Current Scale (6K tasks)
- All indexes fit in memory (50 MB)
- Query time < 50ms
- No optimization needed

### Growth (60K tasks)
- Indexes: ~500 MB
- Still fits in RAM
- HNSW might need tuning (increase m parameter)

### Large Scale (600K tasks)
- Indexes: ~5 GB
- Consider partitioning by business_id
- Consider archiving old tasks
- Might need bigger Droplet ($12-18/month)

**Note**: We won't reach this scale for years

---

## ✅ Success Metrics

### Query Performance Targets

| Query Type | Target | Critical |
|------------|--------|----------|
| Today's tasks | < 20ms | ⭐⭐⭐ |
| Vector search | < 50ms | ⭐⭐⭐ |
| Create task | < 10ms | ⭐⭐⭐ |
| Weekly analytics | < 200ms | ⭐⭐ |
| Full-text search | < 100ms | ⭐ |

### Index Health Metrics

| Metric | Target |
|--------|--------|
| Index usage rate | > 80% of indexes used weekly |
| Bloat ratio | < 20% |
| Rebuild frequency | Monthly (HNSW only) |
| Total size | < 100 MB (Year 1) |

---

## 🛠️ Maintenance Checklist

### Weekly
- [ ] Check slow queries log
- [ ] Monitor index sizes

### Monthly
- [ ] Analyze all tables
- [ ] Check index usage statistics
- [ ] Reindex HNSW if needed
- [ ] Vacuum analyze tasks table

### Quarterly
- [ ] Review unused indexes (drop if 0 scans)
- [ ] Check for missing indexes (slow query log)
- [ ] Update statistics

---

## 📝 References

- PostgreSQL Indexes: https://www.postgresql.org/docs/15/indexes.html
- pgvector Indexes: https://github.com/pgvector/pgvector#indexing
- HNSW Algorithm: https://arxiv.org/abs/1603.09320
- Schema: `docs/02-database/schema.sql`
- ADR-004: RAG Strategy
- ADR-005: PostgreSQL + pgvector

---

**Created**: 2025-10-17  
**Status**: ✅ Complete  
**Total Indexes**: 32  
**Critical Indexes**: 5  
**Expected Performance**: All queries < 100ms

