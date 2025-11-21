#!/bin/bash

set -e

echo "🚀 Starting Demo Copilot (Development Mode)..."
echo ""

# Check if we're in the project root
if [ ! -f "run_server.py" ]; then
    echo "❌ Error: Must run from project root directory"
    echo "Current directory: $(pwd)"
    exit 1
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "❌ Error: .env file not found"
    echo "Please run: ./scripts/setup.sh first"
    exit 1
fi

# Load environment variables
export $(cat .env | grep -v '^#' | xargs)

# Start backend
echo "📦 Starting backend server..."
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    python run_server.py &
    BACKEND_PID=$!
    echo "✓ Backend started (PID: $BACKEND_PID)"
else
    python run_server.py &
    BACKEND_PID=$!
    echo "✓ Backend started (PID: $BACKEND_PID)"
fi

# Wait a moment for backend to start
sleep 2

# Start frontend
echo "🌐 Starting frontend server..."
cd frontend
if [ -f "package.json" ]; then
    npm run dev > ../logs/frontend.log 2>&1 &
    FRONTEND_PID=$!
    echo "✓ Frontend started (PID: $FRONTEND_PID)"
    cd ..
else
    echo "⚠ Warning: frontend/package.json not found, skipping frontend"
    cd ..
fi

# Create PID file for cleanup
mkdir -p logs
echo "$BACKEND_PID" > logs/backend.pid
if [ -n "$FRONTEND_PID" ]; then
    echo "$FRONTEND_PID" > logs/frontend.pid
fi

echo ""
echo "=========================================="
echo "✅ Demo Copilot Started!"
echo "=========================================="
echo ""
echo "Services:"
echo "  📦 Backend API:  http://localhost:8000"
echo "  📚 API Docs:     http://localhost:8000/docs"
if [ -n "$FRONTEND_PID" ]; then
    echo "  🌐 Frontend:     http://localhost:3000"
fi
echo ""
echo "Logs:"
echo "  Backend:  tail -f logs/backend.log"
if [ -n "$FRONTEND_PID" ]; then
    echo "  Frontend: tail -f logs/frontend.log"
fi
echo ""
echo "To stop: ./scripts/stop-dev.sh"
echo "Press Ctrl+C to stop (may leave processes running)"
echo ""

# Trap Ctrl+C to cleanup
trap "echo ''; echo 'Stopping servers...'; kill $BACKEND_PID 2>/dev/null || true; kill $FRONTEND_PID 2>/dev/null || true; rm -f logs/*.pid; exit" INT

# Wait for processes (keeps script running)
wait
