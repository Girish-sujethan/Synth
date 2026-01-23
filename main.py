"""FastAPI application entry point with core middleware and configuration."""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from config import settings
from core.logging import setup_logging, get_logger
from core.exceptions import (
    AppException,
    app_exception_handler,
    http_exception_handler,
    validation_exception_handler,
    general_exception_handler,
)
from db.health import check_database_health
from api.middleware import AuthenticationMiddleware

# Setup logging
setup_logging(level="DEBUG" if settings.is_development else "INFO")
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    logger.info("Starting application...")
    logger.info(f"Environment: {settings.environment}")
    
    # Check database connection on startup
    health = check_database_health()
    if health["status"] == "healthy":
        logger.info("Database connection verified")
    else:
        logger.warning(f"Database health check failed: {health.get('error')}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down application...")


# Create FastAPI application
app = FastAPI(
    title="Synth API",
    description="FastAPI backend with Supabase authentication",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.is_development else [],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add authentication middleware (optional - can use dependencies instead)
# app.add_middleware(AuthenticationMiddleware, protected_paths=["/api"])

# Register exception handlers
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Import and register exception handlers for Starlette
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.exceptions import RequestValidationError

app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Synth API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    
    Returns:
        Health status with database connectivity information
    """
    db_health = check_database_health()
    
    return {
        "status": "healthy" if db_health["status"] == "healthy" else "degraded",
        "database": db_health,
        "environment": settings.environment,
    }


# Include API routes
from api.routes import (
    common_router,
    graph_router,
    validator_router,
    health_routes,
)
from api.routes import storage as storage_routes

# Include health routes (legacy, kept for backward compatibility)
app.include_router(health_routes.router)

# Include domain module routers with API versioning
api_v1_prefix = "/api/v1"

app.include_router(
    common_router,
    prefix=api_v1_prefix,
    tags=["common"]
)

app.include_router(
    graph_router,
    prefix=api_v1_prefix,
    tags=["graph"]
)

app.include_router(
    validator_router,
    prefix=api_v1_prefix,
    tags=["validator"]
)

app.include_router(
    storage_routes.router,
    prefix=api_v1_prefix,
    tags=["storage"]
)


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.is_development,
        log_level="debug" if settings.is_development else "info",
    )

