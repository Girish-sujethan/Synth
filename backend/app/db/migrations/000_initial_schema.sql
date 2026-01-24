-- Combined initial schema migration
-- This file combines all migrations for easy setup
-- Run this file to create the complete database schema

-- ============================================================================
-- ENUMS
-- ============================================================================

-- Assignee type enum for task assignments
CREATE TYPE IF NOT EXISTS assignee_type AS ENUM ('user', 'agent', 'unassigned');

-- Assignment risk level enum
CREATE TYPE IF NOT EXISTS assignment_risk AS ENUM ('low', 'medium', 'high');

-- User level enum for profiles
CREATE TYPE IF NOT EXISTS level AS ENUM ('junior', 'mid', 'senior', 'staff', 'principal');

-- Team member role enum (matches UserRole in Python)
CREATE TYPE IF NOT EXISTS team_role AS ENUM ('admin', 'manager', 'member', 'viewer');

-- ============================================================================
-- TABLES
-- ============================================================================

-- Teams table
CREATE TABLE IF NOT EXISTS teams (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Team members table
CREATE TABLE IF NOT EXISTS team_members (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    team_id UUID NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
    user_id TEXT NOT NULL,  -- References Supabase auth.users.id
    role team_role NOT NULL DEFAULT 'member',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(team_id, user_id)
);

-- Profiles table
CREATE TABLE IF NOT EXISTS profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL UNIQUE,  -- References Supabase auth.users.id
    team_id UUID NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
    name TEXT,
    email TEXT,
    skills JSONB DEFAULT '{}'::jsonb,
    level level,
    velocity FLOAT DEFAULT 0.0,
    load FLOAT DEFAULT 0.0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(team_id, user_id)
);

-- AI Agents table
CREATE TABLE IF NOT EXISTS ai_agents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    team_id UUID NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    capabilities_md TEXT,  -- Markdown description of capabilities
    limits_md TEXT,  -- Markdown description of limits
    tags TEXT[] DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Board columns table for workflow configuration
CREATE TABLE IF NOT EXISTS board_columns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    team_id UUID NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    position INTEGER NOT NULL,
    workflow_config JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(team_id, position)
);

-- Tasks table with hierarchical structure
CREATE TABLE IF NOT EXISTS tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    team_id UUID NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
    parent_id UUID REFERENCES tasks(id) ON DELETE CASCADE,  -- Hierarchical structure
    title TEXT NOT NULL,
    description TEXT,
    status TEXT,
    assignee_type assignee_type DEFAULT 'unassigned',
    assignee_id UUID,  -- Can reference user_id or ai_agent_id
    assignment_risk assignment_risk,
    column_id UUID REFERENCES board_columns(id) ON DELETE SET NULL,
    override_flag BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Events table for audit logging
CREATE TABLE IF NOT EXISTS events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    team_id UUID NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
    event_type TEXT NOT NULL,
    payload JSONB DEFAULT '{}'::jsonb,
    user_id TEXT,  -- References Supabase auth.users.id
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Policies table with markdown fields
CREATE TABLE IF NOT EXISTS policies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    team_id UUID NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    policy_md TEXT,  -- Markdown policy content
    description_md TEXT,  -- Markdown description
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ============================================================================
-- INDEXES
-- ============================================================================

-- Team members indexes
CREATE INDEX IF NOT EXISTS idx_team_members_team_id ON team_members(team_id);
CREATE INDEX IF NOT EXISTS idx_team_members_user_id ON team_members(user_id);

-- Profiles indexes
CREATE INDEX IF NOT EXISTS idx_profiles_team_id ON profiles(team_id);
CREATE INDEX IF NOT EXISTS idx_profiles_user_id ON profiles(user_id);

-- AI agents indexes
CREATE INDEX IF NOT EXISTS idx_ai_agents_team_id ON ai_agents(team_id);

-- Board columns indexes
CREATE INDEX IF NOT EXISTS idx_board_columns_team_id ON board_columns(team_id);

-- Tasks indexes
CREATE INDEX IF NOT EXISTS idx_tasks_team_id ON tasks(team_id);
CREATE INDEX IF NOT EXISTS idx_tasks_parent_id ON tasks(parent_id);
CREATE INDEX IF NOT EXISTS idx_tasks_assignee_id ON tasks(assignee_id);
CREATE INDEX IF NOT EXISTS idx_tasks_column_id ON tasks(column_id);

-- Events indexes
CREATE INDEX IF NOT EXISTS idx_events_team_id ON events(team_id);
CREATE INDEX IF NOT EXISTS idx_events_created_at ON events(created_at);

-- Policies indexes
CREATE INDEX IF NOT EXISTS idx_policies_team_id ON policies(team_id);
