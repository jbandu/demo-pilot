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
    echo -e "${RED}❌ Unsupported operating system${NC}"
    exit 1
fi

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
echo ""
echo "🔍 Checking prerequisites..."

# Check Python 3.10+
if command_exists python3; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
    echo -e "${GREEN}✓${NC} Python ${PYTHON_VERSION} found"
else
    echo -e "${RED}❌ Python 3.10+ required${NC}"
    exit 1
fi

# Check Node.js 18+
if command_exists node; then
    NODE_VERSION=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
    if [ "$NODE_VERSION" -ge 18 ]; then
        echo -e "${GREEN}✓${NC} Node.js $(node --version) found"
    else
        echo -e "${RED}❌ Node.js 18+ required (found v${NODE_VERSION})${NC}"
        exit 1
    fi
else
    echo -e "${RED}❌ Node.js 18+ required${NC}"
    exit 1
fi

# Check Docker
if command_exists docker; then
    echo -e "${GREEN}✓${NC} Docker found"
else
    echo -e "${YELLOW}⚠${NC} Docker not found (optional for local development)"
fi

# Check Git
if command_exists git; then
    echo -e "${GREEN}✓${NC} Git found"
else
    echo -e "${RED}❌ Git required${NC}"
    exit 1
fi

# Create project structure if needed
echo ""
echo "📁 Verifying project structure..."

mkdir -p backend/{agents/demo_scripts,api/routes,database,utils}
mkdir -p frontend/{app/demo,components,lib}
mkdir -p demo-environments/{insign/test-data,crew-intelligence/test-data}
mkdir -p scripts
mkdir -p docs
mkdir -p recordings
mkdir -p logs

echo -e "${GREEN}✓${NC} Project structure verified"

# Setup Python virtual environment
echo ""
echo "🐍 Setting up Python environment..."

if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}✓${NC} Created virtual environment"
else
    echo -e "${GREEN}✓${NC} Virtual environment already exists"
fi

source venv/bin/activate

# Install Python dependencies
if [ -f "requirements.txt" ]; then
    echo "📦 Installing Python packages..."
    pip install --upgrade pip --quiet
    pip install -r requirements.txt --quiet
    echo -e "${GREEN}✓${NC} Python packages installed"
else
    echo -e "${YELLOW}⚠${NC} requirements.txt not found, skipping Python packages"
fi

# Install Playwright browsers
echo "🎭 Installing Playwright browsers..."
playwright install chromium
echo -e "${GREEN}✓${NC} Playwright setup complete"

# Setup Node.js environment
echo ""
echo "📦 Setting up Node.js environment..."

cd frontend
if [ ! -f "package.json" ]; then
    echo -e "${YELLOW}⚠${NC} package.json not found in frontend/"
else
    echo "📦 Installing Node packages..."
    npm install --silent
    echo -e "${GREEN}✓${NC} Node packages installed"
fi

cd ..

# Create .env file if it doesn't exist
echo ""
echo "⚙️  Setting up environment variables..."

if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo -e "${GREEN}✓${NC} Created .env file from .env.example"
    else
        cat > .env << 'EOF'
# Anthropic API Key (required)
ANTHROPIC_API_KEY=your-anthropic-api-key-here

# ElevenLabs API Key (for voice synthesis)
ELEVENLABS_API_KEY=your-elevenlabs-api-key-here

# Database URL (default: SQLite)
DATABASE_URL=sqlite+aiosqlite:///./demo_copilot.db

# Server configuration
PORT=8000
HOST=0.0.0.0

# Frontend URL (for CORS)
FRONTEND_URL=http://localhost:3000
EOF
        echo -e "${GREEN}✓${NC} Created .env file"
    fi
    echo -e "${YELLOW}⚠${NC} Please update .env with your actual API keys"
else
    echo -e "${GREEN}✓${NC} .env file already exists"
fi

# Create frontend/.env.local
if [ ! -f "frontend/.env.local" ]; then
    cat > frontend/.env.local << 'EOF'
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
EOF
    echo -e "${GREEN}✓${NC} Created frontend/.env.local"
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

echo -e "${GREEN}✓${NC} Demo data structure created"

# Setup git hooks (optional)
echo ""
echo "🪝 Setting up git hooks..."

if [ -d ".git" ]; then
    mkdir -p .git/hooks
    cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
# Pre-commit hook for Demo Copilot

echo "Running pre-commit checks..."

# Check Python files
python_files=$(git diff --cached --name-only --diff-filter=ACM | grep '\.py$')
if [ -n "$python_files" ]; then
    echo "Checking Python files..."
    for file in $python_files; do
        python3 -m py_compile "$file" || exit 1
    done
fi

echo "✅ Pre-commit checks passed"
EOF
    chmod +x .git/hooks/pre-commit
    echo -e "${GREEN}✓${NC} Git hooks installed"
fi

# Final summary
echo ""
echo "=========================================="
echo -e "${GREEN}✅ Setup Complete!${NC}"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Update .env with your API keys"
echo "   nano .env"
echo ""
echo "2. Start the development server:"
echo "   python run_server.py"
echo ""
echo "3. (Optional) Start the frontend in another terminal:"
echo "   cd frontend && npm run dev"
echo ""
echo "Useful commands:"
echo "  ${GREEN}./scripts/start-dev.sh${NC}     - Start both backend and frontend"
echo "  ${GREEN}./scripts/stop-dev.sh${NC}      - Stop all servers"
echo "  ${GREEN}./scripts/check-health.sh${NC}  - Check system health"
echo "  ${GREEN}python run_server.py${NC}       - Start backend only"
echo ""
echo "Documentation:"
echo "  📚 API Docs: http://localhost:8000/docs (after starting)"
echo "  📖 README: README.md"
echo ""
