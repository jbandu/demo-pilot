# Quick Start Guide - Running the Backend Server

## Environment Variables

The backend now automatically loads environment variables from the `backend/.env` file when it starts. No need to export them manually!

## Starting the Server

```bash
cd ~/demo-pilot/backend
source venv/bin/activate
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

The server will automatically:
- Load environment variables from `.env` file
- Start on `http://0.0.0.0:8000`
- Auto-reload when you make code changes

## Database Configuration

You have two options for database configuration:

### Option 1: Skip Database (Recommended for Development)

If you don't need database features or don't have a database set up yet, add this line to your `backend/.env` file:

```bash
SKIP_DATABASE=true
```

The server will start without attempting to connect to the database. This is useful when you just want to test the API.

### Option 2: Connect to a Real Database

If you want to use database features, make sure your `backend/.env` has a valid `DATABASE_URL`.

**Important:** For async connections (which this app uses), you need to use the `postgresql+asyncpg://` protocol:

```bash
DATABASE_URL=postgresql+asyncpg://username:password@host:port/database
```

**Example with Neon database:**
```bash
DATABASE_URL=postgresql+asyncpg://neondb_owner:npg_U3cV2pwZqOGA@ep-bitter-math-ahpxc9am-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require
```

**Common mistake:** Using `postgresql://` instead of `postgresql+asyncpg://` will cause connection errors.

## Required Environment Variables

Make sure your `backend/.env` file has these variables:

```bash
# Required for AI features
ANTHROPIC_API_KEY=your_anthropic_api_key
OPENAI_API_KEY=your_openai_api_key

# Required for voice features
ELEVENLABS_API_KEY=your_elevenlabs_api_key

# Database (optional - set SKIP_DATABASE=true if not using)
DATABASE_URL=postgresql+asyncpg://user:pass@host/db
SKIP_DATABASE=true  # Set to true to skip database

# InSign Demo credentials
INSIGN_DEMO_URL=https://your-demo-url
INSIGN_DEMO_EMAIL=your-email
INSIGN_DEMO_PASSWORD=your-password
```

## Pulling the Latest Changes

If you're working from a different machine or want to pull the latest changes:

```bash
cd ~/demo-pilot
git fetch origin
git checkout claude/setup-uvicorn-dev-server-017NX5k1tRgm6Hq6RfUDTTRe
git pull origin claude/setup-uvicorn-dev-server-017NX5k1tRgm6Hq6RfUDTTRe
```

## What Was Fixed

Recent updates include:
- ✅ Automatic `.env` file loading on server startup
- ✅ `SKIP_DATABASE` option for development without database
- ✅ Better error handling for missing environment variables
- ✅ Fixed database session cleanup issues

## Troubleshooting

### Server won't start - "Connection refused"
- Add `SKIP_DATABASE=true` to your `.env` file, or
- Make sure your `DATABASE_URL` uses `postgresql+asyncpg://` protocol

### API keys not found
- Make sure your `.env` file is in the `backend/` directory
- Restart the server after modifying `.env`
- The server will log "Loaded environment variables from..." when it loads the `.env` file

### Database connection fails
- Check that `DATABASE_URL` uses `postgresql+asyncpg://` (not just `postgresql://`)
- Or set `SKIP_DATABASE=true` to run without database
