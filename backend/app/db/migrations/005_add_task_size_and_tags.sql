-- Add size and tags columns to tasks table
-- These fields are required for the Kanban board schema

-- ============================================================================
-- ADD SIZE COLUMN
-- ============================================================================

DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'tasks' AND column_name = 'size'
    ) THEN
        ALTER TABLE tasks ADD COLUMN size INTEGER;
    END IF;
END $$;

-- Add check constraint for Fibonacci size values (1, 2, 3, 5, 8, 13)
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'tasks_size_fibonacci_check'
    ) THEN
        ALTER TABLE tasks 
        ADD CONSTRAINT tasks_size_fibonacci_check 
        CHECK (size IS NULL OR size IN (1, 2, 3, 5, 8, 13));
    END IF;
END $$;

-- ============================================================================
-- ADD TAGS COLUMN
-- ============================================================================

DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'tasks' AND column_name = 'tags'
    ) THEN
        ALTER TABLE tasks ADD COLUMN tags TEXT[] DEFAULT '{}';
    END IF;
END $$;

-- ============================================================================
-- ADD INDEXES
-- ============================================================================

-- Index on size for filtering/sorting
CREATE INDEX IF NOT EXISTS idx_tasks_size ON tasks(size) WHERE size IS NOT NULL;

-- Index on tags using GIN for array operations
CREATE INDEX IF NOT EXISTS idx_tasks_tags ON tasks USING GIN(tags);

-- Additional indexes for task editing queries
CREATE INDEX IF NOT EXISTS idx_tasks_assignee_type ON tasks(assignee_type) WHERE assignee_type IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_tasks_updated_at ON tasks(updated_at);

-- ============================================================================
-- COMMENTS
-- ============================================================================

COMMENT ON COLUMN tasks.size IS 'Task size in Fibonacci points (1, 2, 3, 5, 8, 13)';
COMMENT ON COLUMN tasks.tags IS 'Array of lowercase tags for task categorization';
