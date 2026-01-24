-- Enforce Task Hierarchy Constraints
-- Adds database-level constraints and validation for parent-subtask relationships

-- ============================================================================
-- ADD CONSTRAINT: Parent and subtask must share same team_id
-- ============================================================================

-- Create a function to check that parent and child tasks are in the same team
CREATE OR REPLACE FUNCTION check_parent_child_team_match()
RETURNS TRIGGER AS $$
BEGIN
    -- If parent_id is set, verify parent exists and has same team_id
    IF NEW.parent_id IS NOT NULL THEN
        IF NOT EXISTS (
            SELECT 1 FROM tasks
            WHERE id = NEW.parent_id AND team_id = NEW.team_id
        ) THEN
            RAISE EXCEPTION 'Parent task must belong to the same team as the subtask';
        END IF;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger to enforce team matching
DROP TRIGGER IF EXISTS trigger_check_parent_child_team ON tasks;
CREATE TRIGGER trigger_check_parent_child_team
    BEFORE INSERT OR UPDATE ON tasks
    FOR EACH ROW
    EXECUTE FUNCTION check_parent_child_team_match();

-- ============================================================================
-- VERIFY PARENT_ID FIELD EXISTS
-- ============================================================================

DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'tasks' AND column_name = 'parent_id'
    ) THEN
        RAISE EXCEPTION 'parent_id field missing from tasks table. Please run migration 002 first.';
    END IF;
END $$;

-- ============================================================================
-- VERIFY FOREIGN KEY CONSTRAINT EXISTS
-- ============================================================================

DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'tasks_parent_id_fkey'
        AND conrelid = 'tasks'::regclass
    ) THEN
        -- Add foreign key constraint if it doesn't exist
        ALTER TABLE tasks
        ADD CONSTRAINT tasks_parent_id_fkey
        FOREIGN KEY (parent_id) REFERENCES tasks(id) ON DELETE CASCADE;
    END IF;
END $$;

-- ============================================================================
-- COMMENTS
-- ============================================================================

COMMENT ON COLUMN tasks.parent_id IS 'Parent task ID for hierarchical structure. Subtasks must belong to the same team as their parent. Only single-level hierarchy is supported (subtasks cannot have their own subtasks).';
