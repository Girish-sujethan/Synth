"""API routes package for organizing endpoints by domain modules."""

from api.routes.common import router as common_router
from api.routes.graph import router as graph_router
from api.routes.validator import router as validator_router
from api.routes.tasks import router as tasks_router
from api.routes import health as health_routes

__all__ = [
    "common_router",
    "graph_router",
    "validator_router",
    "tasks_router",
    "health_routes",
]

