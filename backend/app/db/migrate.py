"""Database migration runner."""

import asyncio
from pathlib import Path

import asyncpg
from backend.app.core.config import settings


async def run_migrations():
    """Run all database migrations."""
    if not settings.database_url:
        raise ValueError("DATABASE_URL not set in environment variables")

    # Read the combined migration file
    migrations_dir = Path(__file__).parent / "migrations"
    migration_file = migrations_dir / "000_initial_schema.sql"

    if not migration_file.exists():
        raise FileNotFoundError(f"Migration file not found: {migration_file}")

    print(f"Reading migration file: {migration_file}")
    sql = migration_file.read_text()

    print("Connecting to database...")
    conn = await asyncpg.connect(settings.database_url)

    try:
        print("Running migration...")
        await conn.execute(sql)
        print("✓ Migration completed successfully!")
    except Exception as e:
        print(f"✗ Migration failed: {e}")
        raise
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(run_migrations())
