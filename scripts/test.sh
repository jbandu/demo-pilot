#!/bin/bash

set -e

echo "🧪 Running Demo Copilot Tests..."
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Track test results
backend_tests_passed=false
frontend_tests_passed=false
lint_passed=false

# Activate virtual environment if it exists
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
fi

# Backend tests
echo "================================"
echo "📦 Backend Tests"
echo "================================"
echo ""

# Check if pytest is installed
if command -v pytest &> /dev/null; then
    echo "Running Python tests..."

    # Check if tests directory exists
    if [ -d "backend/tests" ] || [ -d "tests" ]; then
        if pytest backend/tests/ -v --tb=short 2>/dev/null || pytest tests/ -v --tb=short 2>/dev/null; then
            echo -e "${GREEN}✓${NC} Backend tests passed"
            backend_tests_passed=true
        else
            echo -e "${RED}✗${NC} Backend tests failed"
        fi
    else
        echo -e "${YELLOW}⚠${NC} No tests found in backend/tests/ or tests/"
        echo "Skipping backend tests..."
        backend_tests_passed=true
    fi
else
    echo -e "${YELLOW}⚠${NC} pytest not installed"
    echo "To install: pip install pytest pytest-asyncio"
fi

echo ""

# Python linting
echo "================================"
echo "🔍 Python Linting"
echo "================================"
echo ""

echo "Checking Python syntax..."
python_files=$(find backend -name "*.py" 2>/dev/null || true)

if [ -n "$python_files" ]; then
    syntax_errors=0
    for file in $python_files; do
        if ! python3 -m py_compile "$file" 2>/dev/null; then
            echo -e "${RED}✗${NC} Syntax error in $file"
            syntax_errors=$((syntax_errors + 1))
        fi
    done

    if [ $syntax_errors -eq 0 ]; then
        echo -e "${GREEN}✓${NC} No Python syntax errors"
        lint_passed=true
    else
        echo -e "${RED}✗${NC} Found $syntax_errors syntax error(s)"
    fi
else
    echo -e "${YELLOW}⚠${NC} No Python files found"
    lint_passed=true
fi

echo ""

# Frontend tests
echo "================================"
echo "🌐 Frontend Tests"
echo "================================"
echo ""

if [ -d "frontend" ] && [ -f "frontend/package.json" ]; then
    cd frontend

    # Check if test script exists
    if grep -q "\"test\"" package.json; then
        echo "Running frontend tests..."

        if npm test 2>/dev/null; then
            echo -e "${GREEN}✓${NC} Frontend tests passed"
            frontend_tests_passed=true
        else
            echo -e "${RED}✗${NC} Frontend tests failed"
        fi
    else
        echo -e "${YELLOW}⚠${NC} No test script in package.json"
        echo "Skipping frontend tests..."
        frontend_tests_passed=true
    fi

    # Frontend linting
    echo ""
    echo "Checking TypeScript/JavaScript..."

    if grep -q "\"lint\"" package.json; then
        if npm run lint 2>/dev/null; then
            echo -e "${GREEN}✓${NC} Frontend linting passed"
        else
            echo -e "${YELLOW}⚠${NC} Frontend linting failed"
        fi
    else
        echo -e "${YELLOW}⚠${NC} No lint script in package.json"
    fi

    cd ..
else
    echo -e "${YELLOW}⚠${NC} Frontend not found, skipping frontend tests"
    frontend_tests_passed=true
fi

echo ""

# Integration tests
echo "================================"
echo "🔗 Integration Tests"
echo "================================"
echo ""

# Test API endpoints (if server is running)
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "Testing API endpoints..."

    # Test health endpoint
    if curl -s http://localhost:8000/health | grep -q "healthy"; then
        echo -e "${GREEN}✓${NC} Health endpoint working"
    else
        echo -e "${RED}✗${NC} Health endpoint failed"
    fi

    # Test root endpoint
    if curl -s http://localhost:8000/ | grep -q "Demo Copilot"; then
        echo -e "${GREEN}✓${NC} Root endpoint working"
    else
        echo -e "${RED}✗${NC} Root endpoint failed"
    fi
else
    echo -e "${YELLOW}⚠${NC} Backend not running, skipping integration tests"
    echo "To run integration tests, start the backend first:"
    echo "  python run_server.py"
fi

echo ""

# Summary
echo "================================"
echo "📊 Test Summary"
echo "================================"
echo ""

all_passed=true

if [ "$backend_tests_passed" = true ]; then
    echo -e "${GREEN}✓${NC} Backend tests"
else
    echo -e "${RED}✗${NC} Backend tests"
    all_passed=false
fi

if [ "$lint_passed" = true ]; then
    echo -e "${GREEN}✓${NC} Python linting"
else
    echo -e "${RED}✗${NC} Python linting"
    all_passed=false
fi

if [ "$frontend_tests_passed" = true ]; then
    echo -e "${GREEN}✓${NC} Frontend tests"
else
    echo -e "${RED}✗${NC} Frontend tests"
    all_passed=false
fi

echo ""

if [ "$all_passed" = true ]; then
    echo -e "${GREEN}✅ All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}❌ Some tests failed${NC}"
    exit 1
fi
