"""Cerebras LLM integration service."""

import hashlib
import json
import logging
from pathlib import Path
from typing import Any, Callable, Optional

import httpx

from backend.app.core.config import settings
from backend.app.core.exceptions import APIException

logger = logging.getLogger(__name__)


class CerebrasLLMError(APIException):
    """Cerebras LLM service error."""

    def __init__(
        self,
        message: str,
        details: Optional[dict] = None,
        code: str = "LLM_ERROR",
        status_code: int = 500,
    ):
        """Initialize Cerebras LLM error."""
        super().__init__(
            code=code,
            message=message,
            status_code=status_code,
            details=details or {},
        )


class PolicyLoader:
    """Loads markdown policy files from the backend codebase."""

    @staticmethod
    def load_policy_file(filename: str) -> tuple[str, str]:
        """
        Load a policy file from the backend codebase.

        Args:
            filename: Name of the policy file (e.g., "task_splitting.md")

        Returns:
            Tuple of (content, hash) where hash is SHA256 of the content

        Raises:
            CerebrasLLMError: If file not found or cannot be read
        """
        # Policy files should be in backend/policies/ directory
        backend_dir = Path(__file__).parent.parent.parent
        policy_path = backend_dir / "policies" / filename

        if not policy_path.exists():
            raise CerebrasLLMError(
                f"Policy file not found: {filename}",
                details={"filename": filename, "path": str(policy_path)},
            )

        try:
            content = policy_path.read_text(encoding="utf-8")
            content_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
            return content, content_hash
        except Exception as e:
            raise CerebrasLLMError(
                f"Failed to read policy file: {filename}",
                details={"filename": filename, "error": str(e)},
            )

    @staticmethod
    def load_policies(*filenames: str) -> dict[str, tuple[str, str]]:
        """
        Load multiple policy files.

        Args:
            *filenames: Policy file names to load

        Returns:
            Dictionary mapping filename to (content, hash) tuple
        """
        return {filename: PolicyLoader.load_policy_file(filename) for filename in filenames}


class CerebrasLLMService:
    """Service for interacting with Cerebras LLM API."""

    def __init__(self):
        """Initialize Cerebras LLM service."""
        self.api_key = settings.cerebras_api_key
        self.model = settings.cerebras_model
        self.base_url = "https://api.cerebras.ai/v1"

        if not self.api_key:
            raise CerebrasLLMError("CEREBRAS_API_KEY not configured")

    async def generate_completion(
        self,
        prompt: str,
        max_retries: int = 3,
        temperature: float = 0.7,
        json_mode: bool = True,
    ) -> str:
        """
        Generate a completion using Cerebras LLM.

        Args:
            prompt: The prompt to send to the LLM
            max_retries: Maximum number of retry attempts for API calls
            temperature: Sampling temperature (0.0 to 1.0)
            json_mode: Whether to request JSON-only responses

        Returns:
            Generated text response

        Raises:
            CerebrasLLMError: If API call fails after retries
        """
        url = f"{self.base_url}/chat/completions"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": prompt},
            ],
            "temperature": temperature,
        }

        # Request JSON mode if supported
        if json_mode:
            payload["response_format"] = {"type": "json_object"}

        last_error = None
        for attempt in range(max_retries):
            try:
                async with httpx.AsyncClient(timeout=60.0) as client:
                    response = await client.post(url, headers=headers, json=payload)
                    
                    # Handle rate limits
                    if response.status_code == 429:
                        retry_after = response.headers.get("Retry-After", "60")
                        logger.warning(f"Rate limited, retrying after {retry_after}s")
                        if attempt < max_retries - 1:
                            import asyncio
                            await asyncio.sleep(int(retry_after))
                            continue
                    
                    response.raise_for_status()
                    data = response.json()

                    # Extract content from response
                    if "choices" in data and len(data["choices"]) > 0:
                        content = data["choices"][0].get("message", {}).get("content", "")
                        if content:
                            # Log response for audit
                            logger.info(f"LLM response received (attempt {attempt + 1})")
                            return content

                    raise CerebrasLLMError(
                        "Invalid response format from Cerebras API",
                        details={"response": data},
                    )
            except httpx.TimeoutException as e:
                last_error = e
                logger.warning(f"Timeout on attempt {attempt + 1}: {str(e)}")
                if attempt < max_retries - 1:
                    continue
                raise CerebrasLLMError(
                    f"Timeout calling Cerebras API after {max_retries} attempts",
                    details={"error": str(e), "attempt": attempt + 1},
                )
            except httpx.HTTPStatusError as e:
                last_error = e
                logger.error(f"HTTP error on attempt {attempt + 1}: {e.response.status_code}")
                if attempt < max_retries - 1 and e.response.status_code >= 500:
                    # Retry on server errors
                    continue
                raise CerebrasLLMError(
                    f"HTTP error from Cerebras API: {e.response.status_code}",
                    details={"error": str(e), "status_code": e.response.status_code},
                )
            except httpx.HTTPError as e:
                last_error = e
                logger.error(f"HTTP error on attempt {attempt + 1}: {str(e)}")
                if attempt < max_retries - 1:
                    continue
                raise CerebrasLLMError(
                    f"Failed to call Cerebras API after {max_retries} attempts",
                    details={"error": str(e), "attempt": attempt + 1},
                )
            except Exception as e:
                last_error = e
                logger.error(f"Unexpected error on attempt {attempt + 1}: {str(e)}")
                if attempt < max_retries - 1:
                    continue
                raise CerebrasLLMError(
                    f"Unexpected error calling Cerebras API: {str(e)}",
                    details={"error": str(e), "attempt": attempt + 1},
                )

        raise CerebrasLLMError(
            "Failed to generate completion",
            details={"error": str(last_error)},
        )

    async def generate_json_completion(
        self,
        prompt: str,
        schema_validator: Optional[Callable[[dict[str, Any]], list[str]]] = None,
        max_retries: int = 2,
        temperature: float = 0.7,
    ) -> dict[str, Any]:
        """
        Generate a JSON completion with schema validation and retry logic.

        Args:
            prompt: The prompt to send to the LLM
            schema_validator: Optional function that validates the parsed JSON and returns list of errors
            max_retries: Maximum retries for JSON validation (default 2: initial + 1 retry)
            temperature: Sampling temperature (0.0 to 1.0)

        Returns:
            Parsed JSON dictionary

        Raises:
            CerebrasLLMError: If JSON parsing or validation fails after retries
        """
        last_response = None
        last_errors = None

        for attempt in range(max_retries):
            try:
                # Build prompt with JSON correction instructions on retry
                current_prompt = prompt
                if attempt > 0:
                    correction_prompt = f"""
## IMPORTANT: JSON Schema Correction Required

Your previous response failed validation with these errors:
{chr(10).join(f"- {error}" for error in last_errors)}

Previous invalid response (for reference):
```json
{json.dumps(last_response, indent=2)[:500]}
```

You MUST respond with ONLY valid JSON that matches the required schema. Do not include any markdown, explanations, or code blocks. Return ONLY the JSON object.
"""
                    current_prompt = prompt + "\n\n" + correction_prompt

                # Generate completion
                response_text = await self.generate_completion(
                    prompt=current_prompt,
                    max_retries=3,  # API retries
                    temperature=temperature,
                    json_mode=True,
                )

                # Try to extract JSON from response
                json_text = response_text.strip()
                
                # Remove markdown code blocks if present
                if "```json" in json_text:
                    json_text = json_text.split("```json")[1].split("```")[0].strip()
                elif "```" in json_text:
                    json_text = json_text.split("```")[1].split("```")[0].strip()

                # Parse JSON
                try:
                    parsed = json.loads(json_text)
                except json.JSONDecodeError as e:
                    logger.warning(f"JSON parse error on attempt {attempt + 1}: {str(e)}")
                    last_response = response_text[:500]  # Store first 500 chars for retry
                    last_errors = [f"Invalid JSON: {str(e)}"]
                    if attempt < max_retries - 1:
                        continue
                    raise CerebrasLLMError(
                        code="INVALID_LLM_OUTPUT",
                        message="Failed to parse LLM response as JSON",
                        details={
                            "error": str(e),
                            "response_preview": response_text[:500],
                            "attempts": attempt + 1,
                        },
                    )

                # Validate schema if validator provided
                if schema_validator:
                    validation_errors = schema_validator(parsed)
                    if validation_errors:
                        logger.warning(
                            f"Schema validation failed on attempt {attempt + 1}: {validation_errors}",
                        )
                        last_response = parsed
                        last_errors = validation_errors
                        if attempt < max_retries - 1:
                            continue
                        raise CerebrasLLMError(
                            code="INVALID_LLM_OUTPUT",
                            message="LLM response failed schema validation",
                            details={
                                "errors": validation_errors,
                                "response": parsed,
                                "attempts": attempt + 1,
                            },
                        )

                # Success
                logger.info(f"JSON completion generated successfully (attempt {attempt + 1})")
                return parsed

            except CerebrasLLMError:
                # Re-raise LLM errors
                raise
            except Exception as e:
                logger.error(f"Unexpected error in JSON completion: {str(e)}")
                if attempt < max_retries - 1:
                    continue
                raise CerebrasLLMError(
                    code="INVALID_LLM_OUTPUT",
                    message=f"Failed to generate valid JSON: {str(e)}",
                    details={"error": str(e), "attempts": attempt + 1},
                )

        # Should not reach here, but handle it
        raise CerebrasLLMError(
            code="INVALID_LLM_OUTPUT",
            message="Failed to generate valid JSON after retries",
            details={"errors": last_errors, "attempts": max_retries},
        )

    def build_task_splitting_prompt(
        self,
        task_title: str,
        task_description: Optional[str],
        task_splitting_policy: str,
        tagging_rules_policy: str,
        instructions: Optional[str] = None,
    ) -> str:
        """
        Build a prompt for task splitting.

        Args:
            task_title: Title of the parent task
            task_description: Description of the parent task
            task_splitting_policy: Content of task_splitting.md policy
            tagging_rules_policy: Content of tagging_rules.md policy
            instructions: Optional user instructions

        Returns:
            Formatted prompt string
        """
        prompt_parts = [
            "# Task Splitting Request",
            "",
            "You are a task decomposition assistant. Your job is to break down a parent task into smaller, actionable subtasks.",
            "",
            "## Task Splitting Policy",
            task_splitting_policy,
            "",
            "## Tagging Rules",
            tagging_rules_policy,
            "",
            "## Parent Task",
            f"**Title:** {task_title}",
        ]

        if task_description:
            prompt_parts.append(f"**Description:** {task_description}")

        if instructions:
            prompt_parts.append("")
            prompt_parts.append("## Additional Instructions")
            prompt_parts.append(instructions)

        prompt_parts.extend([
            "",
            "## Output Format",
            "You must respond with a valid JSON object in the following format:",
            "",
            "```json",
            "{",
            '  "subtasks": [',
            "    {",
            '      "title": "Subtask title (non-empty string)",',
            '      "description": "Subtask description (non-empty string)",',
            '      "size": 1,  // Must be one of: 1, 2, 3, 5, 8',
            '      "tags": ["intern", "python", "api"]  // Must include exactly one seniority tag (intern, junior, mid, senior) and at least one skill tag',
            "    }",
            "  ]",
            "}",
            "```",
            "",
            "## Requirements",
            "- All subtask titles must be unique",
            "- All subtask descriptions must be non-empty",
            "- All sizes must be Fibonacci numbers: 1, 2, 3, 5, or 8",
            "- Each subtask must have exactly one seniority tag: intern, junior, mid, or senior",
            "- Each subtask must have at least one skill tag (matching the tagging rules)",
            "- All tags must be lowercase",
            "",
            "Generate the subtasks now:",
        ])

        return "\n".join(prompt_parts)

    def build_task_orchestration_prompt(
        self,
        subtasks: list[dict[str, Any]],
        team_members: list[dict[str, Any]],
        ai_agents: list[dict[str, Any]],
        orchestration_policy: str,
        strategy: str = "balanced",
        instructions: Optional[str] = None,
    ) -> str:
        """
        Build a prompt for task orchestration (assignment).

        Args:
            subtasks: List of subtask dictionaries with title, description, size, tags
            team_members: List of team member dictionaries with user_id, skills, level
            ai_agents: List of AI agent dictionaries with agent_id, capabilities
            orchestration_policy: Content of orchestration policy
            strategy: Orchestration strategy (balanced, speed, quality)
            instructions: Optional user instructions

        Returns:
            Formatted prompt string
        """
        prompt_parts = [
            "# Task Orchestration Request",
            "",
            "You are a task assignment assistant. Your job is to assign subtasks to team members or AI agents based on skills, availability, and workload.",
            "",
            "## Orchestration Policy",
            orchestration_policy,
            "",
            "## Strategy",
            f"Orchestration strategy: **{strategy}**",
            "- **balanced**: Balance workload and match skills appropriately",
            "- **speed**: Prioritize fastest completion, assign to most capable",
            "- **quality**: Prioritize best fit, assign to most skilled",
            "",
            "## Subtasks to Assign",
        ]

        for idx, subtask in enumerate(subtasks, 1):
            prompt_parts.append(f"### Subtask {idx}")
            prompt_parts.append(f"**Title:** {subtask.get('title', 'N/A')}")
            prompt_parts.append(f"**Description:** {subtask.get('description', 'N/A')}")
            prompt_parts.append(f"**Size:** {subtask.get('size', 'N/A')}")
            prompt_parts.append(f"**Tags:** {', '.join(subtask.get('tags', []))}")
            prompt_parts.append("")

        prompt_parts.extend([
            "## Available Team Members",
        ])

        for member in team_members:
            prompt_parts.append(f"- **{member.get('name', 'Unknown')}** (ID: {member.get('user_id', 'N/A')})")
            prompt_parts.append(f"  - Level: {member.get('level', 'N/A')}")
            prompt_parts.append(f"  - Skills: {', '.join(member.get('skills', []))}")
            prompt_parts.append("")

        if ai_agents:
            prompt_parts.extend([
                "## Available AI Agents",
            ])
            for agent in ai_agents:
                prompt_parts.append(f"- **{agent.get('name', 'Unknown')}** (ID: {agent.get('agent_id', 'N/A')})")
                prompt_parts.append(f"  - Capabilities: {', '.join(agent.get('capabilities', []))}")
                prompt_parts.append("")

        if instructions:
            prompt_parts.append("")
            prompt_parts.append("## Additional Instructions")
            prompt_parts.append(instructions)

        prompt_parts.extend([
            "",
            "## Output Format",
            "You must respond with a valid JSON object in the following format:",
            "",
            "```json",
            "{",
            '  "assignments": [',
            "    {",
            '      "subtask_index": 1,  // Index of subtask (1-based)',
            '      "assignee_type": "human",  // "human" or "ai"',
            '      "assignee_id": "user-uuid-or-agent-uuid",',
            '      "assignment_risk": "low",  // "low", "medium", or "high"',
            '      "reasoning": "Brief explanation of assignment decision"',
            "    }",
            "  ]",
            "}",
            "```",
            "",
            "## Requirements",
            "- Each subtask must be assigned to exactly one team member or AI agent",
            "- Assignment risk should reflect confidence in the match",
            "- Reasoning should explain why this assignment fits the strategy",
            "- Consider skills, level, and workload balance",
            "",
            "Generate the assignments now:",
        ])

        return "\n".join(prompt_parts)
