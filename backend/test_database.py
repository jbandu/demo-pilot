#!/usr/bin/env python3
"""
Database Connection Test Script
Tests the database connection and provides helpful diagnostics
"""
import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
backend_dir = Path(__file__).parent
env_path = backend_dir / ".env"
if env_path.exists():
    load_dotenv(env_path)
    print(f"✓ Loaded environment variables from {env_path}\n")
else:
    print(f"⚠ No .env file found at {env_path}\n")

# Get database URL
DATABASE_URL = os.getenv("DATABASE_URL")
SKIP_DATABASE = os.getenv("SKIP_DATABASE", "false").lower() in ("true", "1", "yes")

print("=" * 60)
print("DATABASE CONNECTION TEST")
print("=" * 60)
print()

# Check if database is skipped
if SKIP_DATABASE:
    print("❌ SKIP_DATABASE is set to true")
    print("   Change SKIP_DATABASE=false in your .env file to enable database")
    sys.exit(1)

# Check if DATABASE_URL is set
if not DATABASE_URL:
    print("❌ DATABASE_URL not set in environment")
    print("   Add DATABASE_URL to your .env file")
    sys.exit(1)

print(f"DATABASE_URL: {DATABASE_URL}")
print()

# Check URL format
if DATABASE_URL.startswith("postgresql://"):
    print("⚠ WARNING: Using 'postgresql://' protocol")
    print("   For async connections, you should use 'postgresql+asyncpg://'")
    print()
    print("   Current URL:")
    print(f"   {DATABASE_URL}")
    print()
    print("   Suggested fix:")
    suggested_url = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
    # Remove channel_binding if present
    if "channel_binding" in suggested_url:
        import re
        suggested_url = re.sub(r'[&?]channel_binding=[^&]*', '', suggested_url)
    print(f"   {suggested_url}")
    print()

# Test connection
print("Testing database connection...")
print()

try:
    from sqlalchemy.ext.asyncio import create_async_engine
    from backend.database.models import Base

    # Create engine
    engine = create_async_engine(DATABASE_URL, echo=False)

    async def test_connection():
        try:
            async with engine.begin() as conn:
                # Try to create tables
                await conn.run_sync(Base.metadata.create_all)
                print("✓ Successfully connected to database!")
                print("✓ Database tables created/verified")

                # Test a simple query
                result = await conn.execute("SELECT 1 as test")
                row = result.first()
                if row:
                    print(f"✓ Test query successful: {row[0]}")

            await engine.dispose()
            return True

        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            print()
            print("Common issues:")
            print("  1. Wrong protocol - use 'postgresql+asyncpg://' not 'postgresql://'")
            print("  2. Remove 'channel_binding' parameter if present")
            print("  3. Check if your database is accessible from your network")
            print("  4. Verify credentials are correct")
            print()
            await engine.dispose()
            return False

    # Run async test
    success = asyncio.run(test_connection())

    print()
    print("=" * 60)
    if success:
        print("✓ DATABASE TEST PASSED")
        print()
        print("You can now set SKIP_DATABASE=false in your .env file")
    else:
        print("❌ DATABASE TEST FAILED")
        print()
        print("Fix the issues above and try again")
    print("=" * 60)

    sys.exit(0 if success else 1)

except ImportError as e:
    print(f"❌ Missing required package: {e}")
    print()
    print("Install required packages:")
    print("  pip install sqlalchemy asyncpg")
    sys.exit(1)
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
