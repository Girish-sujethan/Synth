"""Unit tests for database connection management and session factory."""

import pytest
from unittest.mock import Mock, MagicMock, patch, call
from sqlalchemy import create_engine, Engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from contextlib import contextmanager

from db import database


class TestDatabaseEngine:
    """Tests for database engine creation."""
    
    def test_engine_exists(self):
        """Test that engine is created and exists."""
        assert database.engine is not None
        assert isinstance(database.engine, Engine)
    
    def test_engine_has_correct_configuration(self):
        """Test that engine has expected configuration."""
        # Engine should exist and be configured
        assert database.engine is not None
        # Check that engine has pool configuration
        assert hasattr(database.engine.pool, "_pool_size") or hasattr(database.engine.pool, "size")
    
    def test_session_local_exists(self):
        """Test that SessionLocal is created."""
        assert database.SessionLocal is not None
        assert callable(database.SessionLocal)


class TestGetDb:
    """Tests for get_db() generator function."""
    
    def test_get_db_yields_session(self, mock_session_local):
        """Test that get_db yields a database session."""
        with patch("db.database.SessionLocal", mock_session_local):
            gen = database.get_db()
            session = next(gen)
            assert session is not None
            assert hasattr(session, "close")
    
    def test_get_db_closes_session_on_success(self, mock_db_session, mock_session_local):
        """Test that get_db closes session after successful use."""
        with patch("db.database.SessionLocal", mock_session_local):
            gen = database.get_db()
            session = next(gen)
            try:
                # Simulate successful use
                pass
            finally:
                gen.close()
            
            mock_db_session.close.assert_called_once()
    
    def test_get_db_rolls_back_on_exception(self, mock_db_session, mock_session_local):
        """Test that get_db rolls back on exception."""
        with patch("db.database.SessionLocal", mock_session_local):
            gen = database.get_db()
            session = next(gen)
            
            # Throw an exception into the generator - this triggers the exception handler
            # in get_db() which should call rollback()
            try:
                gen.throw(SQLAlchemyError("Test error"))
            except SQLAlchemyError:
                # Exception was re-raised as expected
                pass
            
            # Verify rollback was called by the exception handler
            mock_db_session.rollback.assert_called_once()
            # Verify close was called in the finally block
            mock_db_session.close.assert_called_once()


class TestGetDbContext:
    """Tests for get_db_context() context manager."""
    
    def test_get_db_context_yields_session(self, mock_session_local):
        """Test that get_db_context yields a database session."""
        with patch("db.database.SessionLocal", mock_session_local):
            with database.get_db_context() as session:
                assert session is not None
                assert hasattr(session, "commit")
                assert hasattr(session, "close")
    
    def test_get_db_context_commits_on_success(self, mock_db_session, mock_session_local):
        """Test that get_db_context commits on successful exit."""
        with patch("db.database.SessionLocal", mock_session_local):
            with database.get_db_context() as session:
                pass  # Successful exit
            
            mock_db_session.commit.assert_called_once()
            mock_db_session.close.assert_called_once()
    
    def test_get_db_context_rolls_back_on_exception(self, mock_db_session, mock_session_local):
        """Test that get_db_context rolls back on exception."""
        with patch("db.database.SessionLocal", mock_session_local):
            try:
                with database.get_db_context() as session:
                    raise ValueError("Test error")
            except ValueError:
                pass
            
            mock_db_session.rollback.assert_called_once()
            mock_db_session.close.assert_called_once()
            mock_db_session.commit.assert_not_called()
    
    def test_get_db_context_closes_on_exception(self, mock_db_session, mock_session_local):
        """Test that get_db_context always closes session even on exception."""
        with patch("db.database.SessionLocal", mock_session_local):
            try:
                with database.get_db_context() as session:
                    raise RuntimeError("Test error")
            except RuntimeError:
                pass
            
            mock_db_session.close.assert_called_once()


class TestInitDb:
    """Tests for init_db() function."""
    
    @patch("db.database.SQLModel.metadata.create_all")
    @patch("db.database.engine")
    def test_init_db_creates_tables(self, mock_engine, mock_create_all):
        """Test that init_db creates all tables."""
        database.init_db()
        mock_create_all.assert_called_once_with(mock_engine)


class TestCloseDb:
    """Tests for close_db() function."""
    
    @patch("db.database.engine")
    def test_close_db_disposes_engine(self, mock_engine):
        """Test that close_db disposes the engine."""
        database.close_db()
        mock_engine.dispose.assert_called_once()


class TestDatabaseIntegration:
    """Integration tests for database functions."""
    
    def test_get_db_generator_usage(self, test_session_factory):
        """Test that get_db can be used as a generator."""
        with patch("db.database.SessionLocal", test_session_factory):
            gen = database.get_db()
            session = next(gen)
            assert isinstance(session, Session)
            gen.close()
    
    def test_get_db_context_usage(self, test_session_factory):
        """Test that get_db_context can be used as context manager."""
        from sqlalchemy import text
        
        with patch("db.database.SessionLocal", test_session_factory):
            with database.get_db_context() as session:
                assert isinstance(session, Session)
                # Session should be usable
                result = session.execute(text("SELECT 1"))
                assert result is not None

