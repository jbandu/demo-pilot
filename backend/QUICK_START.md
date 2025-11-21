# Quick Start Guide - Fixing Database Connection Error

## The Problem
The server is trying to connect to a database during startup and failing, causing the application to crash.

## Solution 1: Skip Database (Recommended for Development)

Add this line to your `backend/.env` file:

```bash
SKIP_DATABASE=true
```

Then restart the server:
```bash
cd ~/demo-pilot/backend
source venv/bin/activate
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

The server will start without attempting to connect to the database.

## Solution 2: Fix Database URL (If You Want Database Features)

Your current DATABASE_URL uses the wrong driver for async connections.

**Current (in .env):**
```
DATABASE_URL=postgresql://neondb_owner:...
```

**Change to:**
```
DATABASE_URL=postgresql+asyncpg://neondb_owner:...
```

Note the `+asyncpg` addition. The full corrected URL would be:
```
DATABASE_URL=postgresql+asyncpg://neondb_owner:npg_U3cV2pwZqOGA@ep-bitter-math-ahpxc9am-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require
```

(Note: I also removed `channel_binding=require` as asyncpg may not support it)

## What Was Changed

I've updated the backend code to:
- Add a `SKIP_DATABASE` environment variable
- Make database connections optional
- Allow the server to run without a database for development

These changes have been committed to branch: `claude/setup-uvicorn-dev-server-017NX5k1tRgm6Hq6RfUDTTRe`

## Pulling the Changes

If you want to pull my changes to your local machine:

```bash
cd ~/demo-pilot
git fetch origin
git checkout claude/setup-uvicorn-dev-server-017NX5k1tRgm6Hq6RfUDTTRe
git pull origin claude/setup-uvicorn-dev-server-017NX5k1tRgm6Hq6RfUDTTRe
```

Then add `SKIP_DATABASE=true` to your `.env` file and restart the server.
