"""Task approval service for AI task approval workflow."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from backend.app.core.exceptions import APIException
from backend.app.db import queries
from backend.app.db.queries import create_event, get_task, update_task
from backend.app.schemas.auth import TokenData


class TaskApprovalError(APIException):
    """Task approval error."""

    def __init__(self, code: str, message: str, details: Optional[dict] = None):
        """Initialize task approval error."""
        super().__init__(
            code=code,
            message=message,
            status_code=400,
            details=details or {},
        )


class TaskApprovalService:
    """Service for approving AI-assigned tasks."""

    @staticmethod
    async def approve_task(
        task_id: UUID,
        team_id: UUID,
        approved: bool,
        user: TokenData,
        comment: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Approve or reject an AI-assigned task.

        Args:
            task_id: ID of the task to approve
            team_id: Team ID
            approved: Whether the task is approved (True) or rejected (False)
            user: Authenticated user performing the approval
            comment: Optional comment on the approval decision

        Returns:
            Dictionary with approval result

        Raises:
            TaskApprovalError: If validation fails
        """
        # Get task
        task = await get_task(task_id, team_id)
        if not task:
            raise TaskApprovalError(
                code="TASK_NOT_FOUND",
                message=f"Task {task_id} not found",
            )

        # Check if task is AI-assigned or has approval-required tags
        assignee_type = task.get("assignee_type")
        task_tags = task.get("tags", [])
        task_tags_lower = [tag.lower() for tag in task_tags]

        is_ai_task = assignee_type in ["agent", "ai"]
        has_approval_tag = any(
            tag in task_tags_lower
            for tag in ["review-heavy", "approval-required", "high-risk"]
        )

        if not is_ai_task and not has_approval_tag:
            raise TaskApprovalError(
                code="TASK_NOT_ELIGIBLE_FOR_APPROVAL",
                message="Task is not eligible for approval (not AI-assigned and no approval-required tags)",
                details={
                    "assignee_type": assignee_type,
                    "tags": task_tags,
                },
            )

        # Update task approval state
        now = datetime.utcnow()
        updated = await update_task(
            task_id=task_id,
            team_id=team_id,
            approved=approved,
            approved_at=now if approved else None,
            approved_by=user.user_id if approved else None,
            approval_comment=comment,
        )

        if not updated:
            raise TaskApprovalError(
                code="APPROVAL_UPDATE_FAILED",
                message="Failed to update task approval state",
            )

        # Create audit event
        await create_event(
            team_id=team_id,
            event_type="ai_task_approved",
            payload={
                "task_id": str(task_id),
                "approved": approved,
                "comment": comment,
                "assignee_type": assignee_type,
            },
            user_id=user.user_id,
        )

        return {
            "task_id": str(task_id),
            "approved": approved,
            "approved_at": now.isoformat() if approved else None,
            "approved_by": user.user_id if approved else None,
            "comment": comment,
        }
