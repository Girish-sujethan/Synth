# Synth API

FastAPI backend with Supabase authentication and PostgreSQL database.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure environment variables in `.env` file:
```
SUPABASE_URL=your_supabase_url
SUPABASE_DB_URL=postgresql://user:password@host:port/database
ENVIRONMENT=development
```

## Running the Application

```bash
python main.py
```

Or using uvicorn directly:
```bash
uvicorn main:app --reload
```

## Testing

The project uses pytest for unit testing. All tests are located in the `tests/` directory.

### Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_database.py

# Run with coverage report
pytest --cov=db --cov=models --cov-report=term-missing

# Run specific test class or function
pytest tests/test_database.py::TestGetDb
```

### Test Structure

- `tests/conftest.py` - Shared pytest fixtures and configuration
- `tests/test_database.py` - Tests for database connection management
- `tests/test_health.py` - Tests for database health check functions
- `tests/test_models.py` - Tests for base model classes

### Test Coverage

The test suite includes:
- Database session management (`get_db`, `get_db_context`)
- Database initialization and cleanup (`init_db`, `close_db`)
- Health check functions (`check_database_health`, `is_database_connected`)
- Base model functionality (`BaseModel` class and methods)

