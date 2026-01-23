#!/usr/bin/env python3
"""CLI script for creating an admin user directly via Supabase admin API."""

import sys
import getpass
import argparse
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from supabase import create_client, Client
from config import settings
from db.database import get_db
from repositories.user import UserRepository
from core.logging import setup_logging, get_logger

setup_logging()
logger = get_logger(__name__)


def get_supabase_admin_client() -> Client:
    """
    Get Supabase admin client using service role key.
    
    Returns:
        Supabase client with admin privileges
    """
    if not settings.supabase_url:
        raise ValueError("SUPABASE_URL is not configured")
    
    # Check for service role key in environment
    # Service role key should be set as SUPABASE_SERVICE_ROLE_KEY
    import os
    service_role_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or settings.supabase_key
    
    if not service_role_key:
        raise ValueError(
            "SUPABASE_SERVICE_ROLE_KEY is required for admin operations. "
            "Set it in your .env file or as an environment variable."
        )
    
    # Verify it's a service role key (starts with 'eyJ' and is longer)
    if "service_role" not in service_role_key.lower() and len(service_role_key) < 100:
        logger.warning(
            "Warning: The provided key might not be a service role key. "
            "Service role keys are required for admin operations."
        )
    
    return create_client(settings.supabase_url, service_role_key)


def create_admin_user(
    email: str,
    password: str,
    full_name: str | None = None,
    skip_db: bool = False
) -> dict:
    """
    Create an admin user in Supabase Auth and optionally in the database.
    
    Args:
        email: User email address
        password: User password
        full_name: Optional full name
        skip_db: If True, skip creating user in database
        
    Returns:
        Dictionary with user information
    """
    try:
        # Get Supabase admin client
        supabase = get_supabase_admin_client()
        
        # Create user in Supabase Auth using admin API
        logger.info(f"Creating user in Supabase Auth: {email}")
        
        # Use admin API to create user
        # The admin API allows creating users without email confirmation
        try:
            response = supabase.auth.admin.create_user({
                "email": email,
                "password": password,
                "email_confirm": True,  # Auto-confirm email to bypass confirmation
                "user_metadata": {
                    "full_name": full_name or "",
                } if full_name else {}
            })
            
            # Response structure may vary by Supabase client version
            if hasattr(response, 'user'):
                supabase_user = response.user
            elif isinstance(response, dict) and 'user' in response:
                supabase_user = response['user']
            else:
                # Try to get user from response directly
                supabase_user = response if hasattr(response, 'id') else None
                
            if not supabase_user:
                raise ValueError("Failed to create user in Supabase Auth - invalid response")
                
        except AttributeError:
            # Fallback: try alternative method if admin API structure is different
            logger.warning("Admin API method not available, trying alternative approach...")
            # Some versions use different method names
            if hasattr(supabase.auth, 'admin'):
                # Try direct admin method
                admin = supabase.auth.admin
                if hasattr(admin, 'create_user'):
                    response = admin.create_user({
                        "email": email,
                        "password": password,
                        "email_confirm": True,
                    })
                    supabase_user = response.user if hasattr(response, 'user') else None
                else:
                    raise ValueError("Admin create_user method not found")
            else:
                raise ValueError("Admin API not available - check service role key")
        
        if not supabase_user:
            raise ValueError("Failed to create user in Supabase Auth")
        
        # Get user ID - handle both object and dict responses
        if hasattr(supabase_user, 'id'):
            user_id = supabase_user.id
        elif isinstance(supabase_user, dict) and 'id' in supabase_user:
            user_id = supabase_user['id']
        else:
            raise ValueError("Failed to extract user ID from Supabase response")
        
        logger.info(f"✓ User created in Supabase Auth: {user_id}")
        
        # Create user in our database
        if not skip_db:
            logger.info("Creating user in application database...")
            db = next(get_db())
            try:
                user_repo = UserRepository()
                
                # Check if user already exists
                existing_user = user_repo.get_by_supabase_id(db, user_id)
                if existing_user:
                    logger.warning(f"User already exists in database, updating...")
                    user = user_repo.update(db, existing_user, {
                        "email": email,
                        "full_name": full_name,
                        "is_active": True,
                        "is_superuser": True,
                    })
                else:
                    # Create new user
                    user = user_repo.create(db, {
                        "supabase_user_id": user_id,
                        "email": email,
                        "full_name": full_name,
                        "is_active": True,
                        "is_superuser": True,
                    })
                
                db.commit()
                logger.info(f"✓ User created in database: {user.id}")
                
                return {
                    "success": True,
                    "supabase_user_id": user_id,
                    "email": email,
                    "database_user_id": user.id,
                    "is_superuser": True,
                }
            except Exception as e:
                db.rollback()
                logger.error(f"Failed to create user in database: {str(e)}")
                raise
            finally:
                db.close()
        else:
            logger.info("Skipping database user creation (--skip-db flag set)")
            return {
                "success": True,
                "supabase_user_id": user_id,
                "email": email,
                "database_user_id": None,
                "is_superuser": True,
            }
            
    except Exception as e:
        logger.error(f"Failed to create admin user: {str(e)}", exc_info=True)
        raise


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Create an admin user via Supabase admin API"
    )
    
    parser.add_argument(
        "--email",
        type=str,
        help="Admin user email address"
    )
    
    parser.add_argument(
        "--password",
        type=str,
        help="Admin user password (will prompt if not provided)"
    )
    
    parser.add_argument(
        "--name",
        type=str,
        help="Admin user full name (optional)"
    )
    
    parser.add_argument(
        "--skip-db",
        action="store_true",
        help="Skip creating user in application database"
    )
    
    args = parser.parse_args()
    
    # Get email
    email = args.email
    if not email:
        email = input("Enter admin email: ").strip()
        if not email:
            logger.error("Email is required")
            sys.exit(1)
    
    # Get password
    password = args.password
    if not password:
        password = getpass.getpass("Enter admin password: ")
        if not password:
            logger.error("Password is required")
            sys.exit(1)
        password_confirm = getpass.getpass("Confirm password: ")
        if password != password_confirm:
            logger.error("Passwords do not match")
            sys.exit(1)
    
    # Get full name
    full_name = args.name
    if not full_name:
        full_name_input = input("Enter full name (optional, press Enter to skip): ").strip()
        full_name = full_name_input if full_name_input else None
    
    try:
        result = create_admin_user(
            email=email,
            password=password,
            full_name=full_name,
            skip_db=args.skip_db
        )
        
        print("\n" + "="*60)
        print("✓ Admin user created successfully!")
        print("="*60)
        print(f"Email:           {result['email']}")
        print(f"Supabase User ID: {result['supabase_user_id']}")
        if result.get('database_user_id'):
            print(f"Database User ID: {result['database_user_id']}")
        print(f"Superuser:       {result['is_superuser']}")
        print("="*60)
        print("\nYou can now log in with this account.")
        
    except Exception as e:
        logger.error(f"Failed to create admin user: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()

