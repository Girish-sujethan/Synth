# Task Orchestration Policy

**Version:** 1.0  
**Purpose:** Define how tasks should be assigned to team members or AI agents based on skills, workload, and risk assessment.

## Core Principles

1. **Skill Matching**: Assign tasks to team members or agents with matching or compatible skills.
2. **Workload Balance**: Distribute work evenly across team members to avoid overloading.
3. **Risk Management**: Assess assignment risk based on skill match, complexity, and assignee experience.
4. **Seniority Alignment**: Ensure assignee seniority level matches or exceeds task requirements.

## Assignment Strategies

### Balanced Strategy (Default)

- Distribute work evenly across available team members
- Match skills while considering current workload
- Prefer team members with appropriate seniority level
- Balance between speed and quality

### Speed Strategy

- Assign to most capable team member or agent
- Prioritize fastest completion over perfect skill match
- May overload high-performing team members
- Suitable for time-sensitive work

### Quality Strategy

- Assign to best-skilled team member or agent
- Prioritize perfect skill match and experience
- May take longer but ensures high quality
- Suitable for critical or complex work

## Assignment Rules

### Human Assignments

1. **Skill Requirements**: Assignee must have skills matching task tags
2. **Seniority Requirements**: Assignee level must meet or exceed task seniority tag
3. **Workload Limits**: Assignee load should be below 1.0 (100% capacity)
4. **Team Membership**: Assignee must be a member of the same team

### AI Agent Assignments

1. **Capability Matching**: Agent must have capabilities matching task requirements
2. **Tag Restrictions**: Agent tags should align with task tags
3. **Seniority Restrictions**: AI agents cannot be assigned senior-level tasks
4. **Risk Restrictions**: AI agents cannot be assigned high-risk tasks
5. **Approval Requirements**: Tasks requiring approval cannot be assigned to AI agents

## Risk Assessment

### Low Risk
- Strong skill match
- Assignee has completed similar tasks
- Task complexity matches assignee level
- Clear requirements and acceptance criteria

### Medium Risk
- Partial skill match
- Assignee has some relevant experience
- Task complexity slightly above assignee level
- Some ambiguity in requirements

### High Risk
- Weak skill match
- Assignee lacks relevant experience
- Task complexity significantly above assignee level
- Unclear requirements or high uncertainty

## Workload Calculation

- Task size (Fibonacci: 1, 2, 3, 5, 8) contributes to workload
- Normalize task size to 0-1 scale (divide by 8)
- Current load + new task load should not exceed 1.0
- Consider velocity when calculating capacity

## Assignment Process

1. **Analyze Subtasks**: Review each subtask's requirements (tags, size, seniority)
2. **Evaluate Team Members**: Assess skills, level, current workload, and availability
3. **Evaluate AI Agents**: Assess capabilities, tag alignment, and restrictions
4. **Match Assignments**: Create assignments based on strategy and rules
5. **Assess Risk**: Evaluate risk level for each assignment
6. **Provide Reasoning**: Explain why each assignment was made

## Output Format

When generating assignments, return a JSON object with this structure:

```json
{
  "assignments": [
    {
      "subtask_index": 1,
      "assignee_type": "human",
      "assignee_id": "user-uuid",
      "assignment_risk": "low",
      "reasoning": "Strong Python and API skills, appropriate seniority level, current workload allows"
    }
  ]
}
```

## Requirements

- Each subtask must be assigned exactly once
- Assignment risk must be one of: low, medium, high
- Reasoning should explain the assignment decision
- Consider strategy when making assignments
- Respect all restrictions (AI agent limits, workload thresholds, etc.)
