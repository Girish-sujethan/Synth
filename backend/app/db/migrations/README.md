# Database Migrations

This directory contains SQL migration files for setting up the database schema and Row Level Security policies.

## Migration Files

1. **001_create_enums.sql** - Creates all required enum types:
   - `assignee_type`: user, agent, unassigned
   - `assignment_risk`: low, medium, high
   - `level`: junior, mid, senior, staff, principal
   - `team_role`: admin, manager, member, viewer

2. **002_create_core_tables.sql** - Creates all core tables:

3. **004_add_column_management.sql** - Adds column management features:
   - Adds key, display_name, wip_limit, is_locked to board_columns
   - Adds column_key to tasks table
   - Creates default columns for teams
   - Adds constraints and triggers for column limits

4. **005_add_task_size_and_tags.sql** - Adds size and tags to tasks:
   - Adds size column with Fibonacci constraint (1, 2, 3, 5, 8, 13)
   - Adds tags column as TEXT array
   - Creates indexes for performance

5. **006_add_task_status_audit_events.sql** - Extends events table for task status tracking:
   - Adds task_id column to events table (FK to tasks)
   - Adds type column (synced with event_type via trigger)
   - Creates indexes for efficient task status and event queries
   - Verifies required fields exist in tasks table
   - Adds indexes for WIP count calculations and status lookups

6. **007_enforce_task_hierarchy.sql** - Enforces task hierarchy constraints:
   - Adds database trigger to ensure parent and subtask share same team_id
   - Verifies parent_id field and foreign key constraint exist
   - Adds constraint to prevent invalid parent-child relationships

3. **003_enable_rls.sql** - Enables Row Level Security and creates policies:
   - Helper functions for team membership and role checks
   - RLS policies for all tables with role-based access control
   - Team isolation enforcement
   - Append-only events table

4. **000_initial_schema.sql** - Combined migration for easy setup

## Running Migrations

### Using Supabase Dashboard

1. Go to your Supabase project dashboard
2. Navigate to SQL Editor
3. Run each migration file in order:
   - 001_create_enums.sql
   - 002_create_core_tables.sql
   - 003_enable_rls.sql

Or run the combined file:
   - 000_initial_schema.sql (does not include RLS - run 003 separately)

### Using psql

```bash
psql $DATABASE_URL -f backend/app/db/migrations/001_create_enums.sql
psql $DATABASE_URL -f backend/app/db/migrations/002_create_core_tables.sql
psql $DATABASE_URL -f backend/app/db/migrations/003_enable_rls.sql
```

### Using Supabase CLI

```bash
supabase db push
```

## RLS Policy Overview

### Access Control Matrix

| Table | Select | Insert | Update | Delete |
|-------|--------|--------|---------|--------|
| teams | Team members | Authenticated | Admins | Admins |
| team_members | Team members | Admins | Admins | Admins |
| profiles | Team members | Own profile | Own/Admins | Admins |
| tasks | Team members | Team members | Team members | Managers/Admins |
| board_columns | Team members | Admins | Admins | Admins |
| ai_agents | Team members | Managers/Admins | Managers/Admins | Managers/Admins |
| policies | Team members | Admins | Admins | Admins |
| events | Team members | Team members | - | - |

### Role Hierarchy

- **Admin**: Full CRUD access within teams
- **Manager**: Read access + write access to tasks and AI agents
- **Member**: Read access + create tasks
- **Viewer**: Read-only access

### Helper Functions

- `is_team_member(team_id, user_id)` - Check team membership
- `get_user_team_role(team_id, user_id)` - Get user's role in team
- `is_team_admin(team_id, user_id)` - Check if user is admin
- `is_team_manager_or_admin(team_id, user_id)` - Check if user is manager or admin

## Schema Overview

### Core Relationships

- All tables are team-scoped (except teams itself)
- `team_members` links users to teams with roles
- `profiles` stores user information per team
- `tasks` support hierarchical structure via `parent_id`
- `events` provides audit logging for all team activities
- `policies` store team-specific policies as markdown

### Key Constraints

- `team_members`: Unique constraint on (team_id, user_id)
- `profiles`: Unique constraint on (team_id, user_id)
- `board_columns`: Unique constraint on (team_id, position)
- All foreign keys have appropriate CASCADE or SET NULL behavior
