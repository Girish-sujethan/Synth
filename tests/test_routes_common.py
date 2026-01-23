"""Unit tests for common routes."""

import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from fastapi import FastAPI

# Import routes
try:
    from api.routes.common.router import router as common_router
    HAS_ROUTES = True
except ImportError:
    HAS_ROUTES = False
    common_router = None


@pytest.fixture
def app():
    """Create a test FastAPI app."""
    if not HAS_ROUTES:
        pytest.skip("Routes not available")
    app = FastAPI()
    app.include_router(common_router)
    return app


@pytest.fixture
def client(app):
    """Create a test client."""
    return TestClient(app)


class TestCommonRoutes:
    """Tests for common routes."""
    
    @pytest.mark.skipif(not HAS_ROUTES, reason="Routes not available")
    @patch("api.routes.common.router.check_database_health")
    @patch("api.routes.common.router.get_migration_status")
    def test_health_check(self, mock_migration, mock_health, client):
        """Test health check endpoint."""
        mock_health.return_value = {
            "status": "healthy",
            "connected": True,
            "response_time_ms": 10.5
        }
        mock_migration.return_value = {
            "current_revision": "abc123",
            "head_revision": "abc123",
            "is_up_to_date": True
        }
        
        response = client.get("/common/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["status"] == "healthy"
    
    @pytest.mark.skipif(not HAS_ROUTES, reason="Routes not available")
    def test_version_endpoint(self, client):
        """Test version endpoint."""
        response = client.get("/common/version")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["version"] == "1.0.0"
        assert data["data"]["api_version"] == "v1"
    
    @pytest.mark.skipif(not HAS_ROUTES, reason="Routes not available")
    @patch("api.routes.common.router.check_database_health")
    @patch("api.routes.common.router.get_migration_status")
    def test_status_endpoint(self, mock_migration, mock_health, client):
        """Test status endpoint."""
        mock_health.return_value = {
            "status": "healthy",
            "connected": True,
            "response_time_ms": 10.5
        }
        mock_migration.return_value = {
            "current_revision": "abc123",
            "head_revision": "abc123",
            "is_up_to_date": True
        }
        
        response = client.get("/common/status")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "system" in data["data"]
        assert "database" in data["data"]
    
    @pytest.mark.skipif(not HAS_ROUTES, reason="Routes not available")
    def test_info_endpoint(self, client):
        """Test info endpoint."""
        response = client.get("/common/info")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "modules" in data["data"]
        assert "features" in data["data"]

