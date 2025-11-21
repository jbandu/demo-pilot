#!/bin/bash

set -e

echo "🔄 Resetting Demo Environment..."

# Reset demo databases
echo "Resetting demo data..."
cd backend
source venv/bin/activate

python << EOF
import asyncio
from database.models import Base
from sqlalchemy.ext.asyncio import create_async_engine
import os

async def reset():
    engine = create_async_engine(os.getenv('DATABASE_URL'))
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Database reset")

asyncio.run(reset())
EOF

# Clear recordings
echo "Clearing recordings..."
rm -rf ../recordings/*

# Clear cache
echo "Clearing cache..."
rm -rf __pycache__
rm -rf ../.pytest_cache

cd ..

echo "✅ Demo environment reset complete!"
