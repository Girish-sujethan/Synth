-- Add approval field to tasks table for AI task approval system
-- This allows tracking whether AI-assigned tasks have been approved by humans

ALTER TABLE tasks ADD COLUMN IF NOT EXISTS approved BOOLEAN DEFAULT FALSE;
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS approved_at TIMESTAMPTZ;
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS approved_by TEXT;  -- References Supabase auth.users.id
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS approval_comment TEXT;

-- Create index for querying approved tasks
CREATE INDEX IF NOT EXISTS idx_tasks_approved ON tasks(team_id, approved) WHERE approved = TRUE;
