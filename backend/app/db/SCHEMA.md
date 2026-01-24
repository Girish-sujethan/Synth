# Database Schema Documentation

## Overview

This document describes the core database schema for the team-based task management system. All tables are team-scoped, supporting a multi-tenant architecture.

## Enum Types

### `assignee_type`
- `user` - Task assigned to a user
- `agent` - Task assigned to an AI agent
- `unassigned` - Task not yet assigned

### `assignment_risk`
- `low` - Low risk assignment
- `medium` - Medium risk assignment
- `high` - High risk assignment

### `level`
- `junior` - Junior level
- `mid` - Mid level
- `senior` - Senior level
- `staff` - Staff level
- `principal` - Principal level

### `team_role`
- `admin` - Full administrative access
- `manager` - Can create/edit/orchestrate tasks
- `member` - Can create own tasks
- `viewer` - Read-only access

## Tables

### `teams`
Core team entity.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Team identifier |
| name | TEXT | NOT NULL | Team name |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | Creation timestamp |
| updated_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | Last update timestamp |

### `team_members`
Team membership with role-based access control.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Member identifier |
| team_id | UUID | NOT NULL, FK → teams(id) | Team reference |
| user_id | TEXT | NOT NULL | Supabase auth user ID |
| role | team_role | NOT NULL, DEFAULT 'member' | Member role |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | Creation timestamp |
| updated_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | Last update timestamp |

**Unique Constraint**: `(team_id, user_id)` - A user can only be a member of a team once.

### `profiles`
User profiles with skills and performance metrics.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Profile identifier |
| user_id | TEXT | NOT NULL, UNIQUE | Supabase auth user ID |
| team_id | UUID | NOT NULL, FK → teams(id) | Team reference |
| name | TEXT | | User name |
| email | TEXT | | User email |
| skills | JSONB | DEFAULT '{}' | User skills as JSON |
| level | level | | User level |
| velocity | FLOAT | DEFAULT 0.0 | Work velocity metric |
| load | FLOAT | DEFAULT 0.0 | Current work load |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | Creation timestamp |
| updated_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | Last update timestamp |

**Unique Constraints**: 
- `user_id` - One profile per user globally
- `(team_id, user_id)` - One profile per user per team

### `ai_agents`
AI agent configurations.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Agent identifier |
| team_id | UUID | NOT NULL, FK → teams(id) | Team reference |
| name | TEXT | NOT NULL | Agent name |
| capabilities_md | TEXT | | Markdown description of capabilities |
| limits_md | TEXT | | Markdown description of limits |
| tags | TEXT[] | DEFAULT '{}' | Agent tags |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | Creation timestamp |
| updated_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | Last update timestamp |

### `board_columns`
Workflow board column configuration.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Column identifier |
| team_id | UUID | NOT NULL, FK → teams(id) | Team reference |
| name | TEXT | NOT NULL | Column name |
| position | INTEGER | NOT NULL | Column position in board |
| workflow_config | JSONB | DEFAULT '{}' | Workflow configuration |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | Creation timestamp |
| updated_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | Last update timestamp |

**Unique Constraint**: `(team_id, position)` - Each position in a team's board is unique.

### `tasks`
Tasks with hierarchical structure and assignment tracking.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Task identifier |
| team_id | UUID | NOT NULL, FK → teams(id) | Team reference |
| parent_id | UUID | FK → tasks(id) | Parent task (for hierarchy) |
| title | TEXT | NOT NULL | Task title |
| description | TEXT | | Task description |
| status | TEXT | | Task status |
| size | INTEGER | | Task size (Fibonacci: 1, 2, 3, 5, 8, 13) |
| tags | TEXT[] | DEFAULT '{}' | Task tags array |
| assignee_type | assignee_type | DEFAULT 'unassigned' | Type of assignee |
| assignee_id | UUID | | Assignee ID (user or agent) |
| assignment_risk | assignment_risk | | Assignment risk level |
| column_id | UUID | FK → board_columns(id) | Board column reference |
| column_key | TEXT | | Board column key (stable identifier) |
| override_flag | BOOLEAN | DEFAULT FALSE | Override flag |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | Creation timestamp |
| updated_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | Last update timestamp |

**Constraints**:
- `size` must be one of: 1, 2, 3, 5, 8, 13 (Fibonacci sequence) or NULL
- `tags` is stored as a TEXT array, typically lowercase

**Hierarchical Structure**: Tasks can have parent tasks via `parent_id`, enabling task hierarchies and subtasks.

**Hierarchy Constraints**:
- `parent_id` must reference a valid task in the same team (enforced by database trigger)
- Only single-level hierarchy is supported (subtasks cannot have their own subtasks)
- Recursive relationships are prevented (subtasks cannot become parents of their ancestors)
- When a parent task is deleted, all subtasks are automatically deleted (CASCADE)

### `events`
Audit logging for team activities.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Event identifier |
| team_id | UUID | NOT NULL, FK → teams(id) | Team reference |
| task_id | UUID | FK → tasks(id) | Related task ID (nullable) |
| event_type | TEXT | NOT NULL | Event type (legacy, synced with type) |
| type | TEXT | | Event type (synced with event_type via trigger) |
| payload | JSONB | DEFAULT '{}' | Event payload data |
| user_id | TEXT | | Supabase auth user ID |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | Event timestamp |

**Event Types**:
- `task_moved`: Task moved between columns
  - Payload fields: `from_column`, `from_column_key`, `to_column`, `to_column_key`, `actor_user_id`, `reason`, `note`, `client_action`

**Indexes**:
- `idx_events_task_id`: For task-related event queries
- `idx_events_type`: For event type filtering
- `idx_events_team_task_created`: Composite index for team + task + timestamp queries
- `idx_events_team_type_created`: Composite index for team + type + timestamp queries

### `policies`
Team policies stored as markdown.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Policy identifier |
| team_id | UUID | NOT NULL, FK → teams(id) | Team reference |
| name | TEXT | NOT NULL | Policy name |
| policy_md | TEXT | | Markdown policy content |
| description_md | TEXT | | Markdown description |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | Creation timestamp |
| updated_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | Last update timestamp |

## Relationships

### Foreign Key Relationships

- `team_members.team_id` → `teams.id` (CASCADE on delete)
- `profiles.team_id` → `teams.id` (CASCADE on delete)
- `ai_agents.team_id` → `teams.id` (CASCADE on delete)
- `board_columns.team_id` → `teams.id` (CASCADE on delete)
- `tasks.team_id` → `teams.id` (CASCADE on delete)
- `tasks.parent_id` → `tasks.id` (CASCADE on delete) - Hierarchical structure
- `tasks.column_id` → `board_columns.id` (SET NULL on delete)
- `events.team_id` → `teams.id` (CASCADE on delete)
- `policies.team_id` → `teams.id` (CASCADE on delete)

## Indexes

Indexes are created on:
- `team_members(team_id, user_id)`
- `profiles(team_id, user_id)`
- `ai_agents(team_id)`
- `board_columns(team_id)`
- `tasks(team_id, parent_id, assignee_id, column_id)`
- `events(team_id, created_at)`
- `policies(team_id)`

## Design Principles

1. **Team-Scoped Architecture**: All tables (except `teams`) reference a `team_id`, ensuring data isolation between teams.

2. **Hierarchical Tasks**: Tasks support parent-child relationships via `parent_id`, enabling subtasks and task hierarchies.

3. **Flexible Data Storage**: JSONB columns (`skills`, `payload`, `workflow_config`) allow flexible, schema-less data storage.

4. **Markdown Policies**: Policies are stored as markdown text, enabling runtime configurability without code changes.

5. **Audit Trail**: The `events` table provides comprehensive audit logging for all team activities.

6. **Role-Based Access**: Team membership includes role information, supporting fine-grained access control.
