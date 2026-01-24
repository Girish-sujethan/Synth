# Task Splitting Policy

**Version:** 1.0  
**Purpose:** Define how parent tasks should be decomposed into smaller, actionable subtasks using LLM assistance.

## Core Principles

1. **Atomicity**: Each subtask must be independently actionable and completable as a single work unit.
2. **Completeness**: Each subtask should have a clear deliverable or outcome that can be verified.
3. **Appropriate Granularity**: Subtasks should be small enough to complete in a single work session but meaningful enough to provide value.
4. **Minimal Dependencies**: Prefer parallelizable subtasks when possible. When dependencies exist, make them explicit and minimal.

## Decomposition Strategy

### When to Split a Task

Split a task when:
- The task requires multiple distinct skills or knowledge areas
- The task can be logically divided into sequential or parallel work streams
- The task is too large to complete in a single focused work session
- Different parts of the task can be assigned to different team members
- The task involves multiple deliverables or components

### When to Keep a Task Whole

Keep a task whole when:
- The task is already appropriately sized (Fibonacci: 1, 2, 3, 5, 8)
- The task cannot be meaningfully divided without losing context
- All parts of the task are tightly coupled and must be done together
- The task is a single, cohesive unit of work

## Subtask Requirements

### Size Requirements

- All subtasks must use Fibonacci sizing: **1, 2, 3, 5, or 8**
- Size should reflect the relative effort/complexity of the subtask
- Smaller subtasks (1-2) are preferred for clarity and progress tracking
- Larger subtasks (5-8) should only be used when the work cannot be further decomposed

### Title Requirements

- Must be clear, specific, and action-oriented
- Should indicate what will be delivered or accomplished
- Avoid vague terms like "work on", "fix", "improve" without specifics
- Good: "Implement user authentication API endpoint"
- Poor: "Work on authentication"

### Description Requirements

- Must be non-empty and provide sufficient context
- Should explain what needs to be done and why
- Include acceptance criteria or definition of done when applicable
- Reference parent task context when relevant

### Independence Requirements

- Each subtask should be completable without waiting for other subtasks (when possible)
- If dependencies exist, they should be minimal and clearly identifiable
- Prefer parallel work streams over sequential dependencies

## Examples

### Good Task Decomposition

**Parent Task:** "Build user authentication system"

**Subtasks:**
1. **Title:** "Design authentication database schema"  
   **Size:** 2  
   **Description:** "Create database tables for users, sessions, and password hashes. Include indexes for email lookup."

2. **Title:** "Implement password hashing and validation"  
   **Size:** 3  
   **Description:** "Create utility functions for bcrypt password hashing, verification, and strength validation."

3. **Title:** "Build login API endpoint"  
   **Size:** 3  
   **Description:** "Create POST /api/auth/login endpoint that validates credentials and returns JWT token."

4. **Title:** "Implement JWT token generation and validation"  
   **Size:** 2  
   **Description:** "Create JWT service for token creation, signing, and verification with configurable expiration."

### Poor Task Decomposition

**Parent Task:** "Build user authentication system"

**Subtasks:**
1. **Title:** "Work on authentication"  
   **Size:** 8  
   **Description:** "Do authentication stuff"  
   **Problems:** Vague title, too large, no clear deliverable

2. **Title:** "Fix bugs"  
   **Size:** 5  
   **Description:** ""  
   **Problems:** Empty description, not specific, no clear scope

3. **Title:** "Authentication part 1"  
   **Size:** 3  
   **Description:** "First part of authentication"  
   **Problems:** Unclear what "part 1" means, no independence

## Parallelization Guidelines

When decomposing tasks, identify opportunities for parallel work:

- **Frontend and Backend**: If a feature has both frontend and backend components, split them
- **API and Database**: Database schema design can often proceed in parallel with API design
- **Core Logic and Testing**: While not fully parallel, test planning can begin early
- **Documentation and Implementation**: Documentation can be written alongside implementation

## Validation Rules

When generating subtasks, ensure:
- All subtask titles are unique within the split
- All subtask descriptions are non-empty
- All subtask sizes are valid Fibonacci numbers (1, 2, 3, 5, 8)
- Each subtask has exactly one seniority tag (intern, junior, mid, senior)
- Each subtask has at least one skill tag
- All tags are lowercase
- Subtasks are appropriately sized for their complexity

## Output Format

When generating subtasks, always return a JSON object with this structure:

```json
{
  "subtasks": [
    {
      "title": "Clear, specific subtask title",
      "description": "Detailed description of what needs to be done",
      "size": 2,
      "tags": ["mid", "python", "api"]
    }
  ]
}
```
