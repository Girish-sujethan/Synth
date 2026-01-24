-- Add Task Status Database Schema and Audit Events
-- Extends events table to support task status tracking with proper audit logging

-- ============================================================================
-- UPDATE EVENTS TABLE
-- ============================================================================

-- Add task_id column if it doesn't exist
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'events' AND column_name = 'task_id'
    ) THEN
        ALTER TABLE events ADD COLUMN task_id UUID REFERENCES tasks(id) ON DELETE CASCADE;
    END IF;
END $$;

-- Add type column if it doesn't exist (alias for event_type for compatibility)
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'events' AND column_name = 'type'
    ) THEN
        ALTER TABLE events ADD COLUMN type TEXT;
    END IF;
END $$;

-- Sync type with event_type for existing records
UPDATE events SET type = event_type WHERE type IS NULL;

-- Create trigger to keep type and event_type in sync going forward
CREATE OR REPLACE FUNCTION sync_event_type()
RETURNS TRIGGER AS $$
BEGIN
    -- If type is set, also set event_type (for backward compatibility)
    IF NEW.type IS NOT NULL AND (NEW.event_type IS NULL OR NEW.event_type != NEW.type) THEN
        NEW.event_type := NEW.type;
    END IF;
    -- If event_type is set, also set type (for new column)
    IF NEW.event_type IS NOT NULL AND (NEW.type IS NULL OR NEW.type != NEW.event_type) THEN
        NEW.type := NEW.event_type;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Drop trigger if it exists and recreate
DROP TRIGGER IF EXISTS trigger_sync_event_type ON events;
CREATE TRIGGER trigger_sync_event_type
    BEFORE INSERT OR UPDATE ON events
    FOR EACH ROW
    EXECUTE FUNCTION sync_event_type();

-- ============================================================================
-- ADD INDEXES FOR EFFICIENT QUERIES
-- ============================================================================

-- Index on task_id for task-related event queries
CREATE INDEX IF NOT EXISTS idx_events_task_id ON events(task_id) WHERE task_id IS NOT NULL;

-- Index on type for event type filtering
CREATE INDEX IF NOT EXISTS idx_events_type ON events(type) WHERE type IS NOT NULL;

-- Composite index for common query pattern: team_id + task_id + created_at
CREATE INDEX IF NOT EXISTS idx_events_team_task_created ON events(team_id, task_id, created_at DESC) WHERE task_id IS NOT NULL;

-- Composite index for event type queries: team_id + type + created_at
CREATE INDEX IF NOT EXISTS idx_events_team_type_created ON events(team_id, type, created_at DESC) WHERE type IS NOT NULL;

-- ============================================================================
-- VERIFY TASKS TABLE HAS REQUIRED FIELDS
-- ============================================================================

-- Verify column_key exists (should already be added by migration 004)
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'tasks' AND column_name = 'column_key'
    ) THEN
        RAISE EXCEPTION 'column_key field missing from tasks table. Please run migration 004 first.';
    END IF;
END $$;

-- Verify required fields exist in tasks table
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'tasks' AND column_name = 'team_id'
    ) THEN
        RAISE EXCEPTION 'team_id field missing from tasks table';
    END IF;
    
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'tasks' AND column_name = 'parent_id'
    ) THEN
        RAISE EXCEPTION 'parent_id field missing from tasks table';
    END IF;
    
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'tasks' AND column_name = 'assignee_type'
    ) THEN
        RAISE EXCEPTION 'assignee_type field missing from tasks table';
    END IF;
    
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'tasks' AND column_name = 'assignment_risk'
    ) THEN
        RAISE EXCEPTION 'assignment_risk field missing from tasks table';
    END IF;
    
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'tasks' AND column_name = 'tags'
    ) THEN
        RAISE EXCEPTION 'tags field missing from tasks table. Please run migration 005 first.';
    END IF;
    
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'tasks' AND column_name = 'updated_at'
    ) THEN
        RAISE EXCEPTION 'updated_at field missing from tasks table';
    END IF;
END $$;

-- ============================================================================
-- ADD INDEXES FOR TASK STATUS QUERIES
-- ============================================================================

-- Index on column_key for efficient task status lookups
CREATE INDEX IF NOT EXISTS idx_tasks_column_key ON tasks(column_key) WHERE column_key IS NOT NULL;

-- Composite index for WIP count calculations: team_id + column_key
CREATE INDEX IF NOT EXISTS idx_tasks_team_column_key ON tasks(team_id, column_key) WHERE column_key IS NOT NULL;

-- Index on updated_at for efficient status change history queries
CREATE INDEX IF NOT EXISTS idx_tasks_updated_at_status ON tasks(team_id, updated_at DESC) WHERE column_key IS NOT NULL;
