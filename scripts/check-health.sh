#!/bin/bash

echo "🏥 Checking Demo Copilot Health..."
echo ""

# Check backend
echo "Backend API:"
curl -s http://localhost:8000/health | jq . || echo "❌ Backend not responding"
echo ""

# Check frontend
echo "Frontend:"
curl -s -o /dev/null -w "%{http_code}" http://localhost:3000 || echo "❌ Frontend not responding"
echo ""

# Check database connection
echo "Database:"
cd backend
source venv/bin/activate
python << 'EOF'
import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine

async def check_db():
    try:
        engine = create_async_engine(os.getenv('DATABASE_URL'))
        async with engine.connect() as conn:
            await conn.execute('SELECT 1')
        print("✅ Database connected")
    except Exception as e:
        print(f"❌ Database error: {e}")

asyncio.run(check_db())
EOF
cd ..

echo ""
echo "Health check complete!"
