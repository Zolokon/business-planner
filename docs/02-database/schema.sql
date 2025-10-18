-- ============================================================================
-- Business Planner - Database Schema
-- ============================================================================
-- Database: PostgreSQL 15 with pgvector extension
-- Purpose: Voice-first task manager for 4 businesses
-- Created: 2025-10-17
-- References: ADR-003 (Business Isolation), ADR-004 (RAG), ADR-005 (pgvector)
-- ============================================================================

-- ============================================================================
-- EXTENSIONS
-- ============================================================================

-- pgvector for embedding similarity search (ADR-004, ADR-005)
CREATE EXTENSION IF NOT EXISTS vector;

-- UUID generation (for future use)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- TABLES
-- ============================================================================

-- ----------------------------------------------------------------------------
-- users - Telegram users
-- ----------------------------------------------------------------------------
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    telegram_id BIGINT NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    username VARCHAR(100),
    timezone VARCHAR(50) DEFAULT 'Asia/Almaty',
    preferences JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_active TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

COMMENT ON TABLE users IS 'Telegram users of Business Planner system';
COMMENT ON COLUMN users.telegram_id IS 'Unique Telegram user ID from Telegram API';
COMMENT ON COLUMN users.timezone IS 'User timezone for deadline calculation (default: UTC+5 Almaty)';
COMMENT ON COLUMN users.preferences IS 'User settings: default business, time preferences, etc.';

-- ----------------------------------------------------------------------------
-- businesses - The 4 business contexts
-- ----------------------------------------------------------------------------
CREATE TABLE businesses (
    id INTEGER PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    display_name VARCHAR(100) NOT NULL,
    description TEXT,
    keywords TEXT[] DEFAULT ARRAY[]::TEXT[],
    color VARCHAR(7),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

COMMENT ON TABLE businesses IS 'Fixed 4 business contexts - CRITICAL for isolation (ADR-003)';
COMMENT ON COLUMN businesses.name IS 'Internal identifier: inventum, lab, r&d, trade';
COMMENT ON COLUMN businesses.keywords IS 'Keywords for AI auto-detection: фрезер, коронка, прототип, поставщик';
COMMENT ON COLUMN businesses.color IS 'Hex color for UI (future): #FF5733';

-- ----------------------------------------------------------------------------
-- members - Team members (8 people)
-- ----------------------------------------------------------------------------
CREATE TABLE members (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    role VARCHAR(200),
    business_ids INTEGER[] NOT NULL DEFAULT ARRAY[]::INTEGER[],
    skills TEXT[] DEFAULT ARRAY[]::TEXT[],
    is_cross_functional BOOLEAN DEFAULT FALSE,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

COMMENT ON TABLE members IS 'Team members across 4 businesses (total 8 people)';
COMMENT ON COLUMN members.business_ids IS 'Array of business IDs - supports cross-functional roles';
COMMENT ON COLUMN members.is_cross_functional IS 'True for members working in multiple businesses (Максим, Дима)';
COMMENT ON COLUMN members.skills IS 'Skills for smart task assignment: repairs, cad, legal, marketing';

-- ----------------------------------------------------------------------------
-- projects - User-created task groupings
-- ----------------------------------------------------------------------------
CREATE TABLE projects (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    business_id INTEGER NOT NULL,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    status VARCHAR(20) DEFAULT 'active',
    deadline TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    
    CONSTRAINT fk_project_user 
        FOREIGN KEY (user_id) 
        REFERENCES users(id) 
        ON DELETE CASCADE,
    
    CONSTRAINT fk_project_business 
        FOREIGN KEY (business_id) 
        REFERENCES businesses(id) 
        ON DELETE RESTRICT,
    
    CONSTRAINT valid_project_status 
        CHECK (status IN ('active', 'on_hold', 'completed'))
);

COMMENT ON TABLE projects IS 'User-created projects for grouping tasks (optional, NOT auto-created)';
COMMENT ON COLUMN projects.business_id IS 'Projects belong to ONE business context';
COMMENT ON COLUMN projects.status IS 'active = working on, on_hold = paused, completed = done';

-- ----------------------------------------------------------------------------
-- tasks - Main entity (core of the system)
-- ----------------------------------------------------------------------------
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    
    -- Ownership
    user_id INTEGER NOT NULL,
    business_id INTEGER NOT NULL,  -- CRITICAL: Mandatory for isolation (ADR-003)
    project_id INTEGER,             -- Optional project grouping
    assigned_to INTEGER,            -- Optional team member
    
    -- Content
    title TEXT NOT NULL,
    description TEXT,
    
    -- Status & Priority
    status VARCHAR(20) DEFAULT 'open',
    priority INTEGER DEFAULT 2,
    
    -- Time tracking
    estimated_duration INTEGER,     -- Minutes (AI estimate)
    actual_duration INTEGER,        -- Minutes (user feedback for learning)
    
    -- Dates
    deadline TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    
    -- AI/ML
    embedding vector(1536),         -- For RAG similarity search (ADR-004)
    
    -- Flexible metadata
    metadata JSONB DEFAULT '{}'::jsonb,
    
    -- Foreign keys
    CONSTRAINT fk_task_user 
        FOREIGN KEY (user_id) 
        REFERENCES users(id) 
        ON DELETE CASCADE,
    
    CONSTRAINT fk_task_business 
        FOREIGN KEY (business_id) 
        REFERENCES businesses(id) 
        ON DELETE RESTRICT,
    
    CONSTRAINT fk_task_project 
        FOREIGN KEY (project_id) 
        REFERENCES projects(id) 
        ON DELETE SET NULL,
    
    CONSTRAINT fk_task_member 
        FOREIGN KEY (assigned_to) 
        REFERENCES members(id) 
        ON DELETE SET NULL,
    
    -- Validation constraints
    CONSTRAINT valid_status 
        CHECK (status IN ('open', 'done', 'archived')),
    
    CONSTRAINT valid_priority 
        CHECK (priority BETWEEN 1 AND 4),
    
    CONSTRAINT valid_estimated_duration 
        CHECK (estimated_duration IS NULL OR estimated_duration BETWEEN 1 AND 480),
    
    CONSTRAINT valid_actual_duration 
        CHECK (actual_duration IS NULL OR actual_duration BETWEEN 1 AND 480),
    
    CONSTRAINT deadline_after_creation 
        CHECK (deadline IS NULL OR deadline > created_at)
);

COMMENT ON TABLE tasks IS 'Main task entity - core of Business Planner system';
COMMENT ON COLUMN tasks.business_id IS 'CRITICAL: Mandatory for business context isolation (ADR-003)';
COMMENT ON COLUMN tasks.embedding IS 'Vector embedding (1536 dims) for RAG similarity search (ADR-004)';
COMMENT ON COLUMN tasks.estimated_duration IS 'AI-generated time estimate in minutes';
COMMENT ON COLUMN tasks.actual_duration IS 'Actual completion time for learning (feedback loop)';
COMMENT ON COLUMN tasks.priority IS '1=DO NOW, 2=SCHEDULE, 3=DELEGATE, 4=BACKLOG (Eisenhower matrix)';
COMMENT ON COLUMN tasks.metadata IS 'Flexible JSON field for future extensions';

-- ----------------------------------------------------------------------------
-- task_history - Audit trail and analytics
-- ----------------------------------------------------------------------------
CREATE TABLE task_history (
    id SERIAL PRIMARY KEY,
    task_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    action VARCHAR(50) NOT NULL,
    changes JSONB DEFAULT '{}'::jsonb,
    duration INTEGER,
    occurred_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT fk_history_task 
        FOREIGN KEY (task_id) 
        REFERENCES tasks(id) 
        ON DELETE CASCADE,
    
    CONSTRAINT fk_history_user 
        FOREIGN KEY (user_id) 
        REFERENCES users(id) 
        ON DELETE CASCADE,
    
    CONSTRAINT valid_action 
        CHECK (action IN ('created', 'updated', 'completed', 'deleted', 'archived'))
);

COMMENT ON TABLE task_history IS 'Audit trail for all task changes - used for analytics and learning';
COMMENT ON COLUMN task_history.action IS 'What happened: created, updated, completed, deleted, archived';
COMMENT ON COLUMN task_history.changes IS 'JSON diff of what changed (before/after)';
COMMENT ON COLUMN task_history.duration IS 'Actual duration if action = completed (for learning)';

-- ============================================================================
-- INDEXES
-- ============================================================================

-- ----------------------------------------------------------------------------
-- users indexes
-- ----------------------------------------------------------------------------
CREATE INDEX idx_users_telegram_id ON users(telegram_id);
CREATE INDEX idx_users_last_active ON users(last_active);

-- ----------------------------------------------------------------------------
-- businesses indexes
-- ----------------------------------------------------------------------------
CREATE INDEX idx_businesses_name ON businesses(name);

-- ----------------------------------------------------------------------------
-- members indexes
-- ----------------------------------------------------------------------------
CREATE INDEX idx_members_name ON members(name);
CREATE INDEX idx_members_cross_functional ON members(is_cross_functional) WHERE is_cross_functional = true;

-- GIN index for array search (find members by business)
CREATE INDEX idx_members_business_ids ON members USING gin(business_ids);

-- ----------------------------------------------------------------------------
-- projects indexes
-- ----------------------------------------------------------------------------
CREATE INDEX idx_projects_user ON projects(user_id);
CREATE INDEX idx_projects_business ON projects(business_id);
CREATE INDEX idx_projects_status ON projects(status);

-- Composite index for common query (user + business + active)
CREATE INDEX idx_projects_user_business_active 
    ON projects(user_id, business_id, status) 
    WHERE status = 'active';

-- ----------------------------------------------------------------------------
-- tasks indexes (MOST IMPORTANT - frequently queried)
-- ----------------------------------------------------------------------------

-- Foreign keys
CREATE INDEX idx_tasks_user ON tasks(user_id);
CREATE INDEX idx_tasks_business ON tasks(business_id);
CREATE INDEX idx_tasks_project ON tasks(project_id) WHERE project_id IS NOT NULL;
CREATE INDEX idx_tasks_assigned ON tasks(assigned_to) WHERE assigned_to IS NOT NULL;

-- Status queries
CREATE INDEX idx_tasks_status ON tasks(status);

-- Deadline queries
CREATE INDEX idx_tasks_deadline ON tasks(deadline) WHERE deadline IS NOT NULL;

-- Common composite queries
CREATE INDEX idx_tasks_user_business_status 
    ON tasks(user_id, business_id, status);

CREATE INDEX idx_tasks_business_status_deadline 
    ON tasks(business_id, status, deadline) 
    WHERE status = 'open';

-- Analytics queries
CREATE INDEX idx_tasks_completed_at 
    ON tasks(completed_at) 
    WHERE completed_at IS NOT NULL;

CREATE INDEX idx_tasks_user_completed 
    ON tasks(user_id, completed_at, status) 
    WHERE status = 'done';

-- Full-text search (Russian)
CREATE INDEX idx_tasks_title_fts 
    ON tasks 
    USING gin(to_tsvector('russian', title));

-- VECTOR INDEX for RAG similarity search (CRITICAL - ADR-004)
-- Using HNSW algorithm for best performance
CREATE INDEX idx_tasks_embedding_hnsw 
    ON tasks 
    USING hnsw (embedding vector_cosine_ops)
    WITH (m = 16, ef_construction = 64);

COMMENT ON INDEX idx_tasks_embedding_hnsw IS 'HNSW index for fast vector similarity search (cosine distance) - CRITICAL for RAG';

-- Composite index: business + embedding
-- Enables fast filtered vector search (business isolation - ADR-003)
CREATE INDEX idx_tasks_business_completed_embedding
    ON tasks(business_id, actual_duration)
    WHERE embedding IS NOT NULL AND actual_duration IS NOT NULL;

-- ----------------------------------------------------------------------------
-- task_history indexes
-- ----------------------------------------------------------------------------
CREATE INDEX idx_history_task ON task_history(task_id);
CREATE INDEX idx_history_user ON task_history(user_id);
CREATE INDEX idx_history_action ON task_history(action);
CREATE INDEX idx_history_occurred ON task_history(occurred_at);

-- Analytics: completed tasks
CREATE INDEX idx_history_completed 
    ON task_history(occurred_at) 
    WHERE action = 'completed';

-- ============================================================================
-- TRIGGERS
-- ============================================================================

-- ----------------------------------------------------------------------------
-- Auto-update updated_at timestamp
-- ----------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_tasks_updated_at
    BEFORE UPDATE ON tasks
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

COMMENT ON FUNCTION update_updated_at_column IS 'Auto-update updated_at timestamp on row modification';

-- ----------------------------------------------------------------------------
-- Auto-create task_history on task changes
-- ----------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION log_task_changes()
RETURNS TRIGGER AS $$
BEGIN
    -- On INSERT
    IF (TG_OP = 'INSERT') THEN
        INSERT INTO task_history (task_id, user_id, action, changes)
        VALUES (NEW.id, NEW.user_id, 'created', to_jsonb(NEW));
        RETURN NEW;
    END IF;
    
    -- On UPDATE
    IF (TG_OP = 'UPDATE') THEN
        -- Check if status changed to 'done'
        IF (OLD.status != 'done' AND NEW.status = 'done') THEN
            INSERT INTO task_history (task_id, user_id, action, changes, duration)
            VALUES (
                NEW.id, 
                NEW.user_id, 
                'completed',
                jsonb_build_object(
                    'before', to_jsonb(OLD),
                    'after', to_jsonb(NEW)
                ),
                NEW.actual_duration
            );
        ELSE
            INSERT INTO task_history (task_id, user_id, action, changes)
            VALUES (
                NEW.id,
                NEW.user_id,
                'updated',
                jsonb_build_object(
                    'before', to_jsonb(OLD),
                    'after', to_jsonb(NEW)
                )
            );
        END IF;
        RETURN NEW;
    END IF;
    
    -- On DELETE
    IF (TG_OP = 'DELETE') THEN
        INSERT INTO task_history (task_id, user_id, action, changes)
        VALUES (OLD.id, OLD.user_id, 'deleted', to_jsonb(OLD));
        RETURN OLD;
    END IF;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_tasks_history
    AFTER INSERT OR UPDATE OR DELETE ON tasks
    FOR EACH ROW
    EXECUTE FUNCTION log_task_changes();

COMMENT ON FUNCTION log_task_changes IS 'Automatically log all task changes to task_history table';

-- ----------------------------------------------------------------------------
-- Update user.last_active on any activity
-- ----------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION update_user_last_active()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE users 
    SET last_active = NOW() 
    WHERE id = NEW.user_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_tasks_user_active
    AFTER INSERT OR UPDATE ON tasks
    FOR EACH ROW
    EXECUTE FUNCTION update_user_last_active();

-- ============================================================================
-- FUNCTIONS
-- ============================================================================

-- ----------------------------------------------------------------------------
-- Vector similarity search with business isolation (ADR-003 + ADR-004)
-- ----------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION find_similar_tasks(
    query_embedding vector(1536),
    query_business_id INTEGER,
    similarity_threshold FLOAT DEFAULT 0.7,
    limit_count INTEGER DEFAULT 5
)
RETURNS TABLE (
    task_id INTEGER,
    task_title TEXT,
    actual_duration INTEGER,
    similarity FLOAT,
    completed_at TIMESTAMP WITH TIME ZONE
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        t.id,
        t.title,
        t.actual_duration,
        1 - (t.embedding <=> query_embedding) as similarity,
        t.completed_at
    FROM tasks t
    WHERE 
        t.business_id = query_business_id  -- CRITICAL: Business isolation
        AND t.embedding IS NOT NULL
        AND t.actual_duration IS NOT NULL
        AND t.status = 'done'
        AND 1 - (t.embedding <=> query_embedding) >= similarity_threshold
    ORDER BY t.embedding <=> query_embedding
    LIMIT limit_count;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION find_similar_tasks IS 'Find similar tasks using vector similarity - MUST filter by business_id (ADR-003)';

-- ============================================================================
-- INITIAL DATA (Seed)
-- ============================================================================

-- ----------------------------------------------------------------------------
-- Insert 4 businesses (fixed, never change)
-- ----------------------------------------------------------------------------
INSERT INTO businesses (id, name, display_name, description, keywords, color) VALUES
    (1, 'inventum', 'Inventum', 
     'Dental equipment repair service',
     ARRAY['фрезер', 'ремонт', 'диагностика', 'починить', 'сервис', 'Иванов', 'клиент', 'выезд'],
     '#3498db'),
     
    (2, 'lab', 'Inventum Lab',
     'Dental laboratory - modeling and production',
     ARRAY['коронка', 'моделирование', 'CAD', 'CAM', 'фрезеровка', 'зуб', 'протез', 'лаборатория'],
     '#2ecc71'),
     
    (3, 'r&d', 'R&D',
     'Research & Development - prototypes',
     ARRAY['прототип', 'разработка', 'workshop', 'тест', 'дизайн', 'документация', 'исследование'],
     '#9b59b6'),
     
    (4, 'trade', 'Import & Trade',
     'Equipment import from China',
     ARRAY['поставщик', 'Китай', 'контракт', 'таможня', 'логистика', 'импорт', 'экспорт', 'доставка'],
     '#e74c3c');

-- ----------------------------------------------------------------------------
-- Insert team members (8 people) - see docs/TEAM.md
-- ----------------------------------------------------------------------------
INSERT INTO members (name, role, business_ids, skills, is_cross_functional) VALUES
    -- Leadership (all businesses)
    ('Константин', 'CEO', ARRAY[1,2,3,4], ARRAY['management', 'strategy'], true),
    ('Лиза', 'Маркетинг/SMM', ARRAY[1,2,3,4], ARRAY['marketing', 'smm', 'content'], true),
    
    -- Inventum (also R&D for Максим and Дима)
    ('Максим', 'Директор Inventum', ARRAY[1,3], ARRAY['management', 'diagnostics', 'r&d'], true),
    ('Дима', 'Мастер', ARRAY[1,3], ARRAY['repairs', 'technical', 'prototyping'], true),
    ('Максут', 'Выездной мастер', ARRAY[1], ARRAY['field_service', 'repairs', 'customer_service'], false),
    
    -- Inventum Lab
    ('Юрий Владимирович', 'Директор Inventum Lab', ARRAY[2], ARRAY['management', 'quality_control'], false),
    ('Мария', 'CAD/CAM оператор', ARRAY[2], ARRAY['cad', 'cam', 'modeling', 'milling'], false),
    
    -- Import & Trade
    ('Слава', 'Юрист/бухгалтер', ARRAY[4], ARRAY['legal', 'accounting', 'customs'], false);

-- ============================================================================
-- VIEWS (for convenience)
-- ============================================================================

-- ----------------------------------------------------------------------------
-- Active tasks with all context
-- ----------------------------------------------------------------------------
CREATE OR REPLACE VIEW v_active_tasks AS
SELECT 
    t.id,
    t.title,
    t.description,
    t.status,
    t.priority,
    t.estimated_duration,
    t.deadline,
    b.display_name as business_name,
    b.color as business_color,
    p.name as project_name,
    m.name as assigned_to_name,
    m.role as assigned_to_role,
    t.created_at,
    EXTRACT(EPOCH FROM (t.deadline - NOW())) / 3600 as hours_until_deadline
FROM tasks t
JOIN businesses b ON t.business_id = b.id
LEFT JOIN projects p ON t.project_id = p.id
LEFT JOIN members m ON t.assigned_to = m.id
WHERE t.status = 'open';

COMMENT ON VIEW v_active_tasks IS 'Active tasks with all joined context - convenient for queries';

-- ----------------------------------------------------------------------------
-- Completed tasks with duration accuracy
-- ----------------------------------------------------------------------------
CREATE OR REPLACE VIEW v_completed_tasks_accuracy AS
SELECT 
    t.id,
    t.title,
    b.display_name as business_name,
    t.estimated_duration,
    t.actual_duration,
    CASE 
        WHEN t.estimated_duration IS NULL OR t.actual_duration IS NULL THEN NULL
        ELSE ABS(t.estimated_duration - t.actual_duration)::FLOAT / t.actual_duration
    END as error_rate,
    CASE
        WHEN t.estimated_duration IS NULL OR t.actual_duration IS NULL THEN NULL
        ELSE (1 - ABS(t.estimated_duration - t.actual_duration)::FLOAT / t.actual_duration) * 100
    END as accuracy_percent,
    t.completed_at
FROM tasks t
JOIN businesses b ON t.business_id = b.id
WHERE t.status = 'done'
  AND t.actual_duration IS NOT NULL;

COMMENT ON VIEW v_completed_tasks_accuracy IS 'Completed tasks with estimation accuracy metrics - for learning analytics';

-- ============================================================================
-- UTILITY FUNCTIONS
-- ============================================================================

-- ----------------------------------------------------------------------------
-- Get tasks for today (by business)
-- ----------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION get_today_tasks(
    query_user_id INTEGER,
    query_business_id INTEGER DEFAULT NULL
)
RETURNS TABLE (
    id INTEGER,
    title TEXT,
    business_name VARCHAR(100),
    priority INTEGER,
    estimated_duration INTEGER,
    deadline TIMESTAMP WITH TIME ZONE,
    assigned_to_name VARCHAR(100)
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        t.id,
        t.title,
        b.display_name,
        t.priority,
        t.estimated_duration,
        t.deadline,
        m.name
    FROM tasks t
    JOIN businesses b ON t.business_id = b.id
    LEFT JOIN members m ON t.assigned_to = m.id
    WHERE 
        t.user_id = query_user_id
        AND t.status = 'open'
        AND t.deadline::date = CURRENT_DATE
        AND (query_business_id IS NULL OR t.business_id = query_business_id)
    ORDER BY t.priority ASC, t.deadline ASC;
END;
$$ LANGUAGE plpgsql;

-- ----------------------------------------------------------------------------
-- Get estimation accuracy by business
-- ----------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION get_estimation_accuracy(
    query_user_id INTEGER,
    query_business_id INTEGER,
    days_back INTEGER DEFAULT 30
)
RETURNS TABLE (
    total_tasks BIGINT,
    avg_error_percent FLOAT,
    avg_accuracy_percent FLOAT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(*) as total_tasks,
        AVG(ABS(estimated_duration - actual_duration)::FLOAT / actual_duration * 100) as avg_error_percent,
        AVG((1 - ABS(estimated_duration - actual_duration)::FLOAT / actual_duration) * 100) as avg_accuracy_percent
    FROM tasks
    WHERE 
        user_id = query_user_id
        AND business_id = query_business_id
        AND status = 'done'
        AND estimated_duration IS NOT NULL
        AND actual_duration IS NOT NULL
        AND completed_at >= NOW() - (days_back || ' days')::INTERVAL;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION get_estimation_accuracy IS 'Calculate time estimation accuracy for learning metrics (target: 50% → 80%)';

-- ============================================================================
-- GRANTS (Security)
-- ============================================================================

-- Create application user (least privilege)
-- CREATE USER planner_app WITH PASSWORD 'secure_password';

-- Grant necessary permissions
-- GRANT CONNECT ON DATABASE planner TO planner_app;
-- GRANT USAGE ON SCHEMA public TO planner_app;
-- GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO planner_app;
-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO planner_app;

-- ============================================================================
-- VALIDATION QUERIES
-- ============================================================================

-- Verify pgvector extension
SELECT * FROM pg_extension WHERE extname = 'vector';

-- Verify tables created
SELECT tablename FROM pg_tables WHERE schemaname = 'public' ORDER BY tablename;

-- Verify indexes
SELECT indexname, tablename FROM pg_indexes WHERE schemaname = 'public' ORDER BY tablename, indexname;

-- Check initial data
SELECT id, name, display_name, array_length(keywords, 1) as keyword_count FROM businesses;
SELECT name, role, array_length(business_ids, 1) as business_count, is_cross_functional FROM members;

-- ============================================================================
-- MAINTENANCE
-- ============================================================================

-- Analyze tables for query optimization
ANALYZE users;
ANALYZE businesses;
ANALYZE members;
ANALYZE projects;
ANALYZE tasks;
ANALYZE task_history;

-- Vacuum (clean up dead rows)
VACUUM ANALYZE tasks;

-- ============================================================================
-- END OF SCHEMA
-- ============================================================================

-- Total tables: 6 (users, businesses, members, projects, tasks, task_history)
-- Total indexes: ~25
-- Total triggers: 3
-- Total functions: 4
-- Total views: 2

