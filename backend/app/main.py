"""Main FastAPI application."""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.app.api.routes import health
from backend.app.core.config import settings
from backend.app.core.exceptions import APIException
from backend.app.core.middleware import create_error_response
from backend.app.schemas.errors import ErrorResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager."""
    # Startup
    from backend.app.db.client import DatabaseClient

    # Initialize database connection pool
    await DatabaseClient.get_pool()

    yield

    # Shutdown
    # Close database connection pool
    await DatabaseClient.close_pool()


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="FastAPI backend application with Supabase authentication",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handlers
@app.exception_handler(APIException)
async def api_exception_handler(request: Request, exc: APIException) -> JSONResponse:
    """Handle custom API exceptions."""
    error_response, status_code = create_error_response(exc)
    return JSONResponse(
        status_code=status_code,
        content=error_response.model_dump(),
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle general exceptions."""
    error_response, status_code = create_error_response(exc)
    return JSONResponse(
        status_code=status_code,
        content=error_response.model_dump(),
    )


# Include routers
app.include_router(health.router)
from backend.app.api.routes import board, columns, tasks

app.include_router(tasks.router)
app.include_router(board.router)
app.include_router(columns.router)


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint."""
    return {
        "message": f"Welcome to {settings.app_name}",
        "version": settings.app_version,
        "docs": "/docs",
    }
