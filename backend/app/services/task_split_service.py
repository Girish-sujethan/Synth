"""Task splitting service with LLM integration."""

import json
from typing import Any, Optional
from uuid import UUID

from backend.app.core.exceptions import APIException
from backend.app.db import queries
from backend.app.db.queries import create_event, create_task, get_task, get_task_children
from backend.app.llm.cerebras import CerebrasLLMService, PolicyLoader
from backend.app.schemas.auth import TokenData


class TaskSplitError(APIException):
    """Task splitting error."""

    def __init__(self, code: str, message: str, details: Optional[dict] = None):
        """Initialize task split error."""
        super().__init__(
            code=code,
            message=message,
            status_code=400,
            details=details or {},
        )


class TaskSplitService:
    """Service for splitting tasks using LLM."""

    # Valid Fibonacci sizes
    VALID_SIZES = {1, 2, 3, 5, 8}

    # Valid seniority tags
    VALID_SENIORITY_TAGS = {"intern", "junior", "mid", "senior"}

    def __init__(self):
        """Initialize task split service."""
        self.llm_service = CerebrasLLMService()
        self.policy_loader = PolicyLoader()

    async def validate_subtasks(self, subtasks: list[dict[str, Any]], tagging_rules_content: str) -> list[str]:
        """
        Validate subtasks according to requirements.

        Args:
            subtasks: List of subtask dictionaries
            tagging_rules_content: Content of tagging_rules.md for validation

        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []

        if not subtasks:
            errors.append("At least one subtask is required")
            return errors

        # Check for duplicate titles
        titles = [st.get("title", "").strip() for st in subtasks]
        if len(titles) != len(set(titles)):
            errors.append("Duplicate subtask titles found")

        # Validate each subtask
        for idx, subtask in enumerate(subtasks):
            prefix = f"Subtask {idx + 1}"

            # Validate title
            title = subtask.get("title", "").strip()
            if not title:
                errors.append(f"{prefix}: Title is required and must be non-empty")

            # Validate description
            description = subtask.get("description", "").strip()
            if not description:
                errors.append(f"{prefix}: Description is required and must be non-empty")

            # Validate size
            size = subtask.get("size")
            if size not in self.VALID_SIZES:
                errors.append(
                    f"{prefix}: Size must be one of {sorted(self.VALID_SIZES)}, got {size}",
                )

            # Validate tags
            tags = subtask.get("tags", [])
            if not isinstance(tags, list):
                errors.append(f"{prefix}: Tags must be a list")
                continue

            # Check for lowercase
            if not all(isinstance(tag, str) and tag == tag.lower() for tag in tags):
                errors.append(f"{prefix}: All tags must be lowercase strings")

            # Check for exactly one seniority tag
            seniority_tags = [tag for tag in tags if tag in self.VALID_SENIORITY_TAGS]
            if len(seniority_tags) != 1:
                errors.append(
                    f"{prefix}: Must have exactly one seniority tag from {sorted(self.VALID_SENIORITY_TAGS)}, "
                    f"found {len(seniority_tags)}: {seniority_tags}",
                )

            # Check for at least one skill tag (any tag that's not a seniority tag)
            skill_tags = [tag for tag in tags if tag not in self.VALID_SENIORITY_TAGS]
            if not skill_tags:
                errors.append(f"{prefix}: Must have at least one skill tag")

            # Note: We don't validate against tagging_rules.md content here since
            # the policy file content structure is not standardized. The LLM should
            # follow the rules, and we validate the structure.

        return errors

    async def split_task_preview(
        self,
        task_id: UUID,
        team_id: UUID,
        instructions: Optional[str] = None,
        policy_version: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Generate a preview of subtasks for a task split (without persisting.

        Args:
            task_id: ID of the task to split
            team_id: Team ID
            instructions: Optional user instructions
            policy_version: Optional policy version (for audit)

        Returns:
            Dictionary with subtasks, policy version, and model info

        Raises:
            TaskSplitError: If validation fails or LLM call fails
        """
        # Get parent task
        parent_task = await get_task(task_id, team_id)
        if not parent_task:
            raise TaskSplitError(
                code="TASK_NOT_FOUND",
                message=f"Task {task_id} not found",
            )

        # Check if task already has subtasks
        existing_children = await get_task_children(task_id, team_id)
        if existing_children:
            raise TaskSplitError(
                code="TASK_ALREADY_SPLIT",
                message=f"Task {task_id} already has {len(existing_children)} subtasks",
            )

        # Load policy files
        try:
            policies = self.policy_loader.load_policies("task_splitting.md", "tagging_rules.md")
            task_splitting_policy, task_splitting_hash = policies["task_splitting.md"]
            tagging_rules_policy, tagging_rules_hash = policies["tagging_rules.md"]
        except Exception as e:
            raise TaskSplitError(
                code="POLICY_LOAD_ERROR",
                message=f"Failed to load policy files: {str(e)}",
            )

        # Build prompt
        prompt = self.llm_service.build_task_splitting_prompt(
            task_title=parent_task["title"],
            task_description=parent_task.get("description"),
            task_splitting_policy=task_splitting_policy,
            tagging_rules_policy=tagging_rules_policy,
            instructions=instructions,
        )

        # Call LLM with JSON validation
        try:
            # Define schema validator
            def validate_subtasks_schema(parsed: dict[str, Any]) -> list[str]:
                """Validate the parsed JSON matches expected subtask schema."""
                errors = []
                if "subtasks" not in parsed:
                    errors.append("Missing 'subtasks' field in response")
                    return errors

                subtasks_list = parsed.get("subtasks", [])
                if not isinstance(subtasks_list, list):
                    errors.append("'subtasks' must be a list")
                    return errors

                return errors

            # Use JSON completion with validation
            parsed = await self.llm_service.generate_json_completion(
                prompt=prompt,
                schema_validator=validate_subtasks_schema,
                max_retries=2,  # Initial + 1 retry on validation failure
            )
            subtasks = parsed.get("subtasks", [])
        except Exception as e:
            # Check if it's already a TaskSplitError
            if isinstance(e, TaskSplitError):
                raise
            raise TaskSplitError(
                code="INVALID_LLM_OUTPUT",
                message=f"Failed to generate valid subtasks: {str(e)}",
                details={"error": str(e)},
            )

        # Validate subtasks
        validation_errors = await self.validate_subtasks(subtasks, tagging_rules_policy)
        if validation_errors:
            raise TaskSplitError(
                code="INVALID_LLM_OUTPUT",
                message="LLM output failed validation",
                details={"errors": validation_errors, "subtasks": subtasks},
            )

        # Return preview (no database persistence)
        policy_version_hash = f"{task_splitting_hash[:8]}-{tagging_rules_hash[:8]}"
        if policy_version:
            policy_version_hash = policy_version

        return {
            "subtasks": subtasks,
            "policy_version": policy_version_hash,
            "model": self.llm_service.model,
            "parent_task_id": task_id,  # Keep as UUID
        }

    async def confirm_split(
        self,
        task_id: UUID,
        team_id: UUID,
        subtasks: list[dict[str, Any]],
        user: TokenData,
        instructions: Optional[str] = None,
        policy_version: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Confirm and persist subtasks from a task split.

        Args:
            task_id: ID of the parent task
            team_id: Team ID
            subtasks: List of subtask dictionaries (may be user-edited)
            user: Authenticated user
            instructions: Optional user instructions (for audit)
            policy_version: Optional policy version (for audit)

        Returns:
            Dictionary with created subtask IDs and audit info

        Raises:
            TaskSplitError: If validation fails
        """
        # Get parent task
        parent_task = await get_task(task_id, team_id)
        if not parent_task:
            raise TaskSplitError(
                code="TASK_NOT_FOUND",
                message=f"Task {task_id} not found",
            )

        # Check if task already has subtasks
        existing_children = await get_task_children(task_id, team_id)
        if existing_children:
            raise TaskSplitError(
                code="TASK_ALREADY_SPLIT",
                message=f"Task {task_id} already has {len(existing_children)} subtasks",
            )

        # Load tagging rules for validation
        try:
            _, tagging_rules_hash = self.policy_loader.load_policy_file("tagging_rules.md")
        except Exception:
            # If policy file doesn't exist, we'll still validate structure
            tagging_rules_hash = "unknown"

        # Validate user-edited subtasks
        validation_errors = await self.validate_subtasks(subtasks, "")
        if validation_errors:
            raise TaskSplitError(
                code="INVALID_SUBTASK_DATA",
                message="Subtask data failed validation",
                details={"errors": validation_errors},
            )

        # Get parent task's column info
        parent_column_id = parent_task.get("column_id")
        parent_column_key = parent_task.get("column_key")

        # Create subtasks in the same column as parent
        created_subtask_ids = []
        for subtask in subtasks:
            subtask_record = await create_task(
                team_id=team_id,
                title=subtask["title"],
                description=subtask.get("description", ""),
                parent_id=task_id,
                status="todo",
                assignee_type=None,
                assignee_id=None,
                assignment_risk=None,
                column_id=parent_column_id,
                column_key=parent_column_key,
                override_flag=False,
                size=subtask.get("size"),
                tags=subtask.get("tags", []),
            )
            created_subtask_ids.append(str(subtask_record["id"]))

        # Load policy files for audit
        try:
            policies = self.policy_loader.load_policies("task_splitting.md", "tagging_rules.md")
            task_splitting_hash = policies["task_splitting.md"][1]
            tagging_rules_hash = policies["tagging_rules.md"][1]
            policy_version_hash = f"{task_splitting_hash[:8]}-{tagging_rules_hash[:8]}"
        except Exception:
            policy_version_hash = policy_version or "unknown"

        # Create audit event
        await create_event(
            team_id=team_id,
            event_type="task_split",
            payload={
                "task_id": str(task_id),
                "subtask_count": len(created_subtask_ids),
                "subtask_ids": created_subtask_ids,
                "policy_version": policy_version_hash,
                "model": self.llm_service.model,
                "instructions": instructions,
            },
            user_id=user.user_id,
        )

        return {
            "parent_task_id": str(task_id),
            "subtask_ids": created_subtask_ids,
            "subtask_count": len(created_subtask_ids),
            "policy_version": policy_version_hash,
            "model": self.llm_service.model,
        }
