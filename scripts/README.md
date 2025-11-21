# Demo Copilot Scripts

Automated setup and management scripts for Demo Copilot development.

## Quick Start

### Initial Setup

```bash
# Run setup script (first time only)
./scripts/setup.sh
```

This will:
- ✓ Check prerequisites (Python 3.10+, Node 18+, Git)
- ✓ Create project structure
- ✓ Set up Python virtual environment
- ✓ Install Python dependencies
- ✓ Install Playwright browsers
- ✓ Install Node.js dependencies
- ✓ Create `.env` configuration files
- ✓ Set up git hooks
- ✓ Create demo data structure

### Start Development

```bash
# Start both backend and frontend
./scripts/start-dev.sh
```

Access points:
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Frontend: http://localhost:3000

### Stop Development

```bash
# Stop all servers
./scripts/stop-dev.sh
```

## Available Scripts

### setup.sh

Initial environment setup. Run once after cloning the repository.

```bash
./scripts/setup.sh
```

**What it does:**
- Verifies prerequisites (Python, Node.js, Git)
- Creates project directory structure
- Sets up Python virtual environment
- Installs all dependencies (Python + Node.js)
- Installs Playwright browsers
- Creates `.env` files from templates
- Sets up git hooks
- Creates demo data directories

**When to use:**
- First time setting up the project
- After major dependency changes
- To reset development environment

---

### start-dev.sh

Start both backend and frontend servers in development mode.

```bash
./scripts/start-dev.sh
```

**What it does:**
- Checks for `.env` file
- Starts FastAPI backend server
- Starts Next.js frontend server
- Creates PID files for process management
- Provides access URLs

**Output:**
- Logs to `logs/backend.log` and `logs/frontend.log`
- PID files in `logs/*.pid`

**Stop with:**
- `./scripts/stop-dev.sh` (recommended)
- `Ctrl+C` (may leave processes running)

---

### stop-dev.sh

Stop all running development servers.

```bash
./scripts/stop-dev.sh
```

**What it does:**
- Kills processes by PID file
- Fallback: kills by process name
- Cleans up PID files

**Safe to run:**
- Even if servers aren't running
- Multiple times

---

### check-health.sh

Check the health of all Demo Copilot services.

```bash
./scripts/check-health.sh
```

**What it checks:**
- ✓ Backend API (HTTP health endpoint)
- ✓ Frontend (HTTP status)
- ✓ Database connection
- ✓ API keys configuration
- ✓ Running processes

**When to use:**
- After starting servers
- Before running demos
- Troubleshooting issues
- Verifying configuration

---

### reset-demo-env.sh

Reset the demo environment to clean state.

```bash
./scripts/reset-demo-env.sh
```

**⚠️ Warning:** This is destructive!

**What it does:**
- Drops and recreates database
- Clears all recordings
- Clears all logs
- Clears Python cache
- Clears frontend cache

**When to use:**
- Testing fresh environment
- After database schema changes
- Clearing old demo data
- Troubleshooting database issues

---

### test.sh

Run all tests and linting.

```bash
./scripts/test.sh
```

**What it tests:**
- Backend tests (pytest)
- Python syntax checking
- Frontend tests (Jest/Vitest)
- TypeScript/JavaScript linting
- Integration tests (if server is running)

**Exit codes:**
- `0` - All tests passed
- `1` - Some tests failed

**When to use:**
- Before committing code
- In CI/CD pipelines
- After making changes
- Before deployment

---

## Common Workflows

### First Time Setup

```bash
# 1. Clone repository
git clone https://github.com/numberlabs/demo-copilot.git
cd demo-copilot

# 2. Run setup
./scripts/setup.sh

# 3. Configure API keys
nano .env
# Add your ANTHROPIC_API_KEY and ELEVENLABS_API_KEY

# 4. Start development
./scripts/start-dev.sh

# 5. Check health
./scripts/check-health.sh
```

### Daily Development

```bash
# Start your day
./scripts/start-dev.sh

# Check everything is working
./scripts/check-health.sh

# Make changes...

# Run tests
./scripts/test.sh

# Stop servers
./scripts/stop-dev.sh
```

### Troubleshooting

```bash
# Something not working?

# 1. Check health
./scripts/check-health.sh

# 2. Stop everything
./scripts/stop-dev.sh

# 3. Reset environment
./scripts/reset-demo-env.sh

# 4. Re-run setup
./scripts/setup.sh

# 5. Start again
./scripts/start-dev.sh
```

### Testing & CI

```bash
# Before committing
./scripts/test.sh

# If tests fail, fix issues and re-test
./scripts/test.sh
```

## Environment Variables

Scripts use environment variables from `.env`:

**Required:**
```bash
ANTHROPIC_API_KEY=your-key-here
ELEVENLABS_API_KEY=your-key-here
```

**Optional:**
```bash
DATABASE_URL=sqlite+aiosqlite:///./demo_copilot.db
PORT=8000
HOST=0.0.0.0
FRONTEND_URL=http://localhost:3000
```

## Troubleshooting

### "Command not found"

Make scripts executable:
```bash
chmod +x scripts/*.sh
```

### "Must run from project root"

Navigate to project root:
```bash
cd /path/to/demo-pilot
./scripts/setup.sh
```

### "Python/Node not found"

Install prerequisites:
- Python 3.10+: https://python.org
- Node.js 18+: https://nodejs.org

### "Port already in use"

Stop existing servers:
```bash
./scripts/stop-dev.sh
# Or manually:
pkill -f "uvicorn"
pkill -f "next dev"
```

### Database errors

Reset database:
```bash
./scripts/reset-demo-env.sh
```

## Script Development

### Adding a New Script

1. Create script in `scripts/`
2. Add shebang: `#!/bin/bash`
3. Make executable: `chmod +x scripts/your-script.sh`
4. Document in this README
5. Test thoroughly

### Best Practices

- ✓ Use `set -e` to exit on errors
- ✓ Check prerequisites at start
- ✓ Provide clear output messages
- ✓ Use color coding (GREEN, RED, YELLOW)
- ✓ Clean up on failure
- ✓ Document all parameters
- ✓ Test on macOS and Linux

## Support

For issues with scripts:
1. Check this README
2. Run `./scripts/check-health.sh`
3. Check logs in `logs/`
4. Ask on #ai-demos Slack channel
