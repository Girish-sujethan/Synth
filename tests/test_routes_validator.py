"""Unit tests for validator routes."""

import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI

# Import routes
try:
    from api.routes.validator.router import router as validator_router
    HAS_ROUTES = True
except ImportError:
    HAS_ROUTES = False
    validator_router = None


@pytest.fixture
def app():
    """Create a test FastAPI app."""
    if not HAS_ROUTES:
        pytest.skip("Routes not available")
    app = FastAPI()
    app.include_router(validator_router)
    return app


@pytest.fixture
def client(app):
    """Create a test client."""
    return TestClient(app)


class TestValidatorRoutes:
    """Tests for validator routes."""
    
    @pytest.mark.skipif(not HAS_ROUTES, reason="Routes not available")
    def test_validator_info(self, client):
        """Test validator info endpoint."""
        response = client.get("/validator/")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["module"] == "validator"
        assert data["data"]["status"] == "ready"
    
    @pytest.mark.skipif(not HAS_ROUTES, reason="Routes not available")
    def test_validator_status(self, client):
        """Test validator status endpoint."""
        response = client.get("/validator/status")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["module"] == "validator"
        assert data["data"]["status"] == "operational"
        assert "features" in data["data"]

