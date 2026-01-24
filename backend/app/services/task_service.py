"""Task management service layer."""

from typing import Optional
from uuid import UUID

from backend.app.core.exceptions import APIException, AuthorizationError
from backend.app.db import queries
from backend.app.db.queries import (
    create_event,
    create_task,
    delete_task,
    get_ai_agent,
    get_profile,
    get_task,
    get_task_children,
    list_events,
    list_board_columns,
    list_tasks,
    update_task,
)
from backend.app.schemas.auth import TokenData, UserRole
from backend.app.schemas.tasks import (
    SubtaskDetailItem,
    TaskCreateRequest,
    TaskDetailResponse,
    TaskResponse,
    TaskUpdateRequest,
)


class TaskServiceError(APIException):
    """Task service error."""

    def __init__(self, code: str, message: str, details: Optional[dict] = None):
        """Initialize task service error."""
        super().__init__(
            code=code,
            message=message,
            status_code=400,
            details=details or {},
        )


class TaskService:
    """Task management service."""

    @staticmethod
    async def create_task(
        team_id: UUID,
        request: TaskCreateRequest,
        user: TokenData,
    ) -> TaskResponse:
        """
        Create a new task.

        Args:
            team_id: Team ID
            request: Task creation request
            user: Authenticated user

        Returns:
            Created task response

        Raises:
            TaskServiceError: If validation fails
        """
        # Validate column_key if provided
        column_id = None
        if request.column_key:
            columns = await list_board_columns(team_id)
            column = None
            for c in columns:
                # Check both 'key' field and 'name' field (in case key is stored as name)
                if c.get("key") == request.column_key or c.get("name") == request.column_key:
                    column = c
                    break
            if not column:
                raise TaskServiceError(
                    code="INVALID_COLUMN_KEY",
                    message=f"Column key '{request.column_key}' not found in team's board",
                )
            column_id = column["id"]

        # Validate parent_id if provided
        if request.parent_id:
            parent_task = await get_task(request.parent_id, team_id)
            if not parent_task:
                raise TaskServiceError(
                    code="INVALID_SUBTASK_DATA",
                    message=f"Parent task {request.parent_id} not found or does not belong to team",
                )
            
            # Enforce single-level hierarchy: parent cannot be a subtask itself
            if parent_task.get("parent_id"):
                raise TaskServiceError(
                    code="INVALID_HIERARCHY_DEPTH",
                    message="Subtasks cannot have their own subtasks. Only single-level hierarchy is supported.",
                    details={"parent_task_id": str(request.parent_id), "parent_has_parent": True},
                )

        # Create task
        task_record = await create_task(
            team_id=team_id,
            title=request.title,
            description=request.description,
            parent_id=request.parent_id,
            status="todo",  # Default status
            assignee_type=request.assignee_type.value if request.assignee_type else None,
            assignee_id=request.assignee_id,
            assignment_risk=request.assignment_risk.value if request.assignment_risk else None,
            column_id=column_id,
            column_key=request.column_key,
            override_flag=False,
        )

        # Log audit event
        await create_event(
            team_id=team_id,
            event_type="task.created",
            payload={
                "task_id": str(task_record["id"]),
                "title": request.title,
                "parent_id": str(request.parent_id) if request.parent_id else None,
            },
            user_id=user.user_id,
        )

        # Get subtask count
        subtask_count = len(await get_task_children(task_record["id"], team_id))

        return TaskResponse(
            id=task_record["id"],
            team_id=task_record["team_id"],
            parent_id=task_record.get("parent_id"),
            title=task_record["title"],
            description=task_record.get("description"),
            status=task_record.get("status"),
            size=None,  # Not in current schema
            tags=[],  # Not in current schema
            column_id=task_record.get("column_id"),
            column_key=request.column_key,
            assignee_type=AssigneeType(task_record["assignee_type"]) if task_record.get("assignee_type") else None,
            assignee_id=task_record.get("assignee_id"),
            assignment_risk=AssignmentRisk(task_record["assignment_risk"]) if task_record.get("assignment_risk") else None,
            override_flag=task_record.get("override_flag", False),
            subtask_count=subtask_count,
            created_at=task_record["created_at"],
            updated_at=task_record["updated_at"],
        )

    @staticmethod
    async def get_task(task_id: UUID, team_id: UUID, user: TokenData) -> TaskResponse:
        """
        Get a task by ID.

        Args:
            task_id: Task ID
            team_id: Team ID
            user: Authenticated user

        Returns:
            Task response

        Raises:
            TaskServiceError: If task not found
        """
        task_record = await get_task(task_id, team_id)
        if not task_record:
            raise TaskServiceError(
                code="TASK_NOT_FOUND",
                message=f"Task {task_id} not found",
            )

        # Get subtask count
        subtask_count = len(await get_task_children(task_id, team_id))

        # Get audit history (task events)
        events = await list_events(
            team_id=team_id,
            task_id=task_id,
            limit=100,  # Get up to 100 most recent events
        )
        audit_history = [
            TaskHistoryEvent(
                id=event["id"],
                event_type=event.get("event_type") or event.get("type", ""),
                created_at=event["created_at"],
                user_id=event.get("user_id"),
                payload=event.get("payload") or {},
            )
            for event in events
        ]

        return TaskResponse(
            id=task_record["id"],
            team_id=task_record["team_id"],
            parent_id=task_record.get("parent_id"),
            title=task_record["title"],
            description=task_record.get("description"),
            status=task_record.get("status"),
            size=task_record.get("size"),
            tags=task_record.get("tags") or [],
            column_id=task_record.get("column_id"),
            column_key=task_record.get("column_key"),
            assignee_type=AssigneeType(task_record["assignee_type"]) if task_record.get("assignee_type") else None,
            assignee_id=task_record.get("assignee_id"),
            assignment_risk=AssignmentRisk(task_record["assignment_risk"]) if task_record.get("assignment_risk") else None,
            override_flag=task_record.get("override_flag", False),
            subtask_count=subtask_count,
            created_at=task_record["created_at"],
            updated_at=task_record["updated_at"],
            audit_history=audit_history if audit_history else None,
        )

    @staticmethod
    async def get_task_detail(
        task_id: UUID,
        team_id: UUID,
        user: TokenData,
    ) -> TaskDetailResponse:
        """
        Get comprehensive task detail with joined display fields.

        Args:
            task_id: Task ID
            team_id: Team ID
            user: Authenticated user

        Returns:
            Task detail response with all display fields

        Raises:
            TaskServiceError: If task not found
        """
        from backend.app.schemas.common import AssigneeType, AssignmentRisk

        # Get task record
        task_record = await get_task(task_id, team_id)
        if not task_record:
            raise TaskServiceError(
                code="TASK_NOT_FOUND",
                message=f"Task {task_id} not found",
            )

        # Get assignee display name
        assignee_display_name = None
        assignee_type = task_record.get("assignee_type")
        assignee_id = task_record.get("assignee_id")

        if assignee_id and assignee_type:
            if assignee_type in ["agent", "ai"]:
                # Get AI agent name (assignee_id is ai_agents.id UUID)
                try:
                    agent = await get_ai_agent(assignee_id, team_id)
                    if agent:
                        assignee_display_name = agent.get("name") or str(assignee_id)
                except Exception:
                    # If agent not found, leave as None
                    pass
            elif assignee_type in ["user", "human"]:
                # For users, assignee_id might be profiles.id (UUID) or we need to look it up differently
                # Try to get profile by querying all profiles and matching by id
                # Note: This is a workaround since get_profile expects user_id (TEXT), not id (UUID)
                from backend.app.db.queries import list_profiles
                profiles = await list_profiles(team_id)
                for profile in profiles:
                    if profile.get("id") == assignee_id:
                        assignee_display_name = profile.get("name") or profile.get("email") or str(assignee_id)
                        break

        # Get parent title if this is a subtask
        parent_title = None
        parent_id = task_record.get("parent_id")
        if parent_id:
            parent_task = await get_task(parent_id, team_id)
            if parent_task:
                parent_title = parent_task.get("title")

        # Get subtasks preview if this is a parent task
        subtasks_preview = None
        subtasks = await get_task_children(task_id, team_id)
        if subtasks:
            subtasks_preview = []
            for subtask in subtasks:
                # Get assignee display name for each subtask
                subtask_assignee_display_name = None
                subtask_assignee_type = subtask.get("assignee_type")
                subtask_assignee_id = subtask.get("assignee_id")

                if subtask_assignee_id and subtask_assignee_type:
                    if subtask_assignee_type in ["agent", "ai"]:
                        try:
                            agent = await get_ai_agent(subtask_assignee_id, team_id)
                            if agent:
                                subtask_assignee_display_name = agent.get("name") or str(subtask_assignee_id)
                        except Exception:
                            pass
                    elif subtask_assignee_type in ["user", "human"]:
                        # For users, assignee_id is profiles.id (UUID)
                        profile = await get_profile_by_id(subtask_assignee_id, team_id)
                        if profile:
                            subtask_assignee_display_name = profile.get("name") or profile.get("email") or str(subtask_assignee_id)

                subtasks_preview.append(
                    SubtaskDetailItem(
                        id=subtask["id"],
                        title=subtask["title"],
                        column_key=subtask.get("column_key"),
                        assignee_display_name=subtask_assignee_display_name,
                    )
                )

        # Get assignment_reason from events (optional, may not exist)
        assignment_reason = None
        # TODO: Query events table for assignment_reason if stored there
        # For now, leave as None

        return TaskDetailResponse(
            id=task_record["id"],
            team_id=task_record["team_id"],
            parent_id=task_record.get("parent_id"),
            title=task_record["title"],
            description=task_record.get("description"),
            column_key=task_record.get("column_key"),
            tags=task_record.get("tags") or [],
            size=task_record.get("size"),
            assignee_type=AssigneeType(assignee_type) if assignee_type else None,
            assignee_id=assignee_id,
            created_at=task_record["created_at"],
            updated_at=task_record["updated_at"],
            assignee_display_name=assignee_display_name,
            parent_title=parent_title,
            assignment_reason=assignment_reason,
            assignment_risk=AssignmentRisk(task_record["assignment_risk"]) if task_record.get("assignment_risk") else None,
            subtasks_preview=subtasks_preview if subtasks_preview else None,
        )

    @staticmethod
    async def update_task(
        task_id: UUID,
        team_id: UUID,
        request: TaskUpdateRequest,
        user: TokenData,
    ) -> TaskResponse:
        """
        Update a task.

        Args:
            task_id: Task ID
            team_id: Team ID
            request: Task update request
            user: Authenticated user

        Returns:
            Updated task response

        Raises:
            TaskServiceError: If task not found or unauthorized
            AuthorizationError: If user doesn't have permission
        """
        # Get existing task
        task_record = await get_task(task_id, team_id)
        if not task_record:
            raise TaskServiceError(
                code="TASK_NOT_FOUND",
                message=f"Task {task_id} not found",
            )

        # Check permissions: creator, admin, or manager can update
        # For now, we'll check if user is admin/manager (creator check would need events table lookup)
        user_role = await queries.get_user_role_in_team(team_id, user.user_id)
        if user_role not in [UserRole.ADMIN, UserRole.MANAGER]:
            # TODO: Check if user is the creator via events table
            # For now, allow members to update (RLS will enforce team membership)
            pass

        # Validate parent_id if being updated
        if hasattr(request, "parent_id") and request.parent_id is not None:
            # Prevent recursive relationships: cannot set parent to a task that is a descendant
            async def check_recursive_relationship(child_id: UUID, potential_parent_id: UUID) -> bool:
                """Check if potential_parent is a descendant of child (would create cycle)."""
                current_id = potential_parent_id
                depth = 0
                max_depth = 100  # Safety limit
                
                while current_id and depth < max_depth:
                    parent = await get_task(current_id, team_id)
                    if not parent:
                        break
                    if parent.get("parent_id") == child_id:
                        return True  # Cycle detected
                    current_id = parent.get("parent_id")
                    depth += 1
                return False
            
            # Check for recursive relationship
            if await check_recursive_relationship(task_id, request.parent_id):
                raise TaskServiceError(
                    code="RECURSIVE_RELATIONSHIP",
                    message="Cannot set parent: would create a circular relationship",
                    details={"task_id": str(task_id), "parent_id": str(request.parent_id)},
                )
            
            # Validate parent exists and belongs to team
            parent_task = await get_task(request.parent_id, team_id)
            if not parent_task:
                raise TaskServiceError(
                    code="INVALID_SUBTASK_DATA",
                    message=f"Parent task {request.parent_id} not found or does not belong to team",
                )
            
            # Enforce single-level hierarchy: parent cannot be a subtask itself
            if parent_task.get("parent_id"):
                raise TaskServiceError(
                    code="INVALID_HIERARCHY_DEPTH",
                    message="Subtasks cannot have their own subtasks. Only single-level hierarchy is supported.",
                    details={"parent_task_id": str(request.parent_id), "parent_has_parent": True},
                )
        
        # Prevent subtasks from becoming parents: if this task has subtasks, cannot set parent_id
        if hasattr(request, "parent_id") and request.parent_id is not None:
            existing_subtasks = await get_task_children(task_id, team_id)
            if existing_subtasks:
                raise TaskServiceError(
                    code="INVALID_HIERARCHY_DEPTH",
                    message="Tasks with existing subtasks cannot become subtasks themselves",
                    details={"task_id": str(task_id), "subtask_count": len(existing_subtasks)},
                )

        # Validate column_key if provided
        column_id = None
        if hasattr(request, "column_key") and request.column_key:
            columns = await list_board_columns(team_id)
            column = None
            for c in columns:
                # Check both 'key' field and 'name' field
                if c.get("key") == request.column_key or c.get("name") == request.column_key:
                    column = c
                    break
            if not column:
                raise TaskServiceError(
                    code="INVALID_COLUMN_KEY",
                    message=f"Column key '{request.column_key}' not found in team's board",
                )
            column_id = column["id"]

        # Update task
        updated_record = await update_task(
            task_id=task_id,
            team_id=team_id,
            title=request.title,
            description=request.description,
            status=request.status,
            size=request.size,
            tags=request.tags,
            assignee_type=request.assignee_type.value if request.assignee_type else None,
            assignee_id=request.assignee_id,
            assignment_risk=request.assignment_risk.value if request.assignment_risk else None,
            column_id=column_id,
            column_key=request.column_key if hasattr(request, 'column_key') else None,
            parent_id=request.parent_id if hasattr(request, 'parent_id') else None,
            override_flag=request.override_flag,
        )

        if not updated_record:
            raise TaskServiceError(
                code="TASK_UPDATE_FAILED",
                message="Failed to update task",
            )

        # Log audit event
        await create_event(
            team_id=team_id,
            event_type="task.updated",
            payload={
                "task_id": str(task_id),
                "changes": request.model_dump(exclude_unset=True),
            },
            user_id=user.user_id,
        )

        # Get subtask count
        subtask_count = len(await get_task_children(task_id, team_id))

        return TaskResponse(
            id=updated_record["id"],
            team_id=updated_record["team_id"],
            parent_id=updated_record.get("parent_id"),
            title=updated_record["title"],
            description=updated_record.get("description"),
            status=updated_record.get("status"),
            size=None,
            tags=[],
            column_id=updated_record.get("column_id"),
            column_key=request.column_key if hasattr(request, "column_key") else None,
            assignee_type=AssigneeType(updated_record["assignee_type"]) if updated_record.get("assignee_type") else None,
            assignee_id=updated_record.get("assignee_id"),
            assignment_risk=AssignmentRisk(updated_record["assignment_risk"]) if updated_record.get("assignment_risk") else None,
            override_flag=updated_record.get("override_flag", False),
            subtask_count=subtask_count,
            created_at=updated_record["created_at"],
            updated_at=updated_record["updated_at"],
        )

    @staticmethod
    async def delete_task(task_id: UUID, team_id: UUID, user: TokenData, cascade: bool = False) -> None:
        """
        Delete a task.

        Args:
            task_id: Task ID
            team_id: Team ID
            user: Authenticated user
            cascade: If True, delete task and all subtasks. If False, block deletion if task has subtasks.

        Raises:
            TaskServiceError: If task not found or has subtasks without cascade
            AuthorizationError: If user doesn't have permission
        """
        # Get existing task
        task_record = await get_task(task_id, team_id)
        if not task_record:
            raise TaskServiceError(
                code="TASK_NOT_FOUND",
                message=f"Task {task_id} not found",
            )

        # Check permissions: only admin or manager can delete
        user_role = await queries.get_user_role_in_team(team_id, user.user_id)
        if user_role not in [UserRole.ADMIN, UserRole.MANAGER]:
            raise AuthorizationError(
                "Only admins and managers can delete tasks",
                details={"required_roles": ["admin", "manager"]},
            )

        # Check if task has children (subtasks)
        children = await get_task_children(task_id, team_id)
        has_children = len(children) > 0

        # Block deletion if task has subtasks and cascade is not enabled
        if has_children and not cascade:
            raise TaskServiceError(
                code="TASK_HAS_SUBTASKS",
                message=f"Task has {len(children)} subtask(s). Use cascade=true to delete parent and all subtasks.",
                details={
                    "task_id": str(task_id),
                    "subtask_count": len(children),
                    "subtask_ids": [str(child["id"]) for child in children],
                },
            )

        # Delete task (CASCADE will delete children automatically if cascade=True)
        deleted = await queries.delete_task(task_id, team_id)
        if not deleted:
            raise TaskServiceError(
                code="TASK_DELETE_FAILED",
                message="Failed to delete task",
            )

        # Log audit event
        event_type = "task_deleted_with_children" if has_children else "task.deleted"
        event_payload = {
            "task_id": str(task_id),
            "title": task_record.get("title"),
            "cascade": cascade,
        }
        if has_children:
            event_payload["children_count"] = len(children)
            event_payload["children_ids"] = [str(child["id"]) for child in children]

        await create_event(
            team_id=team_id,
            event_type=event_type,
            payload=event_payload,
            user_id=user.user_id,
            task_id=task_id,
        )

    @staticmethod
    async def get_board(team_id: UUID, user: TokenData) -> dict:
        """
        Get board data for a team.

        Args:
            team_id: Team ID
            user: Authenticated user

        Returns:
            Board data with columns and tasks
        """
        # Get board columns
        columns = await list_board_columns(team_id)

        # Get all tasks for the team
        tasks = await list_tasks(team_id)

        # Organize tasks by column
        tasks_by_column: dict[UUID, list] = {}
        for task in tasks:
            column_id = task.get("column_id")
            if column_id:
                if column_id not in tasks_by_column:
                    tasks_by_column[column_id] = []
                # Get subtask count
                subtask_count = len(await get_task_children(task["id"], team_id))
                tasks_by_column[column_id].append({
                    "id": str(task["id"]),
                    "title": task["title"],
                    "description": task.get("description"),
                    "status": task.get("status"),
                    "parent_id": str(task["parent_id"]) if task.get("parent_id") else None,
                    "subtask_count": subtask_count,
                    "assignee_type": task.get("assignee_type"),
                    "assignee_id": str(task["assignee_id"]) if task.get("assignee_id") else None,
                })

        # Build column responses
        column_responses = []
        for col in columns:
            # Group tasks by column_key if available, otherwise by column_id
            col_key = col.get("key") or col.get("name")
            col_tasks = []
            
            # Get tasks by column_id
            if col["id"] in tasks_by_column:
                col_tasks = tasks_by_column[col["id"]]
            
            # Also get tasks by column_key
            for task in tasks:
                task_col_key = task.get("column_key")
                if task_col_key == col_key:
                    # Avoid duplicates
                    if not any(t["id"] == str(task["id"]) for t in col_tasks):
                        subtask_count = len(await get_task_children(task["id"], team_id))
                        col_tasks.append({
                            "id": str(task["id"]),
                            "title": task["title"],
                            "description": task.get("description"),
                            "status": task.get("status"),
                            "subtask_count": subtask_count,
                            "assignee_type": task.get("assignee_type"),
                            "assignee_id": str(task["assignee_id"]) if task.get("assignee_id") else None,
                        })
            
            column_responses.append({
                "id": str(col["id"]),
                "key": col_key,
                "name": col["name"],
                "display_name": col.get("display_name") or col["name"],
                "position": col["position"],
                "wip_limit": col.get("wip_limit"),
                "is_locked": col.get("is_locked", False),
                "tasks": col_tasks,
            })

        return {
            "team_id": str(team_id),
            "columns": column_responses,
        }
