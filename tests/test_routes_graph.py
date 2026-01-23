"""Unit tests for graph routes."""

import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI

# Import routes
try:
    from api.routes.graph.router import router as graph_router
    HAS_ROUTES = True
except ImportError:
    HAS_ROUTES = False
    graph_router = None


@pytest.fixture
def app():
    """Create a test FastAPI app."""
    if not HAS_ROUTES:
        pytest.skip("Routes not available")
    app = FastAPI()
    app.include_router(graph_router)
    return app


@pytest.fixture
def client(app):
    """Create a test client."""
    return TestClient(app)


class TestGraphRoutes:
    """Tests for graph routes."""
    
    @pytest.mark.skipif(not HAS_ROUTES, reason="Routes not available")
    def test_graph_info(self, client):
        """Test graph info endpoint."""
        response = client.get("/graph/")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["module"] == "graph"
        assert data["data"]["status"] == "ready"
    
    @pytest.mark.skipif(not HAS_ROUTES, reason="Routes not available")
    def test_graph_status(self, client):
        """Test graph status endpoint."""
        response = client.get("/graph/status")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["module"] == "graph"
        assert data["data"]["status"] == "operational"
        assert "features" in data["data"]

