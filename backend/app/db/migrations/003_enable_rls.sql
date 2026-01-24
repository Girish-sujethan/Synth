-- Row Level Security (RLS) Policies
-- This migration enables RLS and creates policies for all tables

-- ============================================================================
-- HELPER FUNCTIONS
-- ============================================================================

-- Function to check if user is a member of a team
CREATE OR REPLACE FUNCTION is_team_member(team_uuid UUID, user_uuid TEXT)
RETURNS BOOLEAN AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1 FROM team_members
        WHERE team_id = team_uuid
        AND user_id = user_uuid
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to get user's role in a team
CREATE OR REPLACE FUNCTION get_user_team_role(team_uuid UUID, user_uuid TEXT)
RETURNS team_role AS $$
DECLARE
    user_role team_role;
BEGIN
    SELECT role INTO user_role
    FROM team_members
    WHERE team_id = team_uuid
    AND user_id = user_uuid;
    
    RETURN user_role;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to check if user is admin in a team
CREATE OR REPLACE FUNCTION is_team_admin(team_uuid UUID, user_uuid TEXT)
RETURNS BOOLEAN AS $$
BEGIN
    RETURN get_user_team_role(team_uuid, user_uuid) = 'admin';
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to check if user is manager or admin in a team
CREATE OR REPLACE FUNCTION is_team_manager_or_admin(team_uuid UUID, user_uuid TEXT)
RETURNS BOOLEAN AS $$
DECLARE
    user_role team_role;
BEGIN
    SELECT role INTO user_role
    FROM team_members
    WHERE team_id = team_uuid
    AND user_id = user_uuid;
    
    RETURN user_role IN ('admin', 'manager');
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ============================================================================
-- ENABLE RLS ON ALL TABLES
-- ============================================================================

ALTER TABLE teams ENABLE ROW LEVEL SECURITY;
ALTER TABLE team_members ENABLE ROW LEVEL SECURITY;
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai_agents ENABLE ROW LEVEL SECURITY;
ALTER TABLE board_columns ENABLE ROW LEVEL SECURITY;
ALTER TABLE tasks ENABLE ROW LEVEL SECURITY;
ALTER TABLE events ENABLE ROW LEVEL SECURITY;
ALTER TABLE policies ENABLE ROW LEVEL SECURITY;

-- ============================================================================
-- TEAMS TABLE POLICIES
-- ============================================================================

-- Users can read teams they are members of
CREATE POLICY "teams_select_policy" ON teams
    FOR SELECT
    USING (
        is_team_member(id, auth.uid()::TEXT)
    );

-- Only admins can create teams (via service role, typically)
-- For now, allow authenticated users to create teams
CREATE POLICY "teams_insert_policy" ON teams
    FOR INSERT
    WITH CHECK (auth.role() = 'authenticated');

-- Only admins can update teams
CREATE POLICY "teams_update_policy" ON teams
    FOR UPDATE
    USING (
        is_team_admin(id, auth.uid()::TEXT)
    )
    WITH CHECK (
        is_team_admin(id, auth.uid()::TEXT)
    );

-- Only admins can delete teams
CREATE POLICY "teams_delete_policy" ON teams
    FOR DELETE
    USING (
        is_team_admin(id, auth.uid()::TEXT)
    );

-- ============================================================================
-- TEAM_MEMBERS TABLE POLICIES
-- ============================================================================

-- Team members can read members of teams they belong to
CREATE POLICY "team_members_select_policy" ON team_members
    FOR SELECT
    USING (
        is_team_member(team_id, auth.uid()::TEXT)
    );

-- Only admins can add team members
CREATE POLICY "team_members_insert_policy" ON team_members
    FOR INSERT
    WITH CHECK (
        is_team_admin(team_id, auth.uid()::TEXT)
    );

-- Only admins can update team members
CREATE POLICY "team_members_update_policy" ON team_members
    FOR UPDATE
    USING (
        is_team_admin(team_id, auth.uid()::TEXT)
    )
    WITH CHECK (
        is_team_admin(team_id, auth.uid()::TEXT)
    );

-- Only admins can remove team members
CREATE POLICY "team_members_delete_policy" ON team_members
    FOR DELETE
    USING (
        is_team_admin(team_id, auth.uid()::TEXT)
    );

-- ============================================================================
-- PROFILES TABLE POLICIES
-- ============================================================================

-- Team members can read profiles of their team
CREATE POLICY "profiles_select_policy" ON profiles
    FOR SELECT
    USING (
        is_team_member(team_id, auth.uid()::TEXT)
    );

-- Users can create their own profile in a team they belong to
CREATE POLICY "profiles_insert_policy" ON profiles
    FOR INSERT
    WITH CHECK (
        user_id = auth.uid()::TEXT
        AND is_team_member(team_id, auth.uid()::TEXT)
    );

-- Users can update their own profile, admins can update any profile in their team
CREATE POLICY "profiles_update_policy" ON profiles
    FOR UPDATE
    USING (
        user_id = auth.uid()::TEXT
        OR is_team_admin(team_id, auth.uid()::TEXT)
    )
    WITH CHECK (
        user_id = auth.uid()::TEXT
        OR is_team_admin(team_id, auth.uid()::TEXT)
    );

-- Only admins can delete profiles
CREATE POLICY "profiles_delete_policy" ON profiles
    FOR DELETE
    USING (
        is_team_admin(team_id, auth.uid()::TEXT)
    );

-- ============================================================================
-- TASKS TABLE POLICIES
-- ============================================================================

-- Team members can read tasks in their team
CREATE POLICY "tasks_select_policy" ON tasks
    FOR SELECT
    USING (
        is_team_member(team_id, auth.uid()::TEXT)
    );

-- Members can create tasks in their team
CREATE POLICY "tasks_insert_policy" ON tasks
    FOR INSERT
    WITH CHECK (
        is_team_member(team_id, auth.uid()::TEXT)
    );

-- Team members can update tasks in their team
-- (Application logic should enforce creator-only or manager/admin restrictions)
CREATE POLICY "tasks_update_policy" ON tasks
    FOR UPDATE
    USING (
        is_team_member(team_id, auth.uid()::TEXT)
    )
    WITH CHECK (
        is_team_member(team_id, auth.uid()::TEXT)
    );

-- Only admins and managers can delete tasks
CREATE POLICY "tasks_delete_policy" ON tasks
    FOR DELETE
    USING (
        is_team_manager_or_admin(team_id, auth.uid()::TEXT)
    );

-- ============================================================================
-- BOARD_COLUMNS TABLE POLICIES
-- ============================================================================

-- Team members can read board columns of their team
CREATE POLICY "board_columns_select_policy" ON board_columns
    FOR SELECT
    USING (
        is_team_member(team_id, auth.uid()::TEXT)
    );

-- Only admins can create board columns
CREATE POLICY "board_columns_insert_policy" ON board_columns
    FOR INSERT
    WITH CHECK (
        is_team_admin(team_id, auth.uid()::TEXT)
    );

-- Only admins can update board columns
CREATE POLICY "board_columns_update_policy" ON board_columns
    FOR UPDATE
    USING (
        is_team_admin(team_id, auth.uid()::TEXT)
    )
    WITH CHECK (
        is_team_admin(team_id, auth.uid()::TEXT)
    );

-- Only admins can delete board columns
CREATE POLICY "board_columns_delete_policy" ON board_columns
    FOR DELETE
    USING (
        is_team_admin(team_id, auth.uid()::TEXT)
    );

-- ============================================================================
-- AI_AGENTS TABLE POLICIES
-- ============================================================================

-- Team members can read AI agents of their team
CREATE POLICY "ai_agents_select_policy" ON ai_agents
    FOR SELECT
    USING (
        is_team_member(team_id, auth.uid()::TEXT)
    );

-- Admins and managers can create AI agents
CREATE POLICY "ai_agents_insert_policy" ON ai_agents
    FOR INSERT
    WITH CHECK (
        is_team_manager_or_admin(team_id, auth.uid()::TEXT)
    );

-- Admins and managers can update AI agents
CREATE POLICY "ai_agents_update_policy" ON ai_agents
    FOR UPDATE
    USING (
        is_team_manager_or_admin(team_id, auth.uid()::TEXT)
    )
    WITH CHECK (
        is_team_manager_or_admin(team_id, auth.uid()::TEXT)
    );

-- Admins and managers can delete AI agents
CREATE POLICY "ai_agents_delete_policy" ON ai_agents
    FOR DELETE
    USING (
        is_team_manager_or_admin(team_id, auth.uid()::TEXT)
    );

-- ============================================================================
-- POLICIES TABLE POLICIES
-- ============================================================================

-- Team members can read policies of their team
CREATE POLICY "policies_select_policy" ON policies
    FOR SELECT
    USING (
        is_team_member(team_id, auth.uid()::TEXT)
    );

-- Only admins can create policies
CREATE POLICY "policies_insert_policy" ON policies
    FOR INSERT
    WITH CHECK (
        is_team_admin(team_id, auth.uid()::TEXT)
    );

-- Only admins can update policies
CREATE POLICY "policies_update_policy" ON policies
    FOR UPDATE
    USING (
        is_team_admin(team_id, auth.uid()::TEXT)
    )
    WITH CHECK (
        is_team_admin(team_id, auth.uid()::TEXT)
    );

-- Only admins can delete policies
CREATE POLICY "policies_delete_policy" ON policies
    FOR DELETE
    USING (
        is_team_admin(team_id, auth.uid()::TEXT)
    );

-- ============================================================================
-- EVENTS TABLE POLICIES (APPEND-ONLY)
-- ============================================================================

-- Team members can read events of their team
CREATE POLICY "events_select_policy" ON events
    FOR SELECT
    USING (
        is_team_member(team_id, auth.uid()::TEXT)
    );

-- Team members can create events (append-only)
CREATE POLICY "events_insert_policy" ON events
    FOR INSERT
    WITH CHECK (
        is_team_member(team_id, auth.uid()::TEXT)
    );

-- Events are append-only: no update or delete policies
