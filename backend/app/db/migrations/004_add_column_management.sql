-- Column Management Schema Updates
-- Adds column_key to tasks and updates board_columns structure

-- ============================================================================
-- UPDATE BOARD_COLUMNS TABLE
-- ============================================================================

-- Add key field if it doesn't exist
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'board_columns' AND column_name = 'key'
    ) THEN
        ALTER TABLE board_columns ADD COLUMN key TEXT;
    END IF;
END $$;

-- Add display_name field if it doesn't exist
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'board_columns' AND column_name = 'display_name'
    ) THEN
        ALTER TABLE board_columns ADD COLUMN display_name TEXT;
    END IF;
END $$;

-- Add wip_limit field if it doesn't exist
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'board_columns' AND column_name = 'wip_limit'
    ) THEN
        ALTER TABLE board_columns ADD COLUMN wip_limit INTEGER;
    END IF;
END $$;

-- Add is_locked field if it doesn't exist
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'board_columns' AND column_name = 'is_locked'
    ) THEN
        ALTER TABLE board_columns ADD COLUMN is_locked BOOLEAN DEFAULT FALSE;
    END IF;
END $$;

-- Update display_name to use name if display_name is null
UPDATE board_columns SET display_name = name WHERE display_name IS NULL;

-- Update key to use lowercase slug of name if key is null
UPDATE board_columns 
SET key = LOWER(REGEXP_REPLACE(name, '[^a-zA-Z0-9]+', '-', 'g'))
WHERE key IS NULL;

-- Add unique constraint on (team_id, key)
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'board_columns_team_id_key_unique'
    ) THEN
        ALTER TABLE board_columns 
        ADD CONSTRAINT board_columns_team_id_key_unique 
        UNIQUE (team_id, key);
    END IF;
END $$;

-- ============================================================================
-- UPDATE TASKS TABLE
-- ============================================================================

-- Add column_key field if it doesn't exist
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'tasks' AND column_name = 'column_key'
    ) THEN
        ALTER TABLE tasks ADD COLUMN column_key TEXT;
    END IF;
END $$;

-- Migrate existing column_id references to column_key
UPDATE tasks t
SET column_key = (
    SELECT bc.key 
    FROM board_columns bc 
    WHERE bc.id = t.column_id
)
WHERE t.column_id IS NOT NULL AND t.column_key IS NULL;

-- ============================================================================
-- ADD INDEXES
-- ============================================================================

-- Index on board_columns.key for lookups
CREATE INDEX IF NOT EXISTS idx_board_columns_key ON board_columns(key);
CREATE INDEX IF NOT EXISTS idx_board_columns_team_id_key ON board_columns(team_id, key);

-- Index on tasks.column_key
CREATE INDEX IF NOT EXISTS idx_tasks_column_key ON tasks(column_key);

-- ============================================================================
-- ADD CHECK CONSTRAINT FOR COLUMN LIMIT
-- ============================================================================

-- Function to check column count per team
CREATE OR REPLACE FUNCTION check_team_column_limit()
RETURNS TRIGGER AS $$
DECLARE
    column_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO column_count
    FROM board_columns
    WHERE team_id = NEW.team_id;
    
    IF column_count > 8 THEN
        RAISE EXCEPTION 'Team cannot have more than 8 columns';
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to enforce column limit
DROP TRIGGER IF EXISTS trigger_check_column_limit ON board_columns;
CREATE TRIGGER trigger_check_column_limit
    BEFORE INSERT ON board_columns
    FOR EACH ROW
    EXECUTE FUNCTION check_team_column_limit();

-- ============================================================================
-- FUNCTION TO VALIDATE COLUMN KEY FORMAT
-- ============================================================================

CREATE OR REPLACE FUNCTION validate_column_key(key_value TEXT)
RETURNS BOOLEAN AS $$
BEGIN
    -- Check if key is lowercase slug format (alphanumeric and hyphens only)
    RETURN key_value ~ '^[a-z0-9-]+$' AND LENGTH(key_value) > 0;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- DEFAULT COLUMNS FOR EXISTING TEAMS
-- ============================================================================

-- Function to create default columns for a team
CREATE OR REPLACE FUNCTION create_default_columns(team_uuid UUID)
RETURNS VOID AS $$
BEGIN
    -- Only create if team doesn't have columns yet
    IF NOT EXISTS (SELECT 1 FROM board_columns WHERE team_id = team_uuid) THEN
        INSERT INTO board_columns (team_id, key, name, display_name, position, wip_limit, is_locked)
        VALUES
            (team_uuid, 'backlog', 'Backlog', 'Backlog', 0, NULL, false),
            (team_uuid, 'doing', 'Doing', 'Doing', 1, 5, false),
            (team_uuid, 'review', 'Review', 'Review', 2, NULL, false),
            (team_uuid, 'done', 'Done', 'Done', 3, NULL, true);
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Create default columns for all existing teams
DO $$
DECLARE
    team_record RECORD;
BEGIN
    FOR team_record IN SELECT id FROM teams LOOP
        PERFORM create_default_columns(team_record.id);
    END LOOP;
END $$;

-- ============================================================================
-- TRIGGER TO AUTO-CREATE DEFAULT COLUMNS FOR NEW TEAMS
-- ============================================================================

CREATE OR REPLACE FUNCTION auto_create_default_columns()
RETURNS TRIGGER AS $$
BEGIN
    PERFORM create_default_columns(NEW.id);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_auto_create_columns ON teams;
CREATE TRIGGER trigger_auto_create_columns
    AFTER INSERT ON teams
    FOR EACH ROW
    EXECUTE FUNCTION auto_create_default_columns();
