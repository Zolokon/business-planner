# Database Migrations Plan - Business Planner

> **Alembic migration strategy**  
> **Created**: 2025-10-17  
> **Tool**: Alembic (SQLAlchemy migration tool)

---

## 🎯 Migration Strategy

### Philosophy
- **Version controlled** - Every schema change is a migration
- **Reversible** - Every migration has upgrade + downgrade
- **Tested** - Migrations tested before production
- **Documented** - Each migration explains "why"

### Tool: Alembic
- Industry standard for SQLAlchemy
- Auto-generates migrations from models
- Supports async (asyncpg)
- Branch management

---

## 📋 Migration Plan

### Phase 1: Initial Schema (Week 1)

#### V001_initial_schema.py
**Purpose**: Create all initial tables

**Includes**:
- Enable pgvector extension
- Create tables: users, businesses, members, projects, tasks, task_history
- Create all indexes
- Create all triggers and functions
- Insert initial data (4 businesses, 8 members)

**Upgrade**:
```python
def upgrade():
    # Enable extension
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    
    # Create tables
    op.create_table('users', ...)
    op.create_table('businesses', ...)
    # ... all tables
    
    # Create indexes
    op.create_index('idx_tasks_embedding_hnsw', ...)
    # ... all indexes
    
    # Insert initial data
    op.execute("INSERT INTO businesses VALUES ...")
```

**Downgrade**:
```python
def downgrade():
    op.drop_index('idx_tasks_embedding_hnsw')
    op.drop_table('task_history')
    op.drop_table('tasks')
    # ... reverse order
    op.execute("DROP EXTENSION vector")
```

---

### Phase 2: Features (Weeks 2-12)

#### V002_add_recurring_tasks.py (if needed)
**Purpose**: Add support for recurring tasks

```python
def upgrade():
    op.add_column('tasks', 
        sa.Column('is_recurring', sa.Boolean(), default=False))
    op.add_column('tasks',
        sa.Column('recurrence_rule', sa.String(100)))
    op.create_index('idx_tasks_recurring', 'tasks', ['is_recurring'])
```

#### V003_add_notifications.py (if needed)
**Purpose**: Add notification system

```python
def upgrade():
    op.create_table('notifications',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id')),
        sa.Column('task_id', sa.Integer(), sa.ForeignKey('tasks.id')),
        sa.Column('type', sa.String(50)),
        sa.Column('scheduled_at', sa.DateTime()),
        sa.Column('sent_at', sa.DateTime())
    )
```

#### V004_add_task_templates.py (if needed)
**Purpose**: Template tasks for common operations

```python
def upgrade():
    op.create_table('task_templates',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer()),
        sa.Column('business_id', sa.Integer()),
        sa.Column('title', sa.String(200)),
        sa.Column('default_duration', sa.Integer())
    )
```

---

### Phase 3: Optimization (Month 2-3)

#### V005_partition_task_history.py (if table grows large)
**Purpose**: Partition task_history by month

```python
def upgrade():
    # Only if task_history > 100K rows
    op.execute("""
        CREATE TABLE task_history_partitioned (LIKE task_history)
        PARTITION BY RANGE (occurred_at);
        
        CREATE TABLE task_history_2025_10 
        PARTITION OF task_history_partitioned
        FOR VALUES FROM ('2025-10-01') TO ('2025-11-01');
    """)
```

---

## 🔧 Alembic Configuration

### Directory Structure
```
migrations/
├── alembic.ini              # Alembic configuration
├── env.py                   # Migration environment
├── script.py.mako           # Migration template
└── versions/
    ├── 001_initial_schema.py
    ├── 002_add_recurring_tasks.py (future)
    └── 003_add_notifications.py (future)
```

### alembic.ini
```ini
[alembic]
script_location = migrations
sqlalchemy.url = postgresql://planner:password@localhost/planner

# Async support
# sqlalchemy.url = postgresql+asyncpg://planner:password@localhost/planner

[loggers]
keys = root,sqlalchemy,alembic

[logger_alembic]
level = INFO
handlers =
qualname = alembic
```

### env.py (Async Configuration)
```python
from sqlalchemy.ext.asyncio import create_async_engine
from src.infrastructure.database.models import Base

# Async engine
connectable = create_async_engine(
    config.get_main_option("sqlalchemy.url"),
    future=True,
)

async def run_migrations_online():
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

# Auto-generate migrations
target_metadata = Base.metadata
```

---

## 🚀 Migration Commands

### Development

```bash
# Initialize Alembic (one-time)
alembic init migrations

# Create new migration (auto-generate from models)
alembic revision --autogenerate -m "Add new feature"

# Upgrade to latest
alembic upgrade head

# Downgrade one version
alembic downgrade -1

# Show current version
alembic current

# Show migration history
alembic history
```

### Production

```bash
# Check current database version
alembic current

# Preview SQL (don't execute)
alembic upgrade head --sql

# Execute upgrade
alembic upgrade head

# Backup before migration!
pg_dump -U planner planner > backup_before_migration.sql
```

---

## ✅ Migration Checklist

Before running migration in production:

- [ ] **Backup database** (pg_dump)
- [ ] **Test migration** on staging database
- [ ] **Review generated SQL** (alembic upgrade head --sql)
- [ ] **Check for data loss** (downgrade → upgrade works)
- [ ] **Verify indexes** created correctly
- [ ] **Test application** after migration
- [ ] **Monitor performance** after migration
- [ ] **Have rollback plan** (downgrade script ready)

---

## 🔄 Migration Workflow

### Development
```bash
# 1. Modify SQLAlchemy models
# Edit src/infrastructure/database/models.py

# 2. Generate migration
alembic revision --autogenerate -m "Add field to tasks"

# 3. Review generated migration
# Edit migrations/versions/XXX_add_field_to_tasks.py

# 4. Test upgrade
alembic upgrade head

# 5. Test application
pytest tests/integration/test_database.py

# 6. Test downgrade
alembic downgrade -1

# 7. Upgrade again (verify idempotent)
alembic upgrade head

# 8. Commit migration file
git add migrations/versions/XXX_add_field_to_tasks.py
git commit -m "Migration: Add field to tasks"
```

### Production
```bash
# 1. Backup
docker-compose exec postgres pg_dump -U planner planner > backup.sql

# 2. Run migration
docker-compose exec backend alembic upgrade head

# 3. Verify
docker-compose exec postgres psql -U planner -c "\dt"

# 4. Monitor
docker-compose logs -f backend
```

---

## 🎯 Zero-Downtime Migrations

### For Large Tables (future)

```python
# Use CONCURRENTLY for indexes
def upgrade():
    # ✅ GOOD: No table lock
    op.execute(
        "CREATE INDEX CONCURRENTLY idx_new ON tasks(column)"
    )

# ❌ BAD: Locks table
def upgrade():
    op.create_index('idx_new', 'tasks', ['column'])
```

### For Column Changes
```python
# Add column (safe, doesn't lock)
def upgrade():
    op.add_column('tasks', 
        sa.Column('new_field', sa.String(100), nullable=True))

# Backfill data (in batches)
    op.execute("""
        UPDATE tasks 
        SET new_field = 'default' 
        WHERE new_field IS NULL
    """)

# Make NOT NULL (safe now)
    op.alter_column('tasks', 'new_field', nullable=False)
```

---

## 📊 Expected Migrations

### Year 1
- `V001_initial_schema` - Initial tables
- `V002_add_task_tags` - Optional tagging
- `V003_add_notifications` - Reminders
- `V004_analytics_tables` - If needed

**Total**: ~4 migrations

### Year 2+
- Performance optimizations
- New features
- Partitioning (if needed)

---

## 🔍 Testing Migrations

### Integration Tests
```python
import pytest
from alembic.config import Config
from alembic import command

@pytest.fixture
async def migrated_db():
    """Apply all migrations to test database."""
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")
    
    yield
    
    # Downgrade after test
    command.downgrade(alembic_cfg, "base")


async def test_migration_upgrade_downgrade():
    """Test that migrations are reversible."""
    alembic_cfg = Config("alembic.ini")
    
    # Upgrade
    command.upgrade(alembic_cfg, "head")
    
    # Downgrade
    command.downgrade(alembic_cfg, "base")
    
    # Upgrade again (should work)
    command.upgrade(alembic_cfg, "head")


async def test_initial_data_seeded():
    """Test that initial data is present after migration."""
    businesses = await session.execute(select(Business))
    assert len(businesses.all()) == 4
    
    members = await session.execute(select(Member))
    assert len(members.all()) == 8
```

---

## 📝 Migration Naming Convention

```
Format: VXXX_descriptive_name.py

Examples:
✅ v001_initial_schema.py
✅ v002_add_recurring_tasks.py
✅ v003_add_notifications_table.py
✅ v004_optimize_task_indexes.py

❌ migration_1.py
❌ update.py
❌ fix_schema.py
```

---

## 🎉 Database Design Complete!

### What We Have

1. ✅ **ER Diagram** (`er-diagram.md`) - Visual schema
2. ✅ **Complete SQL Schema** (`schema.sql`) - ~500 lines
3. ✅ **Seed Data** (`seed-data.sql`) - Test data
4. ✅ **Index Strategy** (`indexes-strategy.md`) - 32 indexes
5. ✅ **Migration Plan** (`migrations/README.md`) - Version control

### Database Specs Summary

- **Tables**: 6 (users, businesses, members, projects, tasks, task_history)
- **Indexes**: 32 (including HNSW vector index)
- **Triggers**: 3 (auto-update, history logging, user activity)
- **Functions**: 4 (utility functions for common queries)
- **Views**: 2 (convenience views)
- **Initial Data**: 4 businesses + 8 team members
- **Test Data**: 16 sample tasks

---

**Status**: ✅ Database Design 100% Complete  
**Next**: Domain Model (DDD) - Task 1.5  
**Estimated Time**: Database ready for implementation!

