"""Database query helper functions."""

from datetime import datetime
from typing import Any, Optional
from uuid import UUID

import asyncpg

from backend.app.core.exceptions import DatabaseError
from backend.app.db.client import db
from backend.app.schemas.auth import TeamMember, UserRole


# ============================================================================
# Teams Queries
# ============================================================================


async def create_team(name: str) -> asyncpg.Record:
    """
    Create a new team with default columns.

    Args:
        name: Team name

    Returns:
        Created team record

    Note: Default columns are automatically created via database trigger.
    """
    query = """
        INSERT INTO teams (name)
        VALUES ($1)
        RETURNING *
    """
    result = await db.fetch_one(query, name)
    if not result:
        raise DatabaseError("Failed to create team")
    
    # Default columns are created automatically by trigger
    # But we can verify they exist
    team_id = result["id"]
    columns = await list_board_columns(team_id)
    
    # If no columns exist (trigger didn't fire), create them manually
    if not columns:
        await db.execute(
            "SELECT create_default_columns($1)",
            team_id,
        )
    
    return result


async def get_team(team_id: UUID) -> Optional[asyncpg.Record]:
    """
    Get a team by ID.

    Args:
        team_id: Team ID

    Returns:
        Team record if found, None otherwise
    """
    query = "SELECT * FROM teams WHERE id = $1"
    return await db.fetch_one(query, team_id)


async def list_teams() -> list[asyncpg.Record]:
    """
    List all teams.

    Returns:
        List of team records
    """
    query = "SELECT * FROM teams ORDER BY created_at DESC"
    return await db.fetch_all(query)


async def update_team(team_id: UUID, name: Optional[str] = None) -> Optional[asyncpg.Record]:
    """
    Update a team.

    Args:
        team_id: Team ID
        name: New team name (optional)

    Returns:
        Updated team record if found, None otherwise
    """
    updates = []
    params = []
    param_num = 1

    if name is not None:
        updates.append(f"name = ${param_num}")
        params.append(name)
        param_num += 1

    if not updates:
        return await get_team(team_id)

    updates.append(f"updated_at = ${param_num}")
    params.append(datetime.utcnow())
    params.append(team_id)

    query = f"""
        UPDATE teams
        SET {', '.join(updates)}
        WHERE id = ${param_num + 1}
        RETURNING *
    """
    return await db.fetch_one(query, *params)


async def delete_team(team_id: UUID) -> bool:
    """
    Delete a team.

    Args:
        team_id: Team ID

    Returns:
        True if deleted, False otherwise
    """
    query = "DELETE FROM teams WHERE id = $1 RETURNING id"
    result = await db.fetch_one(query, team_id)
    return result is not None


# ============================================================================
# Team Members Queries
# ============================================================================


async def create_team_member(
    team_id: UUID,
    user_id: str,
    role: UserRole = UserRole.MEMBER,
) -> asyncpg.Record:
    """
    Create a new team member.

    Args:
        team_id: Team ID
        user_id: User ID
        role: Team role

    Returns:
        Created team member record
    """
    query = """
        INSERT INTO team_members (team_id, user_id, role)
        VALUES ($1, $2, $3)
        RETURNING *
    """
    result = await db.fetch_one(query, team_id, user_id, role.value)
    if not result:
        raise DatabaseError("Failed to create team member")
    return result


async def get_team_member(team_id: UUID, user_id: str) -> Optional[TeamMember]:
    """
    Get team member information.

    Args:
        team_id: Team ID
        user_id: User ID

    Returns:
        TeamMember if found, None otherwise
    """
    query = """
        SELECT * FROM team_members
        WHERE team_id = $1 AND user_id = $2
    """
    result = await db.fetch_one(query, team_id, user_id)
    if not result:
        return None

    return TeamMember(
        user_id=result["user_id"],
        team_id=str(result["team_id"]),
        role=UserRole(result["role"]),
    )


async def list_team_members(team_id: UUID) -> list[asyncpg.Record]:
    """
    List all members of a team.

    Args:
        team_id: Team ID

    Returns:
        List of team member records
    """
    query = """
        SELECT * FROM team_members
        WHERE team_id = $1
        ORDER BY created_at ASC
    """
    return await db.fetch_all(query, team_id)


async def update_team_member(
    team_id: UUID,
    user_id: str,
    role: Optional[UserRole] = None,
) -> Optional[asyncpg.Record]:
    """
    Update a team member.

    Args:
        team_id: Team ID
        user_id: User ID
        role: New role (optional)

    Returns:
        Updated team member record if found, None otherwise
    """
    updates = []
    params = []
    param_num = 1

    if role is not None:
        updates.append(f"role = ${param_num}")
        params.append(role.value)
        param_num += 1

    if not updates:
        query = "SELECT * FROM team_members WHERE team_id = $1 AND user_id = $2"
        return await db.fetch_one(query, team_id, user_id)

    updates.append(f"updated_at = ${param_num}")
    params.append(datetime.utcnow())
    params.extend([team_id, user_id])

    query = f"""
        UPDATE team_members
        SET {', '.join(updates)}
        WHERE team_id = ${param_num + 1} AND user_id = ${param_num + 2}
        RETURNING *
    """
    return await db.fetch_one(query, *params)


async def delete_team_member(team_id: UUID, user_id: str) -> bool:
    """
    Remove a team member.

    Args:
        team_id: Team ID
        user_id: User ID

    Returns:
        True if deleted, False otherwise
    """
    query = """
        DELETE FROM team_members
        WHERE team_id = $1 AND user_id = $2
        RETURNING id
    """
    result = await db.fetch_one(query, team_id, user_id)
    return result is not None


async def get_user_role_in_team(team_id: UUID, user_id: str) -> Optional[UserRole]:
    """
    Get user's role in a specific team.

    Args:
        team_id: Team ID
        user_id: User ID

    Returns:
        UserRole if user is a member, None otherwise
    """
    team_member = await get_team_member(team_id, user_id)
    return team_member.role if team_member else None


# ============================================================================
# Profiles Queries
# ============================================================================


async def create_profile(
    user_id: str,
    team_id: UUID,
    name: Optional[str] = None,
    email: Optional[str] = None,
    skills: Optional[dict] = None,
    level: Optional[str] = None,
    velocity: float = 0.0,
    load: float = 0.0,
) -> asyncpg.Record:
    """
    Create a new profile.

    Args:
        user_id: User ID
        team_id: Team ID
        name: User name
        email: User email
        skills: Skills as JSONB
        level: User level
        velocity: Work velocity
        load: Current load

    Returns:
        Created profile record
    """
    query = """
        INSERT INTO profiles (user_id, team_id, name, email, skills, level, velocity, load)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
        RETURNING *
    """
    result = await db.fetch_one(
        query,
        user_id,
        team_id,
        name,
        email,
        skills or {},
        level,
        velocity,
        load,
    )
    if not result:
        raise DatabaseError("Failed to create profile")
    return result


async def get_profile(user_id: str, team_id: UUID) -> Optional[asyncpg.Record]:
    """
    Get a profile by user ID and team ID.

    Args:
        user_id: User ID
        team_id: Team ID

    Returns:
        Profile record if found, None otherwise
    """
    query = """
        SELECT * FROM profiles
        WHERE user_id = $1 AND team_id = $2
    """
    return await db.fetch_one(query, user_id, team_id)


async def list_profiles(team_id: UUID) -> list[asyncpg.Record]:
    """
    List all profiles for a team.

    Args:
        team_id: Team ID

    Returns:
        List of profile records
    """
    query = """
        SELECT * FROM profiles
        WHERE team_id = $1
        ORDER BY created_at ASC
    """
    return await db.fetch_all(query, team_id)


async def get_team_context_for_orchestration(team_id: UUID) -> dict[str, Any]:
    """
    Get team context for orchestration including members with profiles and AI agents.

    Args:
        team_id: Team ID

    Returns:
        Dictionary with team_members (with profile data) and ai_agents
    """
    # Get team members with their profiles
    query_members = """
        SELECT 
            tm.user_id,
            tm.role,
            p.name,
            p.skills,
            p.level,
            p.velocity,
            p.load
        FROM team_members tm
        LEFT JOIN profiles p ON tm.user_id = p.user_id AND tm.team_id = p.team_id
        WHERE tm.team_id = $1
        ORDER BY tm.created_at ASC
    """
    members = await db.fetch_all(query_members, team_id)

    # Get AI agents
    agents = await list_ai_agents(team_id)

    return {
        "team_members": [dict(member) for member in members],
        "ai_agents": [dict(agent) for agent in agents],
    }


async def update_profile(
    user_id: str,
    team_id: UUID,
    name: Optional[str] = None,
    email: Optional[str] = None,
    skills: Optional[dict] = None,
    level: Optional[str] = None,
    velocity: Optional[float] = None,
    load: Optional[float] = None,
) -> Optional[asyncpg.Record]:
    """
    Update a profile.

    Args:
        user_id: User ID
        team_id: Team ID
        name: User name
        email: User email
        skills: Skills as JSONB
        level: User level
        velocity: Work velocity
        load: Current load

    Returns:
        Updated profile record if found, None otherwise
    """
    updates = []
    params = []
    param_num = 1

    if name is not None:
        updates.append(f"name = ${param_num}")
        params.append(name)
        param_num += 1

    if email is not None:
        updates.append(f"email = ${param_num}")
        params.append(email)
        param_num += 1

    if skills is not None:
        updates.append(f"skills = ${param_num}")
        params.append(skills)
        param_num += 1

    if level is not None:
        updates.append(f"level = ${param_num}")
        params.append(level)
        param_num += 1

    if velocity is not None:
        updates.append(f"velocity = ${param_num}")
        params.append(velocity)
        param_num += 1

    if load is not None:
        updates.append(f"load = ${param_num}")
        params.append(load)
        param_num += 1

    if not updates:
        return await get_profile(user_id, team_id)

    updates.append(f"updated_at = ${param_num}")
    params.append(datetime.utcnow())
    params.extend([user_id, team_id])

    query = f"""
        UPDATE profiles
        SET {', '.join(updates)}
        WHERE user_id = ${param_num + 1} AND team_id = ${param_num + 2}
        RETURNING *
    """
    return await db.fetch_one(query, *params)


# ============================================================================
# Tasks Queries
# ============================================================================


async def create_task(
    team_id: UUID,
    title: str,
    description: Optional[str] = None,
    parent_id: Optional[UUID] = None,
    status: Optional[str] = None,
    size: Optional[int] = None,
    tags: Optional[list[str]] = None,
    assignee_type: Optional[str] = None,
    assignee_id: Optional[UUID] = None,
    assignment_risk: Optional[str] = None,
    column_id: Optional[UUID] = None,
    column_key: Optional[str] = None,
    override_flag: bool = False,
) -> asyncpg.Record:
    """
    Create a new task.

    Args:
        team_id: Team ID
        title: Task title
        description: Task description
        parent_id: Parent task ID (for hierarchy)
        status: Task status
        assignee_type: Assignee type
        assignee_id: Assignee ID
        assignment_risk: Assignment risk level
        column_id: Board column ID
        override_flag: Override flag

    Returns:
        Created task record
    """
    query = """
        INSERT INTO tasks (
            team_id, title, description, parent_id, status, size, tags,
            assignee_type, assignee_id, assignment_risk, column_id, column_key, override_flag
        )
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)
        RETURNING *
    """
    result = await db.fetch_one(
        query,
        team_id,
        title,
        description,
        parent_id,
        status,
        size,
        tags or [],
        assignee_type,
        assignee_id,
        assignment_risk,
        column_id,
        column_key,
        override_flag,
    )
    if not result:
        raise DatabaseError("Failed to create task")
    return result


async def get_task(task_id: UUID, team_id: Optional[UUID] = None) -> Optional[asyncpg.Record]:
    """
    Get a task by ID.

    Args:
        task_id: Task ID
        team_id: Team ID (optional, for team scoping)

    Returns:
        Task record if found, None otherwise
    """
    if team_id:
        query = "SELECT * FROM tasks WHERE id = $1 AND team_id = $2"
        return await db.fetch_one(query, task_id, team_id)
    else:
        query = "SELECT * FROM tasks WHERE id = $1"
        return await db.fetch_one(query, task_id)


async def list_tasks(
    team_id: UUID,
    parent_id: Optional[UUID] = None,
    assignee_id: Optional[UUID] = None,
    status: Optional[str] = None,
    column_id: Optional[UUID] = None,
) -> list[asyncpg.Record]:
    """
    List tasks for a team with optional filters.

    Args:
        team_id: Team ID
        parent_id: Filter by parent task ID
        assignee_id: Filter by assignee ID
        status: Filter by status
        column_id: Filter by column ID

    Returns:
        List of task records
    """
    conditions = ["team_id = $1"]
    params = [team_id]
    param_num = 2

    if parent_id is not None:
        conditions.append(f"parent_id = ${param_num}")
        params.append(parent_id)
        param_num += 1

    if assignee_id is not None:
        conditions.append(f"assignee_id = ${param_num}")
        params.append(assignee_id)
        param_num += 1

    if status is not None:
        conditions.append(f"status = ${param_num}")
        params.append(status)
        param_num += 1

    if column_id is not None:
        conditions.append(f"column_id = ${param_num}")
        params.append(column_id)
        param_num += 1

    query = f"""
        SELECT * FROM tasks
        WHERE {' AND '.join(conditions)}
        ORDER BY created_at DESC
    """
    return await db.fetch_all(query, *params)


async def update_task(
    task_id: UUID,
    team_id: UUID,
    title: Optional[str] = None,
    description: Optional[str] = None,
    status: Optional[str] = None,
    size: Optional[int] = None,
    tags: Optional[list[str]] = None,
    assignee_type: Optional[str] = None,
    assignee_id: Optional[UUID] = None,
    assignment_risk: Optional[str] = None,
    column_id: Optional[UUID] = None,
    column_key: Optional[str] = None,
    parent_id: Optional[UUID] = None,
    override_flag: Optional[bool] = None,
) -> Optional[asyncpg.Record]:
    """
    Update a task.

    Args:
        task_id: Task ID
        team_id: Team ID (for team scoping)
        title: Task title
        description: Task description
        status: Task status
        assignee_type: Assignee type
        assignee_id: Assignee ID
        assignment_risk: Assignment risk level
        column_id: Board column ID
        override_flag: Override flag

    Returns:
        Updated task record if found, None otherwise
    """
    updates = []
    params = []
    param_num = 1

    if title is not None:
        updates.append(f"title = ${param_num}")
        params.append(title)
        param_num += 1

    if description is not None:
        updates.append(f"description = ${param_num}")
        params.append(description)
        param_num += 1

    if status is not None:
        updates.append(f"status = ${param_num}")
        params.append(status)
        param_num += 1

    if size is not None:
        updates.append(f"size = ${param_num}")
        params.append(size)
        param_num += 1

    if tags is not None:
        updates.append(f"tags = ${param_num}")
        params.append(tags)
        param_num += 1

    if assignee_type is not None:
        updates.append(f"assignee_type = ${param_num}")
        params.append(assignee_type)
        param_num += 1

    if assignee_id is not None:
        updates.append(f"assignee_id = ${param_num}")
        params.append(assignee_id)
        param_num += 1

    if assignment_risk is not None:
        updates.append(f"assignment_risk = ${param_num}")
        params.append(assignment_risk)
        param_num += 1

    if column_id is not None:
        updates.append(f"column_id = ${param_num}")
        params.append(column_id)
        param_num += 1

    if column_key is not None:
        updates.append(f"column_key = ${param_num}")
        params.append(column_key)
        param_num += 1

    if parent_id is not None:
        updates.append(f"parent_id = ${param_num}")
        params.append(parent_id)
        param_num += 1

    if override_flag is not None:
        updates.append(f"override_flag = ${param_num}")
        params.append(override_flag)
        param_num += 1

    if approved is not None:
        updates.append(f"approved = ${param_num}")
        params.append(approved)
        param_num += 1

    if approved_at is not None:
        updates.append(f"approved_at = ${param_num}")
        params.append(approved_at)
        param_num += 1

    if approved_by is not None:
        updates.append(f"approved_by = ${param_num}")
        params.append(approved_by)
        param_num += 1

    if approval_comment is not None:
        updates.append(f"approval_comment = ${param_num}")
        params.append(approval_comment)
        param_num += 1

    if not updates:
        return await get_task(task_id, team_id)

    updates.append(f"updated_at = ${param_num}")
    params.append(datetime.utcnow())
    params.extend([task_id, team_id])

    query = f"""
        UPDATE tasks
        SET {', '.join(updates)}
        WHERE id = ${param_num + 1} AND team_id = ${param_num + 2}
        RETURNING *
    """
    return await db.fetch_one(query, *params)


async def delete_task(task_id: UUID, team_id: UUID) -> bool:
    """
    Delete a task.

    Args:
        task_id: Task ID
        team_id: Team ID (for team scoping)

    Returns:
        True if deleted, False otherwise
    """
    query = "DELETE FROM tasks WHERE id = $1 AND team_id = $2 RETURNING id"
    result = await db.fetch_one(query, task_id, team_id)
    return result is not None


async def get_task_children(parent_id: UUID, team_id: UUID) -> list[asyncpg.Record]:
    """
    Get all child tasks of a parent task.

    Args:
        parent_id: Parent task ID
        team_id: Team ID

    Returns:
        List of child task records
    """
    query = """
        SELECT * FROM tasks
        WHERE parent_id = $1 AND team_id = $2
        ORDER BY created_at ASC
    """
    return await db.fetch_all(query, parent_id, team_id)


# ============================================================================
# Board Columns Queries
# ============================================================================


async def create_board_column(
    team_id: UUID,
    name: str,
    position: int,
    key: Optional[str] = None,
    display_name: Optional[str] = None,
    wip_limit: Optional[int] = None,
    is_locked: bool = False,
    workflow_config: Optional[dict] = None,
) -> asyncpg.Record:
    """
    Create a new board column.

    Args:
        team_id: Team ID
        name: Column name
        position: Column position
        key: Column key (lowercase slug, auto-generated if not provided)
        display_name: Display name (defaults to name if not provided)
        wip_limit: Work in progress limit
        is_locked: Whether column is locked
        workflow_config: Workflow configuration as JSONB

    Returns:
        Created board column record
    """
    # Generate key from name if not provided
    if not key:
        import re
        key = re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')
    
    if not display_name:
        display_name = name

    query = """
        INSERT INTO board_columns (team_id, key, name, display_name, position, wip_limit, is_locked, workflow_config)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
        RETURNING *
    """
    result = await db.fetch_one(
        query,
        team_id,
        key,
        name,
        display_name,
        position,
        wip_limit,
        is_locked,
        workflow_config or {},
    )
    if not result:
        raise DatabaseError("Failed to create board column")
    return result


async def get_board_column(column_id: UUID, team_id: Optional[UUID] = None) -> Optional[asyncpg.Record]:
    """
    Get a board column by ID.

    Args:
        column_id: Column ID
        team_id: Team ID (optional, for team scoping)

    Returns:
        Board column record if found, None otherwise
    """
    if team_id:
        query = "SELECT * FROM board_columns WHERE id = $1 AND team_id = $2"
        return await db.fetch_one(query, column_id, team_id)
    else:
        query = "SELECT * FROM board_columns WHERE id = $1"
        return await db.fetch_one(query, column_id)


async def list_board_columns(team_id: UUID) -> list[asyncpg.Record]:
    """
    List all board columns for a team.

    Args:
        team_id: Team ID

    Returns:
        List of board column records, ordered by position
    """
    query = """
        SELECT * FROM board_columns
        WHERE team_id = $1
        ORDER BY position ASC
    """
    return await db.fetch_all(query, team_id)


async def update_board_column(
    column_id: UUID,
    team_id: UUID,
    name: Optional[str] = None,
    key: Optional[str] = None,
    display_name: Optional[str] = None,
    position: Optional[int] = None,
    wip_limit: Optional[int] = None,
    is_locked: Optional[bool] = None,
    workflow_config: Optional[dict] = None,
) -> Optional[asyncpg.Record]:
    """
    Update a board column.

    Args:
        column_id: Column ID
        team_id: Team ID
        name: Column name
        position: Column position
        workflow_config: Workflow configuration

    Returns:
        Updated board column record if found, None otherwise
    """
    updates = []
    params = []
    param_num = 1

    if name is not None:
        updates.append(f"name = ${param_num}")
        params.append(name)
        param_num += 1

    if key is not None:
        updates.append(f"key = ${param_num}")
        params.append(key)
        param_num += 1

    if display_name is not None:
        updates.append(f"display_name = ${param_num}")
        params.append(display_name)
        param_num += 1

    if position is not None:
        updates.append(f"position = ${param_num}")
        params.append(position)
        param_num += 1

    if wip_limit is not None:
        updates.append(f"wip_limit = ${param_num}")
        params.append(wip_limit)
        param_num += 1

    if is_locked is not None:
        updates.append(f"is_locked = ${param_num}")
        params.append(is_locked)
        param_num += 1

    if workflow_config is not None:
        updates.append(f"workflow_config = ${param_num}")
        params.append(workflow_config)
        param_num += 1

    if not updates:
        return await get_board_column(column_id, team_id)

    updates.append(f"updated_at = ${param_num}")
    params.append(datetime.utcnow())
    params.extend([column_id, team_id])

    query = f"""
        UPDATE board_columns
        SET {', '.join(updates)}
        WHERE id = ${param_num + 1} AND team_id = ${param_num + 2}
        RETURNING *
    """
    return await db.fetch_one(query, *params)


async def delete_board_column(column_id: UUID, team_id: UUID) -> bool:
    """
    Delete a board column.

    Args:
        column_id: Column ID
        team_id: Team ID

    Returns:
        True if deleted, False otherwise
    """
    query = "DELETE FROM board_columns WHERE id = $1 AND team_id = $2 RETURNING id"
    result = await db.fetch_one(query, column_id, team_id)
    return result is not None


# ============================================================================
# AI Agents Queries
# ============================================================================


async def create_ai_agent(
    team_id: UUID,
    name: str,
    capabilities_md: Optional[str] = None,
    limits_md: Optional[str] = None,
    tags: Optional[list[str]] = None,
) -> asyncpg.Record:
    """
    Create a new AI agent.

    Args:
        team_id: Team ID
        name: Agent name
        capabilities_md: Capabilities markdown
        limits_md: Limits markdown
        tags: Agent tags (stored as lowercase)

    Returns:
        Created AI agent record
    """
    # Normalize tags to lowercase
    normalized_tags = [tag.lower() for tag in (tags or [])]

    query = """
        INSERT INTO ai_agents (team_id, name, capabilities_md, limits_md, tags)
        VALUES ($1, $2, $3, $4, $5)
        RETURNING *
    """
    result = await db.fetch_one(query, team_id, name, capabilities_md, limits_md, normalized_tags)
    if not result:
        raise DatabaseError("Failed to create AI agent")
    return result


async def get_ai_agent(agent_id: UUID, team_id: Optional[UUID] = None) -> Optional[asyncpg.Record]:
    """
    Get an AI agent by ID.

    Args:
        agent_id: Agent ID
        team_id: Team ID (optional, for team scoping)

    Returns:
        AI agent record if found, None otherwise
    """
    if team_id:
        query = "SELECT * FROM ai_agents WHERE id = $1 AND team_id = $2"
        return await db.fetch_one(query, agent_id, team_id)
    else:
        query = "SELECT * FROM ai_agents WHERE id = $1"
        return await db.fetch_one(query, agent_id)


async def list_ai_agents(team_id: UUID) -> list[asyncpg.Record]:
    """
    List all AI agents for a team.

    Args:
        team_id: Team ID

    Returns:
        List of AI agent records
    """
    query = """
        SELECT * FROM ai_agents
        WHERE team_id = $1
        ORDER BY created_at ASC
    """
    return await db.fetch_all(query, team_id)


async def update_ai_agent(
    agent_id: UUID,
    team_id: UUID,
    name: Optional[str] = None,
    capabilities_md: Optional[str] = None,
    limits_md: Optional[str] = None,
    tags: Optional[list[str]] = None,
) -> Optional[asyncpg.Record]:
    """
    Update an AI agent.

    Args:
        agent_id: Agent ID
        team_id: Team ID
        name: Agent name
        capabilities_md: Capabilities markdown
        limits_md: Limits markdown
        tags: Agent tags (normalized to lowercase)

    Returns:
        Updated AI agent record if found, None otherwise
    """
    updates = []
    params = []
    param_num = 1

    if name is not None:
        updates.append(f"name = ${param_num}")
        params.append(name)
        param_num += 1

    if capabilities_md is not None:
        updates.append(f"capabilities_md = ${param_num}")
        params.append(capabilities_md)
        param_num += 1

    if limits_md is not None:
        updates.append(f"limits_md = ${param_num}")
        params.append(limits_md)
        param_num += 1

    if tags is not None:
        updates.append(f"tags = ${param_num}")
        params.append([tag.lower() for tag in tags])
        param_num += 1

    if not updates:
        return await get_ai_agent(agent_id, team_id)

    updates.append(f"updated_at = ${param_num}")
    params.append(datetime.utcnow())
    params.extend([agent_id, team_id])

    query = f"""
        UPDATE ai_agents
        SET {', '.join(updates)}
        WHERE id = ${param_num + 1} AND team_id = ${param_num + 2}
        RETURNING *
    """
    return await db.fetch_one(query, *params)


async def delete_ai_agent(agent_id: UUID, team_id: UUID) -> bool:
    """
    Delete an AI agent.

    Args:
        agent_id: Agent ID
        team_id: Team ID

    Returns:
        True if deleted, False otherwise
    """
    query = "DELETE FROM ai_agents WHERE id = $1 AND team_id = $2 RETURNING id"
    result = await db.fetch_one(query, agent_id, team_id)
    return result is not None


# ============================================================================
# Events (Audit) Queries
# ============================================================================


async def create_event(
    team_id: UUID,
    event_type: str,
    payload: Optional[dict] = None,
    user_id: Optional[str] = None,
    task_id: Optional[UUID] = None,
) -> asyncpg.Record:
    """
    Create an audit event.

    Args:
        team_id: Team ID
        event_type: Event type (also stored in 'type' column via trigger)
        payload: Event payload as JSONB
        user_id: User ID who triggered the event
        task_id: Related task ID (stored in both task_id column and payload)

    Returns:
        Created event record
    """
    event_payload = payload or {}
    if task_id:
        event_payload["task_id"] = str(task_id)

    # Insert with event_type; trigger will sync to 'type' column
    # task_id is stored in both the column and payload for flexibility
    query = """
        INSERT INTO events (team_id, event_type, type, task_id, payload, user_id)
        VALUES ($1, $2, $2, $3, $4, $5)
        RETURNING *
    """
    result = await db.fetch_one(query, team_id, event_type, task_id, event_payload, user_id)
    if not result:
        raise DatabaseError("Failed to create event")
    return result


async def get_event(event_id: UUID, team_id: Optional[UUID] = None) -> Optional[asyncpg.Record]:
    """
    Get an event by ID.

    Args:
        event_id: Event ID
        team_id: Team ID (optional, for team scoping)

    Returns:
        Event record if found, None otherwise
    """
    if team_id:
        query = "SELECT * FROM events WHERE id = $1 AND team_id = $2"
        return await db.fetch_one(query, event_id, team_id)
    else:
        query = "SELECT * FROM events WHERE id = $1"
        return await db.fetch_one(query, event_id)


async def list_events(
    team_id: UUID,
    event_type: Optional[str] = None,
    task_id: Optional[UUID] = None,
    limit: int = 100,
) -> list[asyncpg.Record]:
    """
    List events for a team with optional filters.

    Args:
        team_id: Team ID
        event_type: Filter by event type
        task_id: Filter by task ID (searches in payload)
        limit: Maximum number of events to return

    Returns:
        List of event records, ordered by created_at DESC
    """
    conditions = ["team_id = $1"]
    params = [team_id]
    param_num = 2

    if event_type:
        conditions.append(f"event_type = ${param_num}")
        params.append(event_type)
        param_num += 1

    if task_id:
        # Filter by task_id column (preferred) or fallback to payload
        conditions.append(f"(task_id = ${param_num} OR payload->>'task_id' = ${param_num + 1})")
        params.append(task_id)
        params.append(str(task_id))
        param_num += 2

    query = f"""
        SELECT * FROM events
        WHERE {' AND '.join(conditions)}
        ORDER BY created_at DESC
        LIMIT ${param_num}
    """
    params.append(limit)
    return await db.fetch_all(query, *params)


# ============================================================================
# Policies Queries
# ============================================================================


async def create_policy(
    team_id: UUID,
    name: str,
    policy_md: Optional[str] = None,
    description_md: Optional[str] = None,
) -> asyncpg.Record:
    """
    Create a new policy.

    Args:
        team_id: Team ID
        name: Policy name
        policy_md: Policy markdown content
        description_md: Description markdown

    Returns:
        Created policy record
    """
    query = """
        INSERT INTO policies (team_id, name, policy_md, description_md)
        VALUES ($1, $2, $3, $4)
        RETURNING *
    """
    result = await db.fetch_one(query, team_id, name, policy_md, description_md)
    if not result:
        raise DatabaseError("Failed to create policy")
    return result


async def get_policy(policy_id: UUID, team_id: Optional[UUID] = None) -> Optional[asyncpg.Record]:
    """
    Get a policy by ID.

    Args:
        policy_id: Policy ID
        team_id: Team ID (optional, for team scoping)

    Returns:
        Policy record if found, None otherwise
    """
    if team_id:
        query = "SELECT * FROM policies WHERE id = $1 AND team_id = $2"
        return await db.fetch_one(query, policy_id, team_id)
    else:
        query = "SELECT * FROM policies WHERE id = $1"
        return await db.fetch_one(query, policy_id)


async def list_policies(team_id: UUID) -> list[asyncpg.Record]:
    """
    List all policies for a team.

    Args:
        team_id: Team ID

    Returns:
        List of policy records
    """
    query = """
        SELECT * FROM policies
        WHERE team_id = $1
        ORDER BY updated_at DESC
    """
    return await db.fetch_all(query, team_id)


async def update_policy(
    policy_id: UUID,
    team_id: UUID,
    name: Optional[str] = None,
    policy_md: Optional[str] = None,
    description_md: Optional[str] = None,
) -> Optional[asyncpg.Record]:
    """
    Update a policy.

    Args:
        policy_id: Policy ID
        team_id: Team ID
        name: Policy name
        policy_md: Policy markdown content
        description_md: Description markdown

    Returns:
        Updated policy record if found, None otherwise
    """
    updates = []
    params = []
    param_num = 1

    if name is not None:
        updates.append(f"name = ${param_num}")
        params.append(name)
        param_num += 1

    if policy_md is not None:
        updates.append(f"policy_md = ${param_num}")
        params.append(policy_md)
        param_num += 1

    if description_md is not None:
        updates.append(f"description_md = ${param_num}")
        params.append(description_md)
        param_num += 1

    if not updates:
        return await get_policy(policy_id, team_id)

    updates.append(f"updated_at = ${param_num}")
    params.append(datetime.utcnow())
    params.extend([policy_id, team_id])

    query = f"""
        UPDATE policies
        SET {', '.join(updates)}
        WHERE id = ${param_num + 1} AND team_id = ${param_num + 2}
        RETURNING *
    """
    return await db.fetch_one(query, *params)


async def delete_policy(policy_id: UUID, team_id: UUID) -> bool:
    """
    Delete a policy.

    Args:
        policy_id: Policy ID
        team_id: Team ID

    Returns:
        True if deleted, False otherwise
    """
    query = "DELETE FROM policies WHERE id = $1 AND team_id = $2 RETURNING id"
    result = await db.fetch_one(query, policy_id, team_id)
    return result is not None
