"""Unit tests for storage-related dependencies."""

import pytest
from unittest.mock import patch, MagicMock
from api.dependencies import get_storage_service
from services.storage import StorageService


class TestGetStorageService:
    """Tests for get_storage_service dependency."""
    
    @patch("api.dependencies.StorageService")
    def test_get_storage_service_creates_instance(self, mock_storage_service):
        """Test that get_storage_service creates a new instance."""
        mock_instance = MagicMock()
        mock_storage_service.return_value = mock_instance
        
        # Reset global service
        import api.dependencies
        api.dependencies._storage_service = None
        
        service = get_storage_service()
        
        assert service == mock_instance
        mock_storage_service.assert_called_once()
    
    @patch("api.dependencies.StorageService")
    def test_get_storage_service_reuses_instance(self, mock_storage_service):
        """Test that get_storage_service reuses existing instance."""
        mock_instance = MagicMock()
        mock_storage_service.return_value = mock_instance
        
        # Reset global service
        import api.dependencies
        api.dependencies._storage_service = None
        
        service1 = get_storage_service()
        service2 = get_storage_service()
        
        # Should only create service once
        assert mock_storage_service.call_count == 1
        assert service1 is service2

