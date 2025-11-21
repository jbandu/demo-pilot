#!/bin/bash

set -e

echo "🔄 Resetting Demo Environment..."
echo ""

# Check if we're in the project root
if [ ! -f "run_server.py" ]; then
    echo "❌ Error: Must run from project root directory"
    exit 1
fi

# Confirm with user
read -p "This will reset the database and clear recordings. Continue? (y/N) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Cancelled"
    exit 1
fi

# Load environment
if [ -f ".env" ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Reset database
echo "🗄️  Resetting database..."

# Activate virtual environment if it exists
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
fi

# Check if database script exists
if [ -f "scripts/init_database.py" ]; then
    python scripts/init_database.py --reset
    echo "✓ Database reset using init_database.py"
else
    # Fallback: use inline Python script
    python << 'EOF'
import asyncio
import os
import sys

# Add project root to path
sys.path.insert(0, os.getcwd())

async def reset():
    try:
        from backend.database.models import Base
        from sqlalchemy.ext.asyncio import create_async_engine

        db_url = os.getenv('DATABASE_URL', 'sqlite+aiosqlite:///./demo_copilot.db')
        engine = create_async_engine(db_url)

        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)

        await engine.dispose()
        print("✓ Database reset complete")

    except Exception as e:
        print(f"⚠ Database reset failed: {e}")
        print("Note: This is normal if database doesn't exist yet")

asyncio.run(reset())
EOF
fi

# Clear recordings
echo ""
echo "🎥 Clearing recordings..."
if [ -d "recordings" ]; then
    rm -rf recordings/*
    echo "✓ Recordings cleared"
else
    mkdir -p recordings
    echo "✓ Recordings directory created"
fi

# Clear logs
echo ""
echo "📝 Clearing logs..."
if [ -d "logs" ]; then
    rm -rf logs/*.log
    rm -rf logs/*.pid
    echo "✓ Logs cleared"
else
    mkdir -p logs
    echo "✓ Logs directory created"
fi

# Clear Python cache
echo ""
echo "🧹 Clearing Python cache..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true
echo "✓ Python cache cleared"

# Clear frontend cache (if exists)
if [ -d "frontend" ]; then
    echo ""
    echo "🧹 Clearing frontend cache..."
    cd frontend
    rm -rf .next node_modules/.cache 2>/dev/null || true
    cd ..
    echo "✓ Frontend cache cleared"
fi

echo ""
echo "=========================================="
echo "✅ Demo Environment Reset Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Start the servers: ./scripts/start-dev.sh"
echo "2. Or run backend only: python run_server.py"
echo ""
