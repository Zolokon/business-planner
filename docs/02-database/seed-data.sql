-- ============================================================================
-- Business Planner - Seed Data for Testing
-- ============================================================================
-- Purpose: Realistic test data for development and testing
-- Created: 2025-10-17
-- Note: This data mimics real usage patterns
-- ============================================================================

-- Clear existing data (for re-seeding)
TRUNCATE task_history CASCADE;
TRUNCATE tasks CASCADE;
TRUNCATE projects CASCADE;
TRUNCATE members RESTART IDENTITY CASCADE;
TRUNCATE businesses RESTART IDENTITY CASCADE;
TRUNCATE users RESTART IDENTITY CASCADE;

-- ============================================================================
-- USERS
-- ============================================================================

INSERT INTO users (telegram_id, name, username, timezone, preferences) VALUES
    (123456789, 'Константин', 'konstantin_ceo', 'Asia/Almaty', 
     '{"default_business": "inventum", "time_morning": "09:00", "time_evening": "19:00"}'::jsonb);

-- ============================================================================
-- BUSINESSES (4 fixed businesses)
-- ============================================================================

INSERT INTO businesses (id, name, display_name, description, keywords, color) VALUES
    (1, 'inventum', 'Inventum', 
     'Сервис по ремонту стоматологического оборудования',
     ARRAY['фрезер', 'ремонт', 'диагностика', 'починить', 'сервис', 'Иванов', 'Петров', 'клиент', 'выезд', 'плата', 'наконечник'],
     '#3498db'),
     
    (2, 'lab', 'Inventum Lab',
     'Зуботехническая лаборатория',
     ARRAY['коронка', 'моделирование', 'CAD', 'CAM', 'фрезеровка', 'зуб', 'протез', 'лаборатория', 'мост', 'винир'],
     '#2ecc71'),
     
    (3, 'r&d', 'R&D',
     'Исследования и разработка прототипов',
     ARRAY['прототип', 'разработка', 'workshop', 'тест', 'дизайн', 'документация', 'исследование', 'эксперимент'],
     '#9b59b6'),
     
    (4, 'trade', 'Import & Trade',
     'Импорт оборудования из Китая',
     ARRAY['поставщик', 'Китай', 'контракт', 'таможня', 'логистика', 'импорт', 'экспорт', 'доставка', 'счет', 'оплата'],
     '#e74c3c');

-- ============================================================================
-- TEAM MEMBERS (8 people)
-- ============================================================================

INSERT INTO members (name, role, business_ids, skills, is_cross_functional, notes) VALUES
    -- Leadership (cross-business)
    ('Константин', 'CEO', ARRAY[1,2,3,4], 
     ARRAY['management', 'strategy', 'leadership'], 
     true, 'Founder, manages all 4 businesses'),
    
    ('Лиза', 'Маркетинг/SMM', ARRAY[1,2,3,4], 
     ARRAY['marketing', 'smm', 'content', 'design'], 
     true, 'Marketing across all businesses'),
    
    -- Inventum team
    ('Максим', 'Директор Inventum', ARRAY[1,3], 
     ARRAY['management', 'diagnostics', 'technical', 'r&d'], 
     true, 'Director of Inventum, also participates in R&D'),
    
    ('Дима', 'Мастер', ARRAY[1,3], 
     ARRAY['repairs', 'technical', 'diagnostics', 'prototyping'], 
     true, 'Master technician, also works on R&D projects'),
    
    ('Максут', 'Выездной мастер', ARRAY[1], 
     ARRAY['field_service', 'repairs', 'customer_service', 'diagnostics'], 
     false, 'Field service technician'),
    
    -- Inventum Lab team
    ('Юрий Владимирович', 'Директор Inventum Lab', ARRAY[2], 
     ARRAY['management', 'quality_control', 'dental_tech'], 
     false, 'Director of dental laboratory'),
    
    ('Мария', 'CAD/CAM оператор', ARRAY[2], 
     ARRAY['cad', 'cam', 'modeling', 'milling', 'design'], 
     false, 'CAD/CAM specialist'),
    
    -- Import & Trade team
    ('Слава', 'Юрист/бухгалтер', ARRAY[4], 
     ARRAY['legal', 'accounting', 'customs', 'contracts'], 
     false, 'Legal and accounting specialist');

-- ============================================================================
-- PROJECTS (Sample projects for each business)
-- ============================================================================

INSERT INTO projects (user_id, business_id, name, description, status, deadline) VALUES
    -- Inventum projects
    (1, 1, 'Ремонт фрезера Иванова', 'Полный ремонт фрезера для клиента Иванов', 'active', NOW() + INTERVAL '14 days'),
    (1, 1, 'Сервисное обслуживание Петрова', 'Регулярное обслуживание оборудования', 'active', NOW() + INTERVAL '7 days'),
    
    -- Inventum Lab projects
    (1, 2, 'Заказ на 10 коронок', 'Производство коронок для клиники', 'active', NOW() + INTERVAL '5 days'),
    (1, 2, 'Новый сайт лаборатории', 'Разработка нового сайта', 'on_hold', NULL),
    
    -- R&D projects
    (1, 3, 'Прототип нового наконечника', 'Разработка улучшенного наконечника', 'active', NOW() + INTERVAL '30 days'),
    
    -- Import & Trade projects
    (1, 4, 'Декабрьская поставка', 'Импорт оборудования на декабрь', 'active', NOW() + INTERVAL '45 days');

-- ============================================================================
-- TASKS (Sample tasks with realistic data)
-- ============================================================================

-- Get user_id and member_ids for reference
DO $$
DECLARE
    user_id_var INTEGER;
    maxim_id INTEGER;
    dima_id INTEGER;
    maksut_id INTEGER;
    maria_id INTEGER;
    slava_id INTEGER;
BEGIN
    SELECT id INTO user_id_var FROM users WHERE telegram_id = 123456789;
    SELECT id INTO maxim_id FROM members WHERE name = 'Максим';
    SELECT id INTO dima_id FROM members WHERE name = 'Дима';
    SELECT id INTO maksut_id FROM members WHERE name = 'Максут';
    SELECT id INTO maria_id FROM members WHERE name = 'Мария';
    SELECT id INTO slava_id FROM members WHERE name = 'Слава';

-- Inventum tasks
INSERT INTO tasks (user_id, business_id, project_id, assigned_to, title, status, priority, estimated_duration, actual_duration, deadline, completed_at) VALUES
    -- Completed tasks (for learning)
    (user_id_var, 1, 1, dima_id, 'Диагностика платы фрезера', 'done', 1, 90, 120, NOW() - INTERVAL '2 days', NOW() - INTERVAL '2 days'),
    (user_id_var, 1, 1, dima_id, 'Замена подшипников', 'done', 2, 60, 75, NOW() - INTERVAL '3 days', NOW() - INTERVAL '3 days'),
    (user_id_var, 1, NULL, maksut_id, 'Выезд к клиенту Иванову', 'done', 1, 180, 150, NOW() - INTERVAL '5 days', NOW() - INTERVAL '5 days'),
    (user_id_var, 1, 2, maxim_id, 'Позвонить Петрову по сервису', 'done', 3, 30, 45, NOW() - INTERVAL '1 day', NOW() - INTERVAL '1 day'),
    
    -- Open tasks
    (user_id_var, 1, 1, dima_id, 'Ремонт главного вала', 'open', 1, 120, NULL, NOW() + INTERVAL '1 day', NULL),
    (user_id_var, 1, NULL, maksut_id, 'Выезд на диагностику к новому клиенту', 'open', 2, 120, NULL, NOW() + INTERVAL '2 days', NULL);

-- Inventum Lab tasks
INSERT INTO tasks (user_id, business_id, project_id, assigned_to, title, status, priority, estimated_duration, actual_duration, deadline, completed_at) VALUES
    -- Completed
    (user_id_var, 2, 3, maria_id, 'Моделирование коронки', 'done', 2, 90, 85, NOW() - INTERVAL '1 day', NOW() - INTERVAL '1 day'),
    (user_id_var, 2, 3, maria_id, 'Фрезеровка 3 коронок', 'done', 2, 120, 110, NOW() - INTERVAL '2 days', NOW() - INTERVAL '2 days'),
    
    -- Open
    (user_id_var, 2, 3, maria_id, 'Моделировать 5 коронок для заказа', 'open', 1, 180, NULL, NOW() + INTERVAL '2 days', NULL),
    (user_id_var, 2, 4, NULL, 'Подготовить контент для нового сайта', 'open', 3, 240, NULL, NOW() + INTERVAL '10 days', NULL);

-- R&D tasks
INSERT INTO tasks (user_id, business_id, project_id, assigned_to, title, status, priority, estimated_duration, actual_duration, deadline, completed_at) VALUES
    -- Completed
    (user_id_var, 3, 5, dima_id, 'Тест прототипа наконечника', 'done', 1, 180, 200, NOW() - INTERVAL '3 days', NOW() - INTERVAL '3 days'),
    
    -- Open
    (user_id_var, 3, 5, maxim_id, 'Разработать 3D модель нового наконечника', 'open', 2, 240, NULL, NOW() + INTERVAL '5 days', NULL),
    (user_id_var, 3, 5, dima_id, 'Документация по прототипу', 'open', 3, 120, NULL, NOW() + INTERVAL '7 days', NULL);

-- Import & Trade tasks
INSERT INTO tasks (user_id, business_id, project_id, assigned_to, title, status, priority, estimated_duration, actual_duration, deadline, completed_at) VALUES
    -- Completed
    (user_id_var, 4, 6, slava_id, 'Подготовить контракт с поставщиком', 'done', 1, 120, 90, NOW() - INTERVAL '1 day', NOW() - INTERVAL '1 day'),
    (user_id_var, 4, NULL, slava_id, 'Позвонить поставщику фрез', 'done', 2, 30, 45, NOW() - INTERVAL '4 days', NOW() - INTERVAL '4 days'),
    
    -- Open
    (user_id_var, 4, 6, slava_id, 'Проверить таможенные документы', 'open', 1, 60, NULL, NOW() + INTERVAL '1 day', NULL),
    (user_id_var, 4, 6, NULL, 'Связаться с логистической компанией', 'open', 2, 45, NULL, NOW() + INTERVAL '3 days', NULL);

END $$;

-- ============================================================================
-- GENERATE EMBEDDINGS (Placeholder)
-- ============================================================================
-- Note: Real embeddings will be generated by OpenAI API
-- For testing, we use zero vectors (will be replaced in application)

UPDATE tasks SET embedding = ARRAY(SELECT 0 FROM generate_series(1, 1536))::vector(1536);

COMMENT ON COLUMN tasks.embedding IS 'Placeholder zero vectors - real embeddings generated by OpenAI API';

-- ============================================================================
-- VERIFICATION
-- ============================================================================

-- Check data
SELECT 'Users count:' as check, COUNT(*) as count FROM users
UNION ALL
SELECT 'Businesses count:', COUNT(*) FROM businesses
UNION ALL
SELECT 'Members count:', COUNT(*) FROM members
UNION ALL
SELECT 'Projects count:', COUNT(*) FROM projects
UNION ALL
SELECT 'Tasks count:', COUNT(*) FROM tasks
UNION ALL
SELECT 'Task history count:', COUNT(*) FROM task_history;

-- Tasks by business
SELECT 
    b.display_name,
    COUNT(CASE WHEN t.status = 'open' THEN 1 END) as open_tasks,
    COUNT(CASE WHEN t.status = 'done' THEN 1 END) as completed_tasks,
    COUNT(*) as total_tasks
FROM businesses b
LEFT JOIN tasks t ON b.id = t.business_id
GROUP BY b.id, b.display_name
ORDER BY b.id;

-- Tasks by member
SELECT 
    m.name,
    m.role,
    COUNT(t.id) as assigned_tasks
FROM members m
LEFT JOIN tasks t ON m.id = t.assigned_to
GROUP BY m.id, m.name, m.role
ORDER BY assigned_tasks DESC;

-- Estimation accuracy (sample)
SELECT 
    business_id,
    COUNT(*) as completed_tasks,
    AVG(estimated_duration) as avg_estimated,
    AVG(actual_duration) as avg_actual,
    AVG(ABS(estimated_duration - actual_duration)::FLOAT / actual_duration * 100) as avg_error_percent
FROM tasks
WHERE status = 'done' 
  AND estimated_duration IS NOT NULL 
  AND actual_duration IS NOT NULL
GROUP BY business_id;

-- ============================================================================
-- EXPECTED OUTPUT
-- ============================================================================
/*
Users count: 1
Businesses count: 4
Members count: 8
Projects count: 6
Tasks count: 16 (8 open, 8 completed)
Task history count: 16 (auto-created by trigger)

Tasks by business:
- Inventum: 3 open, 3 completed
- Inventum Lab: 2 open, 2 completed  
- R&D: 2 open, 1 completed
- Import & Trade: 2 open, 2 completed

Tasks by member:
- Дима: 3 tasks
- Слава: 3 tasks
- Мария: 3 tasks
- Максим: 2 tasks
- Максут: 2 tasks
- Others: 0 tasks (unassigned)
*/

