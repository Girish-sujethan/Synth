"""Test script to verify Supabase database connection."""

import os
import sys
from pathlib import Path


def check_env_file():
    """Check if .env file exists and has required variables."""
    env_path = Path(".env")
    if not env_path.exists():
        print("✗ .env file not found!")
        print("\nPlease create a .env file with the following variables:")
        print("  SUPABASE_URL=https://your-project.supabase.co")
        print("  SUPABASE_DB_URL=postgresql://postgres:password@db.project-ref.supabase.co:5432/postgres")
        return False
    
    # Check for required variables
    from dotenv import load_dotenv
    load_dotenv()
    
    required_vars = ["SUPABASE_URL", "SUPABASE_DB_URL"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"✗ Missing required environment variables: {', '.join(missing_vars)}")
        print("\nPlease add these to your .env file:")
        for var in missing_vars:
            if var == "SUPABASE_URL":
                print(f"  {var}=https://your-project.supabase.co")
            elif var == "SUPABASE_DB_URL":
                print(f"  {var}=postgresql://postgres:password@db.project-ref.supabase.co:5432/postgres")
        return False
    
    return True


def main():
    """Test database connection and display results."""
    print("=" * 60)
    print("Testing Supabase Database Connection")
    print("=" * 60)
    print()
    
    # Check environment configuration first
    if not check_env_file():
        sys.exit(1)
    
    print("✓ Environment configuration check passed")
    print()
    
    try:
        from db.health import check_database_health, is_database_connected
        from config import settings
    except Exception as e:
        print(f"✗ Error loading configuration: {e}")
        print("\nPlease check your .env file configuration.")
        sys.exit(1)
    
    # Display configuration (without sensitive data)
    print("Configuration:")
    print(f"  Environment: {settings.environment}")
    print(f"  Supabase URL: {settings.supabase_url}")
    db_url_str = str(settings.effective_database_url)
    if "@" in db_url_str:
        print(f"  Database URL: {db_url_str.split('@')[0]}@***")  # Hide password
    else:
        print(f"  Database URL: {db_url_str}")
    print()
    
    # Quick connection check
    print("Quick Connection Test:")
    if is_database_connected():
        print("  ✓ Database is connected")
    else:
        print("  ✗ Database connection failed")
        print()
        print("Please check:")
        print("  1. Your .env file has correct Supabase credentials")
        print("  2. Your Supabase project is active")
        print("  3. Your network connection is working")
        sys.exit(1)
    
    print()
    
    # Detailed health check
    print("Detailed Health Check:")
    health = check_database_health()
    
    if health["status"] == "healthy":
        print(f"  ✓ Status: {health['status']}")
        print(f"  ✓ Connected: {health['connected']}")
        print(f"  ✓ Response Time: {health['response_time_ms']} ms")
        if health["database_version"]:
            # Show just the version number
            version = health["database_version"].split(",")[0] if "," in health["database_version"] else health["database_version"]
            print(f"  ✓ Database Version: {version}")
        print()
        print("=" * 60)
        print("✓ Connection test PASSED")
        print("=" * 60)
    else:
        print(f"  ✗ Status: {health['status']}")
        print(f"  ✗ Error: {health['error']}")
        print()
        print("=" * 60)
        print("✗ Connection test FAILED")
        print("=" * 60)
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n✗ Error during connection test: {e}")
        import traceback
        traceback.print_exc()
        print("\nPlease ensure:")
        print("  1. Your .env file exists and is properly configured")
        print("  2. All required environment variables are set")
        print("  3. Your Supabase project credentials are correct")
        sys.exit(1)

