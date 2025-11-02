-- Migration: Set completed_at for already completed tasks
-- Date: 2025-11-01
-- Issue: Tasks marked as "done" don't have completed_at timestamp

-- For tasks already marked as "done" but without completed_at,
-- set completed_at to updated_at (best approximation)
UPDATE tasks
SET completed_at = updated_at
WHERE status = 'done'
  AND completed_at IS NULL;

-- Log result
SELECT
    COUNT(*) as tasks_updated,
    'Set completed_at for existing done tasks' as description
FROM tasks
WHERE status = 'done'
  AND completed_at IS NOT NULL;
