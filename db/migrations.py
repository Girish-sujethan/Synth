"""Utility functions for running migrations programmatically."""

from typing import Optional, Dict, Any
from alembic import command
from alembic.config import Config
from alembic.runtime.migration import MigrationContext
from sqlalchemy import inspect
from pathlib import Path

from db.database import engine
from core.logging import get_logger

logger = get_logger(__name__)


def get_alembic_config() -> Config:
    """
    Get Alembic configuration object.
    
    Returns:
        Alembic Config instance
    """
    alembic_cfg = Config(str(Path(__file__).parent.parent / "alembic.ini"))
    return alembic_cfg


def get_current_revision() -> Optional[str]:
    """
    Get the current database revision.
    
    Returns:
        Current revision string, or None if no migrations have been run
    """
    try:
        with engine.connect() as connection:
            context = MigrationContext.configure(connection)
            current_rev = context.get_current_revision()
            return current_rev
    except Exception as e:
        logger.warning(f"Failed to get current revision: {str(e)}")
        return None


def get_head_revision() -> str:
    """
    Get the head (latest) revision from migration files.
    
    Returns:
        Head revision string
    """
    alembic_cfg = get_alembic_config()
    script = command.ScriptDirectory.from_config(alembic_cfg)
    return script.get_current_head()


def is_database_up_to_date() -> bool:
    """
    Check if database is up to date with latest migrations.
    
    Returns:
        True if database is up to date, False otherwise
    """
    current = get_current_revision()
    head = get_head_revision()
    
    if current is None:
        return False
    
    return current == head


def get_migration_status() -> Dict[str, Any]:
    """
    Get migration status information.
    
    Returns:
        Dictionary with migration status details
    """
    current = get_current_revision()
    head = get_head_revision()
    is_up_to_date = current == head if current else False
    
    return {
        "current_revision": current,
        "head_revision": head,
        "is_up_to_date": is_up_to_date,
        "needs_migration": not is_up_to_date,
    }


def upgrade_database(revision: str = "head") -> None:
    """
    Upgrade database to specified revision.
    
    Args:
        revision: Target revision (default: "head" for latest)
    """
    alembic_cfg = get_alembic_config()
    logger.info(f"Upgrading database to revision: {revision}")
    command.upgrade(alembic_cfg, revision)


def downgrade_database(revision: str) -> None:
    """
    Downgrade database to specified revision.
    
    Args:
        revision: Target revision
    """
    alembic_cfg = get_alembic_config()
    logger.info(f"Downgrading database to revision: {revision}")
    command.downgrade(alembic_cfg, revision)


def create_migration(message: str, autogenerate: bool = True) -> str:
    """
    Create a new migration revision.
    
    Args:
        message: Description of the migration
        autogenerate: Whether to autogenerate from model changes
        
    Returns:
        Revision ID of the created migration
    """
    alembic_cfg = get_alembic_config()
    logger.info(f"Creating migration: {message}")
    
    if autogenerate:
        command.revision(
            alembic_cfg,
            message=message,
            autogenerate=True,
        )
    else:
        command.revision(
            alembic_cfg,
            message=message,
        )
    
    # Get the latest revision
    script = command.ScriptDirectory.from_config(alembic_cfg)
    return script.get_current_head()


def stamp_database(revision: str) -> None:
    """
    Stamp database with a revision without running migrations.
    
    Args:
        revision: Revision to stamp
    """
    alembic_cfg = get_alembic_config()
    logger.info(f"Stamping database with revision: {revision}")
    command.stamp(alembic_cfg, revision)

