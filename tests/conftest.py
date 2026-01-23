"""Pytest configuration with database fixtures and test client setup."""

import pytest
from typing import Generator
from unittest.mock import Mock, MagicMock, patch
from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import Session, sessionmaker
from sqlmodel import SQLModel

# Try to import main, but make it optional for tests that don't need it
try:
    from main import app
    from db.database import get_db
    from fastapi.testclient import TestClient
    HAS_MAIN = True
except ImportError:
    app = None
    get_db = None
    TestClient = None
    HAS_MAIN = False

from config import settings
from models.base import BaseModel

# Import all models so SQLModel metadata is complete
try:
    from models.user import User
except ImportError:
    User = None


# Test database URL (use a separate test database or in-memory)
try:
    TEST_DATABASE_URL = str(settings.effective_database_url).replace(
        "/postgres", "/test_postgres"
    ) if not settings.is_development else "sqlite:///./test.db"
except Exception:
    TEST_DATABASE_URL = "sqlite:///:memory:"

# Create test engine
test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in TEST_DATABASE_URL else {},
    echo=False,
)

# Create test session factory
TestSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine,
)


@pytest.fixture(scope="function")
def db_session() -> Generator[Session, None, None]:
    """
    Create a test database session.
    
    Yields:
        Test database session
    """
    # Create tables
    SQLModel.metadata.create_all(test_engine)
    
    # Create session
    session = TestSessionLocal()
    try:
        yield session
    finally:
        session.close()
        # Drop tables after test
        SQLModel.metadata.drop_all(test_engine)


@pytest.fixture
def test_session():
    """Mock database session for testing."""
    session = MagicMock(spec=Session)
    session.get = MagicMock()
    session.query = MagicMock()
    session.add = MagicMock()
    session.commit = MagicMock()
    session.refresh = MagicMock()
    session.delete = MagicMock()
    session.close = MagicMock()
    session.execute = MagicMock()
    session.rollback = MagicMock()
    session.__enter__ = MagicMock(return_value=session)
    session.__exit__ = MagicMock(return_value=False)
    return session


@pytest.fixture
def mock_db_session():
    """Mock database session for testing (alias for test_session)."""
    session = MagicMock(spec=Session)
    session.get = MagicMock()
    session.query = MagicMock()
    session.add = MagicMock()
    session.commit = MagicMock()
    session.refresh = MagicMock()
    session.delete = MagicMock()
    session.close = MagicMock()
    session.execute = MagicMock()
    session.rollback = MagicMock()
    session.__enter__ = MagicMock(return_value=session)
    session.__exit__ = MagicMock(return_value=False)
    return session


@pytest.fixture
def mock_session_local(mock_db_session):
    """Mock SessionLocal that returns a mock session."""
    def session_factory():
        return mock_db_session
    
    session_factory.return_value = mock_db_session
    return session_factory


@pytest.fixture
def test_session_factory():
    """Create a session factory for testing."""
    return TestSessionLocal


@pytest.fixture(scope="function")
def client(db_session: Session):
    """
    Create a test client with database dependency override.
    
    Args:
        db_session: Test database session
        
    Yields:
        FastAPI test client
    """
    if not HAS_MAIN or app is None or TestClient is None:
        pytest.skip("Main app not available")
    
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def test_user(db_session: Session):
    """
    Create a test user.
    
    Args:
        db_session: Test database session
        
    Returns:
        Test user instance
    """
    if User is None:
        pytest.skip("User model not available")
    
    user = User(
        supabase_user_id="test_supabase_id_123",
        email="test@example.com",
        full_name="Test User",
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user
