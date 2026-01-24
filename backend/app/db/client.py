"""Database client with connection pooling."""

import asyncpg
from typing import Optional

from backend.app.core.config import settings
from backend.app.core.exceptions import DatabaseError as CoreDatabaseError


class DatabaseClient:
    """Database client with connection pooling."""

    _pool: Optional[asyncpg.Pool] = None

    @classmethod
    async def get_pool(cls) -> asyncpg.Pool:
        """
        Get or create database connection pool.

        Returns:
            Database connection pool

        Raises:
            CoreDatabaseError: If connection fails
        """
        if cls._pool is None:
            if not settings.database_url:
                raise CoreDatabaseError("DATABASE_URL not configured")

            try:
                cls._pool = await asyncpg.create_pool(
                    settings.database_url,
                    min_size=2,
                    max_size=10,
                    command_timeout=60,
                )
            except Exception as e:
                raise CoreDatabaseError(f"Failed to create database pool: {str(e)}")

        return cls._pool

    @classmethod
    async def close_pool(cls):
        """Close database connection pool."""
        if cls._pool:
            await cls._pool.close()
            cls._pool = None

    @classmethod
    async def execute(cls, query: str, *args) -> str:
        """
        Execute a query that doesn't return rows.

        Args:
            query: SQL query string
            *args: Query parameters

        Returns:
            Status string

        Raises:
            CoreDatabaseError: If query execution fails
        """
        pool = await cls.get_pool()
        try:
            async with pool.acquire() as conn:
                return await conn.execute(query, *args)
        except Exception as e:
            raise CoreDatabaseError(f"Query execution failed: {str(e)}", details={"query": query})

    @classmethod
    async def fetch_one(cls, query: str, *args) -> Optional[asyncpg.Record]:
        """
        Fetch a single row.

        Args:
            query: SQL query string
            *args: Query parameters

        Returns:
            Record if found, None otherwise

        Raises:
            CoreDatabaseError: If query execution fails
        """
        pool = await cls.get_pool()
        try:
            async with pool.acquire() as conn:
                return await conn.fetchrow(query, *args)
        except Exception as e:
            raise CoreDatabaseError(f"Query execution failed: {str(e)}", details={"query": query})

    @classmethod
    async def fetch_all(cls, query: str, *args) -> list[asyncpg.Record]:
        """
        Fetch all rows.

        Args:
            query: SQL query string
            *args: Query parameters

        Returns:
            List of records

        Raises:
            CoreDatabaseError: If query execution fails
        """
        pool = await cls.get_pool()
        try:
            async with pool.acquire() as conn:
                return await conn.fetch(query, *args)
        except Exception as e:
            raise CoreDatabaseError(f"Query execution failed: {str(e)}", details={"query": query})

    @classmethod
    async def fetch_val(cls, query: str, *args, column: int = 0) -> Optional[any]:
        """
        Fetch a single value.

        Args:
            query: SQL query string
            *args: Query parameters
            column: Column index to fetch

        Returns:
            Value if found, None otherwise

        Raises:
            CoreDatabaseError: If query execution fails
        """
        pool = await cls.get_pool()
        try:
            async with pool.acquire() as conn:
                return await conn.fetchval(query, *args, column=column)
        except Exception as e:
            raise CoreDatabaseError(f"Query execution failed: {str(e)}", details={"query": query})


# Global database client instance
db = DatabaseClient()
