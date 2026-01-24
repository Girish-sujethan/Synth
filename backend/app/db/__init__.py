"""Database client and query helpers."""

from backend.app.db.client import DatabaseClient, db
from backend.app.db.queries import (
    # Teams
    create_team,
    get_team,
    list_teams,
    update_team,
    delete_team,
    # Team Members
    create_team_member,
    get_team_member,
    list_team_members,
    update_team_member,
    delete_team_member,
    get_user_role_in_team,
    # Profiles
    create_profile,
    get_profile,
    list_profiles,
    update_profile,
    # Tasks
    create_task,
    get_task,
    list_tasks,
    update_task,
    delete_task,
    get_task_children,
    # Board Columns
    create_board_column,
    get_board_column,
    list_board_columns,
    update_board_column,
    delete_board_column,
    # AI Agents
    create_ai_agent,
    get_ai_agent,
    list_ai_agents,
    update_ai_agent,
    delete_ai_agent,
    # Events
    create_event,
    get_event,
    list_events,
    # Policies
    create_policy,
    get_policy,
    list_policies,
    update_policy,
    delete_policy,
)

__all__ = [
    "DatabaseClient",
    "db",
    # Teams
    "create_team",
    "get_team",
    "list_teams",
    "update_team",
    "delete_team",
    # Team Members
    "create_team_member",
    "get_team_member",
    "list_team_members",
    "update_team_member",
    "delete_team_member",
    "get_user_role_in_team",
    # Profiles
    "create_profile",
    "get_profile",
    "list_profiles",
    "update_profile",
    # Tasks
    "create_task",
    "get_task",
    "list_tasks",
    "update_task",
    "delete_task",
    "get_task_children",
    # Board Columns
    "create_board_column",
    "get_board_column",
    "list_board_columns",
    "update_board_column",
    "delete_board_column",
    # AI Agents
    "create_ai_agent",
    "get_ai_agent",
    "list_ai_agents",
    "update_ai_agent",
    "delete_ai_agent",
    # Events
    "create_event",
    "get_event",
    "list_events",
    # Policies
    "create_policy",
    "get_policy",
    "list_policies",
    "update_policy",
    "delete_policy",
]
