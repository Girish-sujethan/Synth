# Row Level Security (RLS) Policies Documentation

## Overview

This document describes the Row Level Security policies implemented for the team-based task management system. RLS ensures that users can only access data for teams they belong to and perform actions appropriate to their role level.

## Helper Functions

### `is_team_member(team_uuid UUID, user_uuid TEXT)`
Returns `TRUE` if the user is a member of the specified team.

### `get_user_team_role(team_uuid UUID, user_uuid TEXT)`
Returns the user's role (`admin`, `manager`, `member`, or `viewer`) in the specified team.

### `is_team_admin(team_uuid UUID, user_uuid TEXT)`
Returns `TRUE` if the user is an admin in the specified team.

### `is_team_manager_or_admin(team_uuid UUID, user_uuid TEXT)`
Returns `TRUE` if the user is a manager or admin in the specified team.

## Table Policies

### Teams

- **SELECT**: Team members can read teams they are members of
- **INSERT**: Authenticated users can create teams
- **UPDATE**: Only admins can update teams
- **DELETE**: Only admins can delete teams

### Team Members

- **SELECT**: Team members can read members of teams they belong to
- **INSERT**: Only admins can add team members
- **UPDATE**: Only admins can update team members (e.g., change roles)
- **DELETE**: Only admins can remove team members

### Profiles

- **SELECT**: Team members can read profiles of their team
- **INSERT**: Users can create their own profile in a team they belong to
- **UPDATE**: Users can update their own profile; admins can update any profile in their team
- **DELETE**: Only admins can delete profiles

### Tasks

- **SELECT**: Team members can read tasks in their team
- **INSERT**: Team members can create tasks in their team
- **UPDATE**: Team members can update tasks in their team
  - *Note: Application logic should enforce creator-only or manager/admin restrictions if needed*
- **DELETE**: Only managers and admins can delete tasks

### Board Columns

- **SELECT**: Team members can read board columns of their team
- **INSERT**: Only admins can create board columns
- **UPDATE**: Only admins can update board columns
- **DELETE**: Only admins can delete board columns

### AI Agents

- **SELECT**: Team members can read AI agents of their team
- **INSERT**: Admins and managers can create AI agents
- **UPDATE**: Admins and managers can update AI agents
- **DELETE**: Admins and managers can delete AI agents

### Policies

- **SELECT**: Team members can read policies of their team
- **INSERT**: Only admins can create policies
- **UPDATE**: Only admins can update policies
- **DELETE**: Only admins can delete policies

### Events (Append-Only)

- **SELECT**: Team members can read events of their team
- **INSERT**: Team members can create events (append-only)
- **UPDATE**: Not allowed (no policy)
- **DELETE**: Not allowed (no policy)

## Role-Based Access Control

### Admin
- Full CRUD access within their teams
- Can manage team members, board columns, policies
- Can delete tasks and AI agents

### Manager
- Read access to all team data
- Can create and manage tasks
- Can create and manage AI agents
- Cannot manage team members, board columns, or policies

### Member
- Read access to all team data
- Can create tasks
- Can update tasks (application logic may restrict to own tasks)
- Cannot delete tasks
- Cannot manage AI agents, board columns, or policies

### Viewer
- Read-only access to all team data
- Cannot create, update, or delete anything

## Team Isolation

All policies enforce team isolation by:
1. Checking team membership using `is_team_member()`
2. Verifying that the `team_id` in the row matches a team the user belongs to
3. Using helper functions that query the `team_members` table

## User Identification

Policies use `auth.uid()` to identify the current user from the JWT token. This is provided by Supabase Auth and returns the user's UUID as a TEXT value.

## Security Considerations

1. **Helper Functions**: All helper functions are marked as `SECURITY DEFINER` to ensure they run with the necessary privileges to query the `team_members` table.

2. **Efficient Queries**: Policies use EXISTS subqueries and helper functions to minimize performance impact.

3. **Append-Only Events**: The events table has no UPDATE or DELETE policies, ensuring an immutable audit trail.

4. **Application Logic**: Some restrictions (like task creator-only updates) may need to be enforced at the application level in addition to RLS policies.

## Testing RLS Policies

To test RLS policies:

1. Create test users with different roles
2. Verify they can only access data for teams they belong to
3. Verify role-based permissions are enforced
4. Test that users cannot access data from other teams
5. Verify append-only behavior of events table

## Migration

The RLS policies are applied via migration file `003_enable_rls.sql`. This should be run after the schema is created (migrations 001 and 002).
