"""Unit tests for database health check functions."""

import pytest
import time
from unittest.mock import Mock, MagicMock, patch, call
from sqlalchemy.exc import SQLAlchemyError, OperationalError
from sqlalchemy import text

from db import health


class TestCheckDatabaseHealth:
    """Tests for check_database_health() function."""
    
    def test_check_database_health_success(self, mock_db_session):
        """Test successful database health check."""
        # Mock the database response - first call for SELECT 1, second for version
        mock_version_result = MagicMock()
        mock_version_result.fetchone.return_value = ("PostgreSQL 15.0",)
        
        def execute_side_effect(query):
            if "version()" in str(query):
                return mock_version_result
            return MagicMock()
        
        mock_db_session.execute.side_effect = execute_side_effect
        
        with patch("db.health.get_db_context") as mock_context:
            mock_context.return_value.__enter__.return_value = mock_db_session
            mock_context.return_value.__exit__.return_value = False
            
            result = health.check_database_health()
            
            assert result["status"] == "healthy"
            assert result["connected"] is True
            assert result["response_time_ms"] is not None
            assert isinstance(result["response_time_ms"], float)
            assert result["error"] is None
            assert result["database_version"] == "PostgreSQL 15.0"
            assert mock_db_session.execute.call_count >= 2  # SELECT 1 and SELECT version()
            mock_db_session.commit.assert_called_once()
    
    def test_check_database_health_without_version(self, mock_db_session):
        """Test health check when version query returns None."""
        # Mock the database response - first call for SELECT 1, second for version
        mock_version_result = MagicMock()
        mock_version_result.fetchone.return_value = None
        
        def execute_side_effect(query):
            if "version()" in str(query):
                return mock_version_result
            return MagicMock()
        
        mock_db_session.execute.side_effect = execute_side_effect
        
        with patch("db.health.get_db_context") as mock_context:
            mock_context.return_value.__enter__.return_value = mock_db_session
            mock_context.return_value.__exit__.return_value = False
            
            result = health.check_database_health()
            
            assert result["status"] == "healthy"
            assert result["connected"] is True
            assert result["database_version"] is None
    
    def test_check_database_health_sqlalchemy_error(self, mock_db_session):
        """Test health check when SQLAlchemyError occurs."""
        mock_db_session.execute.side_effect = SQLAlchemyError("Connection failed", None, None)
        
        with patch("db.health.get_db_context") as mock_context:
            mock_context.return_value.__enter__.return_value = mock_db_session
            mock_context.return_value.__exit__.return_value = False
            
            result = health.check_database_health()
            
            assert result["status"] == "unhealthy"
            assert result["connected"] is False
            assert result["response_time_ms"] is None
            assert "Database connection error" in result["error"]
            assert result["database_version"] is None
    
    def test_check_database_health_operational_error(self, mock_db_session):
        """Test health check when OperationalError occurs."""
        # OperationalError is a subclass of SQLAlchemyError, so it will be caught
        mock_db_session.execute.side_effect = OperationalError(
            "Connection refused", None, None, None
        )
        
        with patch("db.health.get_db_context") as mock_context:
            mock_context.return_value.__enter__.return_value = mock_db_session
            mock_context.return_value.__exit__.return_value = False
            
            result = health.check_database_health()
            
            assert result["status"] == "unhealthy"
            assert result["connected"] is False
            assert "Database connection error" in result["error"]
    
    def test_check_database_health_unexpected_error(self, mock_db_session):
        """Test health check when unexpected error occurs."""
        mock_db_session.execute.side_effect = ValueError("Unexpected error")
        
        with patch("db.health.get_db_context") as mock_context:
            mock_context.return_value.__enter__.return_value = mock_db_session
            mock_context.return_value.__exit__.return_value = False
            
            result = health.check_database_health()
            
            assert result["status"] == "unhealthy"
            assert result["connected"] is False
            assert "Unexpected error" in result["error"]
    
    @patch("time.time")
    def test_check_database_health_response_time(self, mock_time, mock_db_session):
        """Test that response time is calculated correctly."""
        mock_result = MagicMock()
        mock_result.fetchone.return_value = None
        mock_db_session.execute.return_value = mock_result
        
        # Mock time to simulate 0.1 second response time
        mock_time.side_effect = [0.0, 0.1]
        
        with patch("db.health.get_db_context") as mock_context:
            mock_context.return_value.__enter__.return_value = mock_db_session
            mock_context.return_value.__exit__.return_value = False
            
            result = health.check_database_health()
            
            assert result["response_time_ms"] == 100.0  # 0.1 seconds = 100ms
    
    def test_check_database_health_result_structure(self, mock_db_session):
        """Test that health check returns expected structure."""
        mock_result = MagicMock()
        mock_result.fetchone.return_value = ("PostgreSQL 14.5",)
        mock_db_session.execute.return_value = mock_result
        
        with patch("db.health.get_db_context") as mock_context:
            mock_context.return_value.__enter__.return_value = mock_db_session
            mock_context.return_value.__exit__.return_value = False
            
            result = health.check_database_health()
            
            # Check all expected keys are present
            assert "status" in result
            assert "connected" in result
            assert "response_time_ms" in result
            assert "error" in result
            assert "database_version" in result
            
            # Check types
            assert isinstance(result["status"], str)
            assert isinstance(result["connected"], bool)
            assert isinstance(result["response_time_ms"], (float, type(None)))
            assert isinstance(result["error"], (str, type(None)))
            assert isinstance(result["database_version"], (str, type(None)))


class TestIsDatabaseConnected:
    """Tests for is_database_connected() function."""
    
    def test_is_database_connected_success(self, mock_db_session):
        """Test successful database connection check."""
        mock_db_session.execute.return_value = MagicMock()
        
        with patch("db.health.get_db_context") as mock_context:
            mock_context.return_value.__enter__.return_value = mock_db_session
            mock_context.return_value.__exit__.return_value = False
            
            result = health.is_database_connected()
            
            assert result is True
            mock_db_session.execute.assert_called_once()
            # Verify it was called with text("SELECT 1")
            call_args = mock_db_session.execute.call_args[0][0]
            assert "SELECT 1" in str(call_args)
    
    def test_is_database_connected_failure(self, mock_db_session):
        """Test database connection check when connection fails."""
        mock_db_session.execute.side_effect = SQLAlchemyError("Connection failed")
        
        with patch("db.health.get_db_context") as mock_context:
            mock_context.return_value.__enter__.return_value = mock_db_session
            mock_context.return_value.__exit__.return_value = False
            
            result = health.is_database_connected()
            
            assert result is False
    
    def test_is_database_connected_operational_error(self, mock_db_session):
        """Test database connection check when OperationalError occurs."""
        mock_db_session.execute.side_effect = OperationalError(
            "Connection refused", None, None, None
        )
        
        with patch("db.health.get_db_context") as mock_context:
            mock_context.return_value.__enter__.return_value = mock_db_session
            mock_context.return_value.__exit__.return_value = False
            
            result = health.is_database_connected()
            
            assert result is False
    
    def test_is_database_connected_unexpected_error(self, mock_db_session):
        """Test database connection check when unexpected error occurs."""
        mock_db_session.execute.side_effect = ValueError("Unexpected error")
        
        with patch("db.health.get_db_context") as mock_context:
            mock_context.return_value.__enter__.return_value = mock_db_session
            mock_context.return_value.__exit__.return_value = False
            
            result = health.is_database_connected()
            
            assert result is False

