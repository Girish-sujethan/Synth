# Risk Assessment Edge Function

Supabase Edge Function that integrates with Cerebras LLM to perform risk assessment analysis of subtasks.

## Overview

This Edge Function analyzes software development subtasks for risk factors including:
- Legacy system involvement
- Complexity levels
- Specialized skills requirements
- External dependencies

It generates structured risk assessments and stores them in the database.

## Environment Variables

The following environment variables must be set in your Supabase project:

- `CEREBRAS_API_KEY` - Your Cerebras LLM API key
- `CEREBRAS_API_URL` - (Optional) Cerebras API endpoint, defaults to `https://api.cerebras.ai/v1/chat/completions`
- `CEREBRAS_MODEL` - (Optional) Model to use, defaults to `llama-3.1-8b-instruct`
- `SUPABASE_URL` - Automatically available in Edge Functions
- `SUPABASE_SERVICE_ROLE_KEY` - Automatically available in Edge Functions

## Request Format

```json
{
  "task_id": 1,
  "subtasks": [
    {
      "id": "subtask_1",
      "description": "Implement user authentication",
      "dependencies": ["dep_1"]
    }
  ],
  "dependencies": [
    {
      "id": "dep_1",
      "type": "external_api",
      "description": "OAuth provider integration"
    }
  ]
}
```

## Response Format

```json
{
  "success": true,
  "task_id": 1,
  "assessments_created": 1,
  "total_subtasks": 1,
  "results": [
    {
      "subtask_id": "subtask_1",
      "risk_level": "medium",
      "risk_factors_count": 2
    }
  ]
}
```

## Deployment

Deploy using Supabase CLI:

```bash
supabase functions deploy assess-risks
```

## Error Handling

The function includes graceful error handling:
- If LLM API fails, falls back to default risk assessment
- Continues processing remaining subtasks if one fails
- Creates reasoning traces even for failed assessments
- Returns partial results if some assessments succeed

