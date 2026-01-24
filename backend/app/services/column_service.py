"""Column management service layer."""

from typing import Optional
from uuid import UUID

from backend.app.core.exceptions import APIException, AuthorizationError
from backend.app.db import queries
from backend.app.db import queries
from backend.app.db.queries import (
    create_board_column,
    create_event,
    delete_board_column,
    get_board_column,
    list_board_columns,
    update_board_column,
    update_task,
)
from backend.app.schemas.auth import TokenData, UserRole


class ColumnServiceError(APIException):
    """Column service error."""

    def __init__(self, code: str, message: str, details: Optional[dict] = None):
        """Initialize column service error."""
        super().__init__(
            code=code,
            message=message,
            status_code=400,
            details=details or {},
        )


class ColumnService:
    """Column management service."""

    @staticmethod
    async def list_columns(team_id: UUID, user: TokenData) -> list[dict]:
        """
        List all columns for a team.

        Args:
            team_id: Team ID
            user: Authenticated user

        Returns:
            List of column records
        """
        columns = await list_board_columns(team_id)
        return [
            {
                "id": str(col["id"]),
                "key": col.get("key") or col.get("name"),
                "display_name": col.get("display_name") or col["name"],
                "name": col["name"],
                "position": col["position"],
                "wip_limit": col.get("wip_limit"),
                "is_locked": col.get("is_locked", False),
            }
            for col in columns
        ]

    @staticmethod
    async def get_column(team_id: UUID, column_key: str, user: TokenData) -> dict:
        """
        Get a column by key.

        Args:
            team_id: Team ID
            column_key: Column key
            user: Authenticated user

        Returns:
            Column record

        Raises:
            ColumnServiceError: If column not found
        """
        columns = await list_board_columns(team_id)
        column = None
        for c in columns:
            if c.get("key") == column_key or c.get("name") == column_key:
                column = c
                break

        if not column:
            raise ColumnServiceError(
                code="COLUMN_NOT_FOUND",
                message=f"Column with key '{column_key}' not found",
            )

        return {
            "id": str(column["id"]),
            "key": column.get("key") or column.get("name"),
            "display_name": column.get("display_name") or column["name"],
            "name": column["name"],
            "position": column["position"],
            "wip_limit": column.get("wip_limit"),
            "is_locked": column.get("is_locked", False),
        }

    @staticmethod
    async def update_column(
        team_id: UUID,
        column_key: str,
        display_name: Optional[str] = None,
        position: Optional[int] = None,
        wip_limit: Optional[int] = None,
        user: TokenData = None,
    ) -> dict:
        """
        Update a column.

        Args:
            team_id: Team ID
            column_key: Column key
            display_name: New display name
            position: New position
            wip_limit: New WIP limit
            user: Authenticated user

        Returns:
            Updated column record

        Raises:
            ColumnServiceError: If column not found or locked
            AuthorizationError: If user doesn't have permission
        """
        # Check permissions - only admins can update columns
        if user:
            user_role = await queries.get_user_role_in_team(team_id, user.user_id)
            if user_role != UserRole.ADMIN:
                raise AuthorizationError(
                    "Only admins can update columns",
                    details={"required_role": "admin"},
                )

        # Get existing column
        columns = await list_board_columns(team_id)
        column = None
        column_id = None
        for c in columns:
            if c.get("key") == column_key or c.get("name") == column_key:
                column = c
                column_id = c["id"]
                break

        if not column:
            raise ColumnServiceError(
                code="COLUMN_NOT_FOUND",
                message=f"Column with key '{column_key}' not found",
            )

        # Check if column is locked
        if column.get("is_locked", False):
            raise ColumnServiceError(
                code="COLUMN_LOCKED",
                message="Cannot modify locked column",
            )

        # Update column
        updated = await update_board_column(
            column_id=column_id,
            team_id=team_id,
            display_name=display_name,
            position=position,
            wip_limit=wip_limit,
        )

        if not updated:
            raise ColumnServiceError(
                code="COLUMN_UPDATE_FAILED",
                message="Failed to update column",
            )

        return {
            "id": str(updated["id"]),
            "key": updated.get("key") or updated.get("name"),
            "display_name": updated.get("display_name") or updated["name"],
            "name": updated["name"],
            "position": updated["position"],
            "wip_limit": updated.get("wip_limit"),
            "is_locked": updated.get("is_locked", False),
        }

    @staticmethod
    async def reorder_columns(
        team_id: UUID,
        ordered_keys: list[str],
        user: TokenData,
    ) -> list[dict]:
        """
        Reorder columns.

        Args:
            team_id: Team ID
            ordered_keys: Ordered list of column keys
            user: Authenticated user

        Returns:
            List of updated column records

        Raises:
            ColumnServiceError: If validation fails
            AuthorizationError: If user doesn't have permission
        """
        # Check permissions - only admins can reorder columns
        user_role = await queries.get_user_role_in_team(team_id, user.user_id)
        if user_role != UserRole.ADMIN:
            raise AuthorizationError(
                "Only admins can reorder columns",
                details={"required_role": "admin"},
            )

        # Get all columns
        columns = await list_board_columns(team_id)
        column_map = {}
        for col in columns:
            key = col.get("key") or col.get("name")
            column_map[key] = col

        # Validate all keys exist
        missing_keys = [key for key in ordered_keys if key not in column_map]
        if missing_keys:
            raise ColumnServiceError(
                code="INVALID_COLUMN_KEYS",
                message=f"Columns not found: {', '.join(missing_keys)}",
            )

        # Check for locked columns
        locked_keys = [
            key
            for key in ordered_keys
            if column_map[key].get("is_locked", False)
        ]
        if locked_keys:
            raise ColumnServiceError(
                code="COLUMN_LOCKED",
                message=f"Cannot reorder locked columns: {', '.join(locked_keys)}",
            )

        # Update positions sequentially
        updated_columns = []
        for position, key in enumerate(ordered_keys):
            column = column_map[key]
            updated = await update_board_column(
                column_id=column["id"],
                team_id=team_id,
                position=position,
            )
            if updated:
                updated_columns.append({
                    "id": str(updated["id"]),
                    "key": updated.get("key") or updated.get("name"),
                    "display_name": updated.get("display_name") or updated["name"],
                    "name": updated["name"],
                    "position": updated["position"],
                    "wip_limit": updated.get("wip_limit"),
                    "is_locked": updated.get("is_locked", False),
                })

        return updated_columns

    @staticmethod
    async def create_column(
        team_id: UUID,
        key: str,
        display_name: str,
        position: Optional[int] = None,
        wip_limit: Optional[int] = None,
        user: TokenData = None,
    ) -> dict:
        """
        Create a new column.

        Args:
            team_id: Team ID
            key: Column key (lowercase slug)
            display_name: Display name
            position: Position (defaults to end)
            wip_limit: WIP limit
            user: Authenticated user

        Returns:
            Created column record

        Raises:
            ColumnServiceError: If validation fails
            AuthorizationError: If user doesn't have permission
        """
        # Check permissions - only admins can create columns
        if user:
            user_role = await queries.get_user_role_in_team(team_id, user.user_id)
            if user_role != UserRole.ADMIN:
                raise AuthorizationError(
                    "Only admins can create columns",
                    details={"required_role": "admin"},
                )

        # Validate key format (lowercase slug)
        import re
        if not re.match(r'^[a-z0-9-]+$', key):
            raise ColumnServiceError(
                code="INVALID_COLUMN_KEY",
                message="Column key must be lowercase alphanumeric with hyphens only",
            )

        # Check column limit (8 max)
        columns = await list_board_columns(team_id)
        if len(columns) >= 8:
            raise ColumnServiceError(
                code="COLUMN_LIMIT_EXCEEDED",
                message="Team cannot have more than 8 columns",
            )

        # Set position to end if not provided
        if position is None:
            position = len(columns)

        # Create column
        created = await create_board_column(
            team_id=team_id,
            name=display_name,  # Use display_name as name
            key=key,
            display_name=display_name,
            position=position,
            wip_limit=wip_limit,
            is_locked=False,
        )

        return {
            "id": str(created["id"]),
            "key": created.get("key") or created.get("name"),
            "display_name": created.get("display_name") or created["name"],
            "name": created["name"],
            "position": created["position"],
            "wip_limit": created.get("wip_limit"),
            "is_locked": created.get("is_locked", False),
        }

    @staticmethod
    async def delete_column(
        team_id: UUID,
        column_key: str,
        migrate_tasks_to: Optional[str] = None,
        user: TokenData = None,
    ) -> None:
        """
        Delete a column.

        Args:
            team_id: Team ID
            column_key: Column key to delete
            migrate_tasks_to: Target column key for task migration
            user: Authenticated user

        Raises:
            ColumnServiceError: If validation fails
            AuthorizationError: If user doesn't have permission
        """
        # Check permissions - only admins can delete columns
        if user:
            user_role = await queries.get_user_role_in_team(team_id, user.user_id)
            if user_role != UserRole.ADMIN:
                raise AuthorizationError(
                    "Only admins can delete columns",
                    details={"required_role": "admin"},
                )

        # Get column
        columns = await list_board_columns(team_id)
        column = None
        column_id = None
        for c in columns:
            if c.get("key") == column_key or c.get("name") == column_key:
                column = c
                column_id = c["id"]
                break

        if not column:
            raise ColumnServiceError(
                code="COLUMN_NOT_FOUND",
                message=f"Column with key '{column_key}' not found",
            )

        # Check if column is locked
        if column.get("is_locked", False):
            raise ColumnServiceError(
                code="COLUMN_LOCKED",
                message="Cannot delete locked column",
            )

        # Check for tasks in this column
        tasks = await list_tasks(team_id, column_id=column_id)
        if tasks:
            if not migrate_tasks_to:
                raise ColumnServiceError(
                    code="COLUMN_HAS_TASKS",
                    message=f"Column has {len(tasks)} task(s). Provide migrate_tasks_to parameter.",
                    details={"task_count": len(tasks)},
                )

            # Validate target column exists
            target_column = None
            for c in columns:
                if c.get("key") == migrate_tasks_to or c.get("name") == migrate_tasks_to:
                    target_column = c
                    break

            if not target_column:
                raise ColumnServiceError(
                    code="INVALID_MIGRATION_TARGET",
                    message=f"Target column '{migrate_tasks_to}' not found",
                )

            # Migrate tasks
            for task in tasks:
                await update_task(
                    task_id=task["id"],
                    team_id=team_id,
                    column_id=target_column["id"],
                    column_key=migrate_tasks_to,
                )

        # Delete column
        deleted = await delete_board_column(column_id, team_id)
        if not deleted:
            raise ColumnServiceError(
                code="COLUMN_DELETE_FAILED",
                message="Failed to delete column",
            )

    @staticmethod
    async def move_task(
        team_id: UUID,
        task_id: UUID,
        column_key: str,
        user: TokenData,
        note: Optional[str] = None,
        client_action: Optional[str] = None,
    ) -> dict:
        """
        Move a task to a different column with validation and business rules.

        Args:
            team_id: Team ID
            task_id: Task ID
            column_key: Target column key
            user: Authenticated user
            note: Optional note for the move
            client_action: Optional client action identifier

        Returns:
            Task move response with from/to columns and timestamp

        Raises:
            ColumnServiceError: If validation fails or business rules are violated
        """
        # Get task
        task = await queries.get_task(task_id, team_id)
        if not task:
            raise ColumnServiceError(
                code="TASK_NOT_FOUND",
                message=f"Task {task_id} not found",
            )

        from_column_key = task.get("column_key")

        # Validate column exists
        columns = await list_board_columns(team_id)
        target_column = None
        for col in columns:
            if col.get("key") == column_key or col.get("name") == column_key:
                target_column = col
                break

        if not target_column:
            raise ColumnServiceError(
                code="INVALID_COLUMN_KEY",
                message=f"Column key '{column_key}' not found in team's board",
            )

        # Check if already in target column
        if from_column_key == column_key:
            raise ColumnServiceError(
                code="ALREADY_IN_COLUMN",
                message=f"Task is already in column '{column_key}'",
            )

        # Enforce WIP limits
        wip_limit = target_column.get("wip_limit")
        if wip_limit is not None:
            # Count tasks in target column
            tasks_in_column = await queries.list_tasks(team_id, column_id=target_column["id"])
            current_count = len(tasks_in_column)
            
            # If moving from this column, don't count the current task
            if from_column_key == target_column.get("key"):
                current_count = max(0, current_count - 1)

            if current_count >= wip_limit:
                raise ColumnServiceError(
                    code="WIP_LIMIT_EXCEEDED",
                    message=f"WIP limit ({wip_limit}) would be exceeded in column '{column_key}'",
                    details={
                        "current_count": current_count,
                        "wip_limit": wip_limit,
                        "column_key": column_key,
                    },
                )

        # Enforce AI review gating
        # Prevent AI-assigned tasks or high-risk tasks from moving directly to "done"
        target_key = target_column.get("key") or target_column.get("name", "").lower()
        if target_key == "done":
            assignee_type = task.get("assignee_type")
            tags = task.get("tags") or []
            task_tags_lower = [t.lower() for t in tags]
            
            # Check if coming from review column
            from_key = from_column_key or ""
            from_column = None
            for col in columns:
                if col.get("key") == from_key or col.get("name", "").lower() == from_key.lower():
                    from_column = col
                    break
            
            is_from_review = from_column and (
                from_column.get("key", "").lower() == "review" or
                from_column.get("name", "").lower() == "review"
            )

            # Block if:
            # 1. AI-assigned task AND not coming from review AND not approved
            # 2. Has review-heavy/approval-required/high-risk tags AND not coming from review AND not approved
            # 3. High assignment risk AND not coming from review AND not approved
            task_approved = task.get("approved", False)
            
            if not is_from_review and not task_approved:
                if assignee_type == "agent" or assignee_type == "ai":
                    raise ColumnServiceError(
                        code="AI_REVIEW_GATING",
                        message="AI-assigned tasks must be approved before moving to done",
                        details={
                            "assignee_type": assignee_type,
                            "from_column": from_column_key,
                            "to_column": column_key,
                            "approved": task_approved,
                        },
                    )
                
                review_tags = ["review-required", "approval-required", "high-risk"]
                has_review_tag = any(tag in task_tags_lower for tag in review_tags)
                assignment_risk = task.get("assignment_risk")
                
                if has_review_tag or assignment_risk == "high":
                    raise ColumnServiceError(
                        code="REVIEW_GATING",
                        message="Tasks with review requirements must be approved before moving to done",
                        details={
                            "tags": tags,
                            "assignment_risk": assignment_risk,
                            "from_column": from_column_key,
                            "to_column": column_key,
                            "approved": task_approved,
                        },
                    )

        # Update task
        updated = await update_task(
            task_id=task_id,
            team_id=team_id,
            column_id=target_column["id"],
            column_key=column_key,
        )

        if not updated:
            raise ColumnServiceError(
                code="TASK_UPDATE_FAILED",
                message="Failed to move task",
            )

        # Log audit event
        await create_event(
            team_id=team_id,
            event_type="task_moved",
            payload={
                "from_column": from_column_key,  # Support both naming conventions
                "from_column_key": from_column_key,
                "to_column": column_key,  # Support both naming conventions
                "to_column_key": column_key,
                "actor_user_id": user.user_id,
                "reason": note,  # Support 'reason' field as specified in work order
                "note": note,
                "client_action": client_action,
            },
            user_id=user.user_id,
            task_id=task_id,  # Store task_id in column for efficient queries
        )

        return {
            "task_id": task_id,
            "from_column_key": from_column_key,
            "to_column_key": column_key,
            "updated_at": updated["updated_at"],
        }
