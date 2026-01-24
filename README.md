# Synth API

FastAPI backend application with Supabase authentication and role-based access control.

## Project Structure

```
backend/
├── app/
│   ├── api/
│   │   └── routes/          # API route handlers
│   ├── core/                 # Core utilities (config, middleware, exceptions)
│   ├── db/                   # Database models and queries
│   ├── llm/                  # LLM integration services
│   ├── schemas/              # Pydantic schemas
│   ├── services/             # Business logic services
│   └── main.py               # FastAPI application entry point
├── requirements.txt          # Python dependencies
└── pyproject.toml            # Project configuration
```

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file with the following variables (see `.env.example` for template):
```
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key
SUPABASE_DB_URL=postgresql://...
DATABASE_URL=postgresql://...
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
SUPABASE_JWT_SECRET=your_jwt_secret  # Get from Supabase Dashboard > Project Settings > API > JWT Secret
CEREBRAS_API_KEY=your_cerebras_key
CEREBRAS_MODEL=zai-glm-4.7
ENVIRONMENT=development
```

**Important**: The `SUPABASE_JWT_SECRET` is required for JWT token validation. 
Find it in your Supabase Dashboard under Project Settings > API > JWT Secret.

3. Run the application:
```bash
uvicorn backend.app.main:app --reload
```

The API will be available at `http://localhost:8000` with documentation at `http://localhost:8000/docs`.

## Features

- **FastAPI** with OpenAPI documentation
- **Supabase Auth** JWT token validation
- **Team scoping** middleware for team-based access control
- **Role-based access control** (admin, manager, member, viewer)
- **Standardized error handling** with consistent error response format
- **Health check endpoint** at `/health` (no authentication required)

## Architecture

- **Thin routes, fat services**: Route handlers delegate business logic to service layer
- **Middleware-based authentication**: JWT validation via dependency injection
- **Pydantic v2** for request/response validation

## Development

- **Linting**: `ruff check .`
- **Testing**: `pytest`
