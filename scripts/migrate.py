#!/usr/bin/env python3
"""CLI script for running database migrations."""

import sys
import argparse
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from db.migrations import (
    upgrade_database,
    downgrade_database,
    create_migration,
    get_migration_status,
    get_current_revision,
    get_head_revision,
    is_database_up_to_date,
    stamp_database,
)
from core.logging import setup_logging, get_logger

setup_logging()
logger = get_logger(__name__)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Database migration management tool"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Migration command")
    
    # Upgrade command
    upgrade_parser = subparsers.add_parser("upgrade", help="Upgrade database to a revision")
    upgrade_parser.add_argument(
        "revision",
        nargs="?",
        default="head",
        help="Target revision (default: head)"
    )
    
    # Downgrade command
    downgrade_parser = subparsers.add_parser("downgrade", help="Downgrade database to a revision")
    downgrade_parser.add_argument(
        "revision",
        help="Target revision"
    )
    
    # Create migration command
    create_parser = subparsers.add_parser("create", help="Create a new migration")
    create_parser.add_argument(
        "message",
        help="Migration message/description"
    )
    create_parser.add_argument(
        "--no-autogenerate",
        action="store_true",
        help="Create empty migration without autogenerate"
    )
    
    # Status command
    status_parser = subparsers.add_parser("status", help="Show migration status")
    
    # Stamp command
    stamp_parser = subparsers.add_parser("stamp", help="Stamp database with a revision")
    stamp_parser.add_argument(
        "revision",
        help="Revision to stamp"
    )
    
    # History command
    history_parser = subparsers.add_parser("history", help="Show migration history")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    try:
        if args.command == "upgrade":
            logger.info(f"Upgrading database to: {args.revision}")
            upgrade_database(args.revision)
            logger.info("Upgrade completed successfully")
            
        elif args.command == "downgrade":
            logger.warning(f"Downgrading database to: {args.revision}")
            confirm = input("Are you sure you want to downgrade? (yes/no): ")
            if confirm.lower() != "yes":
                logger.info("Downgrade cancelled")
                sys.exit(0)
            downgrade_database(args.revision)
            logger.info("Downgrade completed successfully")
            
        elif args.command == "create":
            autogenerate = not args.no_autogenerate
            revision = create_migration(args.message, autogenerate=autogenerate)
            logger.info(f"Migration created: {revision}")
            
        elif args.command == "status":
            status = get_migration_status()
            current = get_current_revision()
            head = get_head_revision()
            
            print("\nMigration Status:")
            print(f"  Current Revision: {current or 'None (no migrations applied)'}")
            print(f"  Head Revision:    {head}")
            print(f"  Up to Date:       {status['is_up_to_date']}")
            
            if not status['is_up_to_date']:
                print("\n⚠️  Database is not up to date. Run 'migrate upgrade' to apply migrations.")
            else:
                print("\n✓ Database is up to date.")
                
        elif args.command == "stamp":
            logger.info(f"Stamping database with: {args.revision}")
            stamp_database(args.revision)
            logger.info("Stamp completed successfully")
            
        elif args.command == "history":
            from alembic.config import Config
            from alembic import command
            from db.migrations import get_alembic_config
            
            alembic_cfg = get_alembic_config()
            command.history(alembic_cfg)
            
    except Exception as e:
        logger.error(f"Migration command failed: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

