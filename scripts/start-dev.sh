#!/bin/bash
set -e

echo "🚀 Starting Demo Copilot (Development Mode)..."

# Start backend
cd backend
source venv/bin/activate
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Start frontend
cd ../frontend
npm run dev &
FRONTEND_PID=$!

echo ""
echo "✅ Demo Copilot started!"
echo "📦 Backend: http://localhost:8000"
echo "🌐 Frontend: http://localhost:3000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop..."

# Wait for Ctrl+C
trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait
