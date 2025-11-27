#!/bin/bash
set -e

echo "🧪 Running tests..."

# Backend tests
echo "Testing backend..."
cd backend
source venv/bin/activate
pytest tests/ -v
cd ..

# Frontend tests
echo "Testing frontend..."
cd frontend
npm test
cd ..

echo "✅ All tests passed!"
