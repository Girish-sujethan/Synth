"""Task orchestration service with LLM integration."""

import json
from typing import Any, Optional
from uuid import UUID

from backend.app.core.exceptions import APIException
from backend.app.db import queries
from backend.app.db.queries import (
    create_event,
    get_task,
    get_task_children,
    get_team_context_for_orchestration,
    update_profile,
    update_task,
)
from backend.app.llm.cerebras import CerebrasLLMService, PolicyLoader
from backend.app.schemas.auth import TokenData, UserRole


class TaskOrchestrationError(APIException):
    """Task orchestration error."""

    def __init__(self, code: str, message: str, details: Optional[dict] = None):
        """Initialize task orchestration error."""
        super().__init__(
            code=code,
            message=message,
            status_code=400,
            details=details or {},
        )


class TaskOrchestrationService:
    """Service for orchestrating task assignments using LLM."""

    # Valid seniority tags
    VALID_SENIORITY_TAGS = {"intern", "junior", "mid", "senior"}

    def __init__(self):
        """Initialize task orchestration service."""
        self.llm_service = CerebrasLLMService()
        self.policy_loader = PolicyLoader()

    def _extract_seniority_from_tags(self, tags: list[str]) -> Optional[str]:
        """Extract seniority tag from task tags."""
        for tag in tags:
            if tag in self.VALID_SENIORITY_TAGS:
                return tag
        return None

    async def validate_assignment(
        self,
        assignment: dict[str, Any],
        subtask: dict[str, Any],
        team_id: UUID,
        team_members: list[dict[str, Any]],
        ai_agents: list[dict[str, Any]],
    ) -> list[str]:
        """
        Validate a single assignment according to business rules.

        Args:
            assignment: Assignment dictionary with assignee_type, assignee_id, etc.
            subtask: Subtask dictionary with title, tags, size
            team_id: Team ID
            team_members: List of team member dictionaries
            ai_agents: List of AI agent dictionaries

        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []

        assignee_type = assignment.get("assignee_type")
        assignee_id = assignment.get("assignee_id")

        if assignee_type not in ["human", "ai"]:
            errors.append(f"Invalid assignee_type: {assignee_type}")

        if not assignee_id:
            errors.append("assignee_id is required")

        # Validate assignee belongs to team
        if assignee_type == "human":
            # Check if user is a team member
            user_found = False
            user_profile = None
            for member in team_members:
                if member.get("user_id") == assignee_id:
                    user_found = True
                    user_profile = member
                    break

            if not user_found:
                errors.append(f"Assignee {assignee_id} is not a member of team {team_id}")

            # Validate seniority requirements
            if user_profile:
                subtask_seniority = self._extract_seniority_from_tags(subtask.get("tags", []))
                user_level = user_profile.get("level")

                # Map user level to seniority tag
                level_to_seniority = {
                    "intern": "intern",
                    "junior": "junior",
                    "mid": "mid",
                    "senior": "senior",
                    "staff": "senior",
                    "principal": "senior",
                }

                if subtask_seniority and user_level:
                    user_seniority = level_to_seniority.get(user_level)
                    # User should be at or above required seniority
                    seniority_order = ["intern", "junior", "mid", "senior"]
                    if user_seniority:
                        required_idx = seniority_order.index(subtask_seniority)
                        user_idx = seniority_order.index(user_seniority)
                        if user_idx < required_idx:
                            errors.append(
                                f"User level {user_level} does not meet required seniority {subtask_seniority}",
                            )

                # Check workload threshold (simple check: load < 1.0 means available)
                current_load = user_profile.get("load", 0.0)
                if current_load >= 1.0:
                    errors.append(f"User {assignee_id} is at capacity (load: {current_load})")

        elif assignee_type == "ai":
            # Check if agent exists in team
            agent_found = False
            for agent in ai_agents:
                if str(agent.get("id")) == str(assignee_id):
                    agent_found = True
                    break

            if not agent_found:
                errors.append(f"AI agent {assignee_id} not found in team {team_id}")

            # AI restrictions: cannot receive senior-level, high-risk, or approval-required tasks
            subtask_seniority = self._extract_seniority_from_tags(subtask.get("tags", []))
            if subtask_seniority == "senior":
                errors.append("AI agents cannot be assigned senior-level tasks")

            assignment_risk = assignment.get("assignment_risk", "low")
            if assignment_risk == "high":
                errors.append("AI agents cannot be assigned high-risk tasks")

        return errors

    async def orchestrate_preview(
        self,
        task_id: UUID,
        team_id: UUID,
        strategy: str = "balanced",
        instructions: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Generate a preview of task assignments for orchestration (without persisting).

        Args:
            task_id: ID of the parent task
            team_id: Team ID
            strategy: Orchestration strategy (balanced, speed, quality)
            instructions: Optional user instructions

        Returns:
            Dictionary with assignments, policy version, and model info

        Raises:
            TaskOrchestrationError: If validation fails or LLM call fails
        """
        # Get parent task
        parent_task = await get_task(task_id, team_id)
        if not parent_task:
            raise TaskOrchestrationError(
                code="TASK_NOT_FOUND",
                message=f"Task {task_id} not found",
            )

        # Get subtasks
        subtasks = await get_task_children(task_id, team_id)
        if not subtasks:
            raise TaskOrchestrationError(
                code="NO_SUBTASKS",
                message=f"Task {task_id} has no subtasks to orchestrate",
            )

        # Get team context
        team_context = await get_team_context_for_orchestration(team_id)

        # Load policy files
        try:
            policies = self.policy_loader.load_policies("orchestration_policy.md", "tagging_rules.md")
            orchestration_policy, orchestration_hash = policies["orchestration_policy.md"]
            tagging_rules_policy, tagging_rules_hash = policies["tagging_rules.md"]
        except Exception as e:
            raise TaskOrchestrationError(
                code="POLICY_LOAD_ERROR",
                message=f"Failed to load policy files: {str(e)}",
            )

        # Prepare subtasks data
        subtasks_data = []
        for subtask in subtasks:
            subtasks_data.append({
                "title": subtask["title"],
                "description": subtask.get("description", ""),
                "size": subtask.get("size"),
                "tags": subtask.get("tags", []),
            })

        # Prepare team members data
        team_members_data = []
        for member in team_context["team_members"]:
            skills = member.get("skills", {})
            if isinstance(skills, dict):
                skills_list = list(skills.keys()) if skills else []
            else:
                skills_list = skills if isinstance(skills, list) else []

            team_members_data.append({
                "user_id": member["user_id"],
                "name": member.get("name", "Unknown"),
                "level": member.get("level"),
                "skills": skills_list,
                "velocity": member.get("velocity", 0.0),
                "load": member.get("load", 0.0),
            })

        # Prepare AI agents data
        ai_agents_data = []
        for agent in team_context["ai_agents"]:
            ai_agents_data.append({
                "agent_id": str(agent["id"]),
                "name": agent.get("name", "Unknown"),
                "capabilities": agent.get("capabilities_md", ""),
                "tags": agent.get("tags", []),
            })

        # Build prompt
        prompt = self.llm_service.build_task_orchestration_prompt(
            subtasks=subtasks_data,
            team_members=team_members_data,
            ai_agents=ai_agents_data,
            orchestration_policy=orchestration_policy,
            strategy=strategy,
            instructions=instructions,
        )

        # Call LLM with JSON validation
        try:
            # Define schema validator
            def validate_orchestration_schema(parsed: dict[str, Any]) -> list[str]:
                """Validate the parsed JSON matches expected orchestration schema."""
                errors = []
                if "assignments" not in parsed:
                    errors.append("Missing 'assignments' field in response")
                    return errors

                assignments_list = parsed.get("assignments", [])
                if not isinstance(assignments_list, list):
                    errors.append("'assignments' must be a list")
                    return errors

                return errors

            # Use JSON completion with validation
            parsed = await self.llm_service.generate_json_completion(
                prompt=prompt,
                schema_validator=validate_orchestration_schema,
                max_retries=2,
            )
            assignments = parsed.get("assignments", [])
        except Exception as e:
            if isinstance(e, TaskOrchestrationError):
                raise
            raise TaskOrchestrationError(
                code="INVALID_LLM_OUTPUT",
                message=f"Failed to generate valid assignments: {str(e)}",
                details={"error": str(e)},
            )

        # Validate assignments against business rules
        validation_errors = []
        subtask_indices = set()

        for assignment in assignments:
            subtask_index = assignment.get("subtask_index")
            if subtask_index is None:
                validation_errors.append("Assignment missing subtask_index")
                continue

            # Check for duplicate assignments
            if subtask_index in subtask_indices:
                validation_errors.append(f"Subtask {subtask_index} assigned multiple times")
            subtask_indices.add(subtask_index)

            # Validate subtask index is valid
            if subtask_index < 1 or subtask_index > len(subtasks):
                validation_errors.append(f"Invalid subtask_index: {subtask_index}")
                continue

            # Get subtask
            subtask = subtasks[subtask_index - 1]  # Convert to 0-based index
            subtask_data = {
                "title": subtask["title"],
                "tags": subtask.get("tags", []),
                "size": subtask.get("size"),
            }

            # Validate assignment
            assignment_errors = await self.validate_assignment(
                assignment=assignment,
                subtask=subtask_data,
                team_id=team_id,
                team_members=team_context["team_members"],
                ai_agents=team_context["ai_agents"],
            )
            validation_errors.extend([f"Subtask {subtask_index}: {e}" for e in assignment_errors])

        # Check all subtasks are assigned
        if len(subtask_indices) != len(subtasks):
            missing = set(range(1, len(subtasks) + 1)) - subtask_indices
            validation_errors.append(f"Missing assignments for subtasks: {sorted(missing)}")

        if validation_errors:
            raise TaskOrchestrationError(
                code="INVALID_ASSIGNMENT_DATA",
                message="Assignment validation failed",
                details={"errors": validation_errors},
            )

        # Return preview (no database persistence)
        policy_version_hash = f"{orchestration_hash[:8]}-{tagging_rules_hash[:8]}"

        return {
            "assignments": assignments,
            "policy_version": policy_version_hash,
            "model": self.llm_service.model,
            "parent_task_id": str(task_id),
        }

    async def confirm_orchestration(
        self,
        task_id: UUID,
        team_id: UUID,
        assignments: list[dict[str, Any]],
        user: TokenData,
        instructions: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Confirm and persist task assignments from orchestration.

        Args:
            task_id: ID of the parent task
            team_id: Team ID
            assignments: List of assignment dictionaries
            user: Authenticated user
            instructions: Optional user instructions (for audit)

        Returns:
            Dictionary with assignment results and audit info

        Raises:
            TaskOrchestrationError: If validation fails
        """
        # Get parent task
        parent_task = await get_task(task_id, team_id)
        if not parent_task:
            raise TaskOrchestrationError(
                code="TASK_NOT_FOUND",
                message=f"Task {task_id} not found",
            )

        # Get subtasks
        subtasks = await get_task_children(task_id, team_id)
        if not subtasks:
            raise TaskOrchestrationError(
                code="NO_SUBTASKS",
                message=f"Task {task_id} has no subtasks to orchestrate",
            )

        # Get team context
        team_context = await get_team_context_for_orchestration(team_id)

        # Validate all assignments
        validation_errors = []
        subtask_indices = set()

        for assignment in assignments:
            subtask_index = assignment.get("subtask_index")
            if subtask_index is None:
                validation_errors.append("Assignment missing subtask_index")
                continue

            if subtask_index in subtask_indices:
                validation_errors.append(f"Subtask {subtask_index} assigned multiple times")
            subtask_indices.add(subtask_index)

            if subtask_index < 1 or subtask_index > len(subtasks):
                validation_errors.append(f"Invalid subtask_index: {subtask_index}")
                continue

            subtask = subtasks[subtask_index - 1]
            subtask_data = {
                "title": subtask["title"],
                "tags": subtask.get("tags", []),
                "size": subtask.get("size"),
            }

            assignment_errors = await self.validate_assignment(
                assignment=assignment,
                subtask=subtask_data,
                team_id=team_id,
                team_members=team_context["team_members"],
                ai_agents=team_context["ai_agents"],
            )
            validation_errors.extend([f"Subtask {subtask_index}: {e}" for e in assignment_errors])

        if len(subtask_indices) != len(subtasks):
            missing = set(range(1, len(subtasks) + 1)) - subtask_indices
            validation_errors.append(f"Missing assignments for subtasks: {sorted(missing)}")

        if validation_errors:
            raise TaskOrchestrationError(
                code="INVALID_ASSIGNMENT_DATA",
                message="Assignment validation failed",
                details={"errors": validation_errors},
            )

        # Apply assignments and update workloads
        assignment_results = []
        for assignment in assignments:
            subtask_index = assignment["subtask_index"]
            subtask = subtasks[subtask_index - 1]

            assignee_type = assignment["assignee_type"]
            assignee_id = UUID(assignment["assignee_id"])
            assignment_risk = assignment.get("assignment_risk", "low")

            # Map assignee_type to database enum
            db_assignee_type = "user" if assignee_type == "human" else "agent"

            # Update task assignment
            await update_task(
                task_id=subtask["id"],
                team_id=team_id,
                assignee_type=db_assignee_type,
                assignee_id=assignee_id,
                assignment_risk=assignment_risk,
            )

            # Update workload for human assignees
            if assignee_type == "human":
                # Find user profile
                for member in team_context["team_members"]:
                    if member.get("user_id") == str(assignee_id):
                        current_load = member.get("load", 0.0)
                        task_size = subtask.get("size", 1)
                        # Simple workload calculation: add task size to load
                        new_load = current_load + (task_size / 8.0)  # Normalize to 0-1 scale
                        await update_profile(
                            user_id=member["user_id"],
                            team_id=team_id,
                            load=new_load,
                        )
                        break

            assignment_results.append({
                "subtask_id": str(subtask["id"]),
                "assignee_type": assignee_type,
                "assignee_id": str(assignee_id),
                "assignment_risk": assignment_risk,
            })

        # Load policy files for audit
        try:
            policies = self.policy_loader.load_policies("orchestration_policy.md", "tagging_rules.md")
            orchestration_hash = policies["orchestration_policy.md"][1]
            tagging_rules_hash = policies["tagging_rules.md"][1]
            policy_version_hash = f"{orchestration_hash[:8]}-{tagging_rules_hash[:8]}"
        except Exception:
            policy_version_hash = "unknown"

        # Create audit event
        await create_event(
            team_id=team_id,
            event_type="task_orchestrated",
            payload={
                "task_id": str(task_id),
                "assignment_count": len(assignment_results),
                "assignments": assignment_results,
                "policy_version": policy_version_hash,
                "model": self.llm_service.model,
                "instructions": instructions,
            },
            user_id=user.user_id,
        )

        return {
            "parent_task_id": str(task_id),
            "assignments": assignment_results,
            "assignment_count": len(assignment_results),
            "policy_version": policy_version_hash,
            "model": self.llm_service.model,
        }
