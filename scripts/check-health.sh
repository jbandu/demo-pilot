#!/bin/bash

echo "🏥 Checking Demo Copilot Health..."
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check backend API
echo "📦 Backend API (http://localhost:8000):"
if command -v curl &> /dev/null; then
    response=$(curl -s -w "%{http_code}" http://localhost:8000/health 2>/dev/null)
    http_code="${response: -3}"

    if [ "$http_code" = "200" ]; then
        echo -e "${GREEN}✓${NC} Backend is healthy"
        # Try to parse JSON response if jq is available
        if command -v jq &> /dev/null; then
            response_body="${response:0:-3}"
            echo "$response_body" | jq . 2>/dev/null || echo "$response_body"
        fi
    else
        echo -e "${RED}✗${NC} Backend not responding (HTTP $http_code)"
    fi
else
    echo -e "${YELLOW}⚠${NC} curl not installed, skipping backend check"
fi

echo ""

# Check frontend
echo "🌐 Frontend (http://localhost:3000):"
if command -v curl &> /dev/null; then
    http_code=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000 2>/dev/null)

    if [ "$http_code" = "200" ] || [ "$http_code" = "304" ]; then
        echo -e "${GREEN}✓${NC} Frontend is running"
    else
        echo -e "${RED}✗${NC} Frontend not responding (HTTP $http_code)"
    fi
else
    echo -e "${YELLOW}⚠${NC} curl not installed, skipping frontend check"
fi

echo ""

# Check database connection
echo "🗄️  Database:"
if [ -f ".env" ]; then
    export $(cat .env | grep -v '^#' | grep 'DATABASE_URL' | xargs)
fi

# Activate virtual environment if it exists
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
fi

python << 'EOF'
import asyncio
import os
import sys

# Add project root to path
sys.path.insert(0, os.getcwd())

async def check_db():
    try:
        from sqlalchemy.ext.asyncio import create_async_engine

        db_url = os.getenv('DATABASE_URL', 'sqlite+aiosqlite:///./demo_copilot.db')
        engine = create_async_engine(db_url, echo=False)

        async with engine.connect() as conn:
            await conn.execute(__import__('sqlalchemy').text('SELECT 1'))

        await engine.dispose()
        print("\033[0;32m✓\033[0m Database connected")
        print(f"  URL: {db_url.split('@')[-1] if '@' in db_url else 'local SQLite'}")

    except Exception as e:
        print(f"\033[0;31m✗\033[0m Database error: {e}")

asyncio.run(check_db())
EOF

echo ""

# Check API keys
echo "🔑 API Keys:"

if [ -f ".env" ]; then
    source .env

    # Check Anthropic
    if [ -n "$ANTHROPIC_API_KEY" ] && [ "$ANTHROPIC_API_KEY" != "your-anthropic-api-key-here" ]; then
        echo -e "${GREEN}✓${NC} Anthropic API key configured"
    else
        echo -e "${YELLOW}⚠${NC} Anthropic API key not configured"
    fi

    # Check ElevenLabs
    if [ -n "$ELEVENLABS_API_KEY" ] && [ "$ELEVENLABS_API_KEY" != "your-elevenlabs-api-key-here" ]; then
        echo -e "${GREEN}✓${NC} ElevenLabs API key configured"
    else
        echo -e "${YELLOW}⚠${NC} ElevenLabs API key not configured"
    fi
else
    echo -e "${RED}✗${NC} .env file not found"
fi

echo ""

# Check processes
echo "⚙️  Processes:"

backend_running=false
frontend_running=false

if pgrep -f "python.*run_server.py" > /dev/null || pgrep -f "uvicorn.*backend.api.main" > /dev/null; then
    backend_pid=$(pgrep -f "python.*run_server.py" -o || pgrep -f "uvicorn.*backend.api.main" -o)
    echo -e "${GREEN}✓${NC} Backend running (PID: $backend_pid)"
    backend_running=true
else
    echo -e "${RED}✗${NC} Backend not running"
fi

if pgrep -f "next dev" > /dev/null || pgrep -f "node.*next" > /dev/null; then
    frontend_pid=$(pgrep -f "next dev" -o || pgrep -f "node.*next" -o)
    echo -e "${GREEN}✓${NC} Frontend running (PID: $frontend_pid)"
    frontend_running=true
else
    echo -e "${RED}✗${NC} Frontend not running"
fi

echo ""
echo "=========================================="

if [ "$backend_running" = true ]; then
    echo -e "${GREEN}✅ Health Check Passed${NC}"
    echo ""
    echo "Access points:"
    echo "  • Backend: http://localhost:8000"
    echo "  • API Docs: http://localhost:8000/docs"
    if [ "$frontend_running" = true ]; then
        echo "  • Frontend: http://localhost:3000"
    fi
else
    echo -e "${YELLOW}⚠ Health Check Failed${NC}"
    echo ""
    echo "To start servers:"
    echo "  ./scripts/start-dev.sh"
fi

echo "=========================================="
echo ""
