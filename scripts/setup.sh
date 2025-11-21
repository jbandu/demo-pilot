#!/bin/bash

set -e

echo "🚀 Setting up Demo Copilot Development Environment..."
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running on macOS or Linux
OS="$(uname)"
if [[ "$OS" == "Darwin" ]]; then
    echo "📱 Detected macOS"
elif [[ "$OS" == "Linux" ]]; then
    echo "🐧 Detected Linux"
else
    echo "${RED}❌ Unsupported operating system${NC}"
    exit 1
fi

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
echo ""
echo "🔍 Checking prerequisites..."

# Check Python 3.11+
if command_exists python3; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
    echo "${GREEN}✓${NC} Python ${PYTHON_VERSION} found"
else
    echo "${RED}❌ Python 3.11+ required${NC}"
    exit 1
fi

# Check Node.js 20+
if command_exists node; then
    NODE_VERSION=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
    if [ "$NODE_VERSION" -ge 20 ]; then
        echo "${GREEN}✓${NC} Node.js $(node --version) found"
    else
        echo "${RED}❌ Node.js 20+ required (found v${NODE_VERSION})${NC}"
        exit 1
    fi
else
    echo "${RED}❌ Node.js 20+ required${NC}"
    exit 1
fi

# Check Docker
if command_exists docker; then
    echo "${GREEN}✓${NC} Docker found"
else
    echo "${YELLOW}⚠${NC} Docker not found (optional for local development)"
fi

# Check Git
if command_exists git; then
    echo "${GREEN}✓${NC} Git found"
else
    echo "${RED}❌ Git required${NC}"
    exit 1
fi

# Create project structure
echo ""
echo "📁 Creating project structure..."

mkdir -p backend/{agents/demo_scripts,api/routes,database,utils}
mkdir -p frontend/{app/demo,components,lib}
mkdir -p demo-environments/{insign/test-data,crew-intelligence/test-data}
mkdir -p scripts
mkdir -p docs
mkdir -p recordings
mkdir -p logs

echo "${GREEN}✓${NC} Project structure created"

# Setup Python virtual environment
echo ""
echo "🐍 Setting up Python environment..."

cd backend
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate

# Install Python dependencies
if [ -f "requirements.txt" ]; then
    echo "📦 Installing Python packages..."
    pip install --upgrade pip
    pip install -r requirements.txt
    echo "${GREEN}✓${NC} Python packages installed"
else
    echo "${YELLOW}⚠${NC} requirements.txt not found, skipping Python packages"
fi

# Install Playwright browsers
echo "🎭 Installing Playwright browsers..."
playwright install chromium
playwright install-deps chromium
echo "${GREEN}✓${NC} Playwright setup complete"

cd ..

# Setup Node.js environment
echo ""
echo "📦 Setting up Node.js environment..."

cd frontend
if [ ! -f "package.json" ]; then
    echo "${YELLOW}⚠${NC} package.json not found, initializing..."
    npm init -y
fi

echo "📦 Installing Node packages..."
npm install
echo "${GREEN}✓${NC} Node packages installed"

cd ..

# Create .env file if it doesn't exist
echo ""
echo "⚙️  Setting up environment variables..."

if [ ! -f ".env" ]; then
    cat > .env << 'EOF'
# Anthropic
ANTHROPIC_API_KEY=your_anthropic_key_here

# ElevenLabs
ELEVENLABS_API_KEY=your_elevenlabs_key_here

# OpenAI (for Whisper)
OPENAI_API_KEY=your_openai_key_here

# Database (Neon PostgreSQL)
DATABASE_URL=postgresql://user:pass@neon.tech:5432/demo_copilot

# Redis
REDIS_URL=redis://localhost:6379

# InSign Demo Environment
INSIGN_DEMO_URL=https://demo.insign.io
INSIGN_DEMO_EMAIL=demo@numberlabs.ai
INSIGN_DEMO_PASSWORD=your_demo_password

# Server URLs
BACKEND_URL=http://localhost:8000
FRONTEND_URL=http://localhost:3000

# Vercel (for deployment)
VERCEL_TOKEN=your_vercel_token_here

# GCP (for deployment)
GCP_PROJECT_ID=your_gcp_project_id
GCP_REGION=us-central1
EOF
    echo "${GREEN}✓${NC} Created .env file"
    echo "${YELLOW}⚠${NC} Please update .env with your actual API keys"
else
    echo "${GREEN}✓${NC} .env file already exists"
fi

# Create backend/.env symlink
if [ ! -f "backend/.env" ]; then
    ln -s ../.env backend/.env
    echo "${GREEN}✓${NC} Created backend/.env symlink"
fi

# Create frontend/.env.local
if [ ! -f "frontend/.env.local" ]; then
    cat > frontend/.env.local << 'EOF'
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
EOF
    echo "${GREEN}✓${NC} Created frontend/.env.local"
fi

# Setup demo data
echo ""
echo "📄 Setting up demo data..."

# Create sample documents for InSign demo
mkdir -p demo-environments/insign/test-data

# Create a simple sample PDF (placeholder - replace with actual documents)
cat > demo-environments/insign/test-data/README.md << 'EOF'
# InSign Demo Test Data

Place your demo documents here:
- NDA_Template.pdf
- Employment_Agreement.pdf
- Consulting_Contract.pdf

These will be used during InSign demos.
EOF

echo "${GREEN}✓${NC} Demo data structure created"

# Setup git hooks (optional)
echo ""
echo "🪝 Setting up git hooks..."

if [ -d ".git" ]; then
    cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
# Run Python linting
cd backend
source venv/bin/activate
black --check . || exit 1
flake8 . || exit 1
cd ..

# Run TypeScript checks
cd frontend
npm run lint || exit 1
cd ..

echo "✅ Pre-commit checks passed"
EOF
    chmod +x .git/hooks/pre-commit
    echo "${GREEN}✓${NC} Git hooks installed"
fi

# Create helpful scripts
echo ""
echo "🛠️  Creating utility scripts..."

# Start dev script
cat > scripts/start-dev.sh << 'EOF'
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
EOF
chmod +x scripts/start-dev.sh

# Stop dev script
cat > scripts/stop-dev.sh << 'EOF'
#!/bin/bash
echo "🛑 Stopping Demo Copilot..."
pkill -f "uvicorn api.main:app"
pkill -f "next dev"
echo "✅ Stopped"
EOF
chmod +x scripts/stop-dev.sh

# Test script
cat > scripts/test.sh << 'EOF'
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
EOF
chmod +x scripts/test.sh

echo "${GREEN}✓${NC} Utility scripts created"

# Final summary
echo ""
echo "=========================================="
echo "${GREEN}✅ Setup Complete!${NC}"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Update .env with your API keys"
echo "2. Add demo documents to demo-environments/insign/test-data/"
echo "3. Start development: ./scripts/start-dev.sh"
echo ""
echo "Useful commands:"
echo "  ${GREEN}./scripts/start-dev.sh${NC}   - Start development servers"
echo "  ${GREEN}./scripts/stop-dev.sh${NC}    - Stop development servers"
echo "  ${GREEN}./scripts/test.sh${NC}        - Run tests"
echo "  ${GREEN}docker-compose up${NC}        - Start with Docker"
echo ""
echo "Documentation:"
echo "  📚 API Docs: http://localhost:8000/docs (after starting)"
echo "  📖 README: docs/README.md"
echo ""
