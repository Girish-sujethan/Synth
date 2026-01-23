"""Database health check functions for monitoring and verification."""

from typing import Dict, Any
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from db.database import engine, get_db_context


def check_database_health() -> Dict[str, Any]:
    """
    Perform a comprehensive database health check.
    
    Returns:
        Dict containing health status and diagnostic information:
        - status: "healthy" or "unhealthy"
        - connected: bool indicating if connection is successful
        - response_time_ms: float indicating query response time in milliseconds
        - error: str with error message if unhealthy, None otherwise
        - database_version: str with PostgreSQL version if available
        
    Example:
        ```python
        health = check_database_health()
        if health["status"] == "healthy":
            print(f"Database is healthy (response time: {health['response_time_ms']}ms)")
        else:
            print(f"Database is unhealthy: {health['error']}")
        ```
    """
    import time
    
    result: Dict[str, Any] = {
        "status": "unhealthy",
        "connected": False,
        "response_time_ms": None,
        "error": None,
        "database_version": None,
    }
    
    try:
        start_time = time.time()
        
        with get_db_context() as db:
            # Test basic connection with a simple query
            db.execute(text("SELECT 1"))
            
            # Get PostgreSQL version
            version_result = db.execute(text("SELECT version()"))
            version_row = version_result.fetchone()
            if version_row:
                result["database_version"] = version_row[0]
            
            db.commit()
        
        end_time = time.time()
        response_time = (end_time - start_time) * 1000  # Convert to milliseconds
        
        result["status"] = "healthy"
        result["connected"] = True
        result["response_time_ms"] = round(response_time, 2)
        
    except SQLAlchemyError as e:
        result["error"] = f"Database connection error: {str(e)}"
    except Exception as e:
        result["error"] = f"Unexpected error during health check: {str(e)}"
    
    return result


def is_database_connected() -> bool:
    """
    Quick check to verify database connectivity.
    
    Returns:
        bool: True if database is connected and responsive, False otherwise
        
    Example:
        ```python
        if is_database_connected():
            print("Database is connected")
        else:
            print("Database connection failed")
        ```
    """
    try:
        with get_db_context() as db:
            db.execute(text("SELECT 1"))
            return True
    except Exception:
        return False

