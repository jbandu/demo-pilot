# 🚀 Deployment Guide

This guide covers deploying Demo Copilot to production using Railway (recommended) or alternative platforms.

## 📋 Table of Contents

- [Prerequisites](#prerequisites)
- [Option 1: Railway (Recommended)](#option-1-railway-recommended)
- [Option 2: Vercel + Railway Hybrid](#option-2-vercel--railway-hybrid)
- [Option 3: Other Platforms](#option-3-other-platforms)
- [Environment Variables](#environment-variables)
- [Post-Deployment](#post-deployment)

---

## Prerequisites

Before deploying, ensure you have:

✅ **API Keys:**
- Anthropic API key (Claude)
- ElevenLabs API key (Voice)
- OpenAI API key (Whisper)

✅ **Database:**
- Neon PostgreSQL database (or Railway PostgreSQL)
- Database URL with `postgresql+asyncpg://` protocol

✅ **Custom Voice (Optional):**
- ElevenLabs voice ID for your custom cloned voice

---

## Option 1: Railway (Recommended)

**Why Railway?**
- ✓ WebSocket support (critical for real-time demo streaming)
- ✓ Long-running processes (demos can run for minutes)
- ✓ Playwright support (full Docker containers)
- ✓ Persistent storage (audio cache)
- ✓ No timeouts
- ✓ Simple monorepo deployment

### Step 1: Connect to Railway

1. Go to [Railway.app](https://railway.app)
2. Sign in with GitHub
3. Click **"New Project"** → **"Deploy from GitHub repo"**
4. Select your `demo-pilot` repository
5. Railway will detect both `backend` and `frontend` services

### Step 2: Configure Services

Railway should auto-detect two services:

**Backend Service:**
- **Root Directory:** `/backend`
- **Dockerfile:** `backend/Dockerfile`
- **Port:** 8000 (Railway auto-assigns)

**Frontend Service:**
- **Root Directory:** `/frontend`
- **Dockerfile:** `frontend/Dockerfile`
- **Port:** 3000 (Railway auto-assigns)

### Step 3: Add Database (Optional)

If not using Neon:
1. Click **"+ New"** → **"Database"** → **"PostgreSQL"**
2. Railway will create a database and provide `DATABASE_URL`

### Step 4: Set Environment Variables

**Backend Environment Variables:**

```bash
# Required
ANTHROPIC_API_KEY=sk-ant-...
ELEVENLABS_API_KEY=...
OPENAI_API_KEY=sk-...

# Database (use Railway's ${{Postgres.DATABASE_URL}} or Neon)
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/dbname
SKIP_DATABASE=false

# Voice (optional - uses Rachel by default)
ELEVENLABS_VOICE_ID=your_custom_voice_id

# InSign Demo Credentials
INSIGN_DEMO_URL=https://demo.insign.io
INSIGN_DEMO_EMAIL=demo@example.com
INSIGN_DEMO_PASSWORD=your_password

# Audio
PLAY_AUDIO_LOCALLY=false  # Don't play on server in production
AUDIO_CACHE_DIR=/app/audio_cache

# Redis (optional)
REDIS_URL=redis://localhost:6379
```

**Frontend Environment Variables:**

```bash
# Backend URL (use Railway's backend service URL)
NEXT_PUBLIC_BACKEND_URL=https://your-backend.railway.app
```

### Step 5: Deploy

1. Railway automatically deploys on git push
2. Monitor deployment logs in Railway dashboard
3. Backend health check: `https://your-backend.railway.app/health`
4. Frontend: `https://your-frontend.railway.app`

### Step 6: Set Up Domain (Optional)

1. In Railway service settings → **"Networking"**
2. Click **"Generate Domain"** or **"Custom Domain"**
3. Update `NEXT_PUBLIC_BACKEND_URL` with new domain

**Cost Estimate:** $10-20/month for both services

---

## Option 2: Vercel + Railway Hybrid

Deploy frontend on Vercel (best Next.js performance) and backend on Railway.

### Deploy Backend to Railway

Follow **Option 1** steps above, but only deploy the backend service.

### Deploy Frontend to Vercel

1. Go to [Vercel](https://vercel.com)
2. Import `demo-pilot` repository
3. **Root Directory:** `frontend`
4. **Framework Preset:** Next.js
5. **Environment Variables:**
   ```bash
   NEXT_PUBLIC_BACKEND_URL=https://your-backend.railway.app
   ```
6. Deploy

### Configure CORS

Update `backend/api/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://your-frontend.vercel.app",
        "http://localhost:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Cost Estimate:** $5-15/month (Vercel free + Railway backend)

---

## Option 3: Other Platforms

### Render

Similar to Railway, supports Docker + WebSockets.

1. Create account at [Render.com](https://render.com)
2. New Web Service from GitHub
3. Select Docker for both services
4. Set environment variables
5. Free tier available (limited resources)

### Fly.io

Good for edge deployment, more complex setup.

```bash
# Install flyctl
curl -L https://fly.io/install.sh | sh

# Deploy backend
cd backend
fly launch
fly deploy

# Deploy frontend
cd frontend
fly launch
fly deploy
```

---

## Environment Variables

### Complete Backend .env

```bash
# AI APIs
ANTHROPIC_API_KEY=sk-ant-api03-...
ELEVENLABS_API_KEY=sk_...
OPENAI_API_KEY=sk-...

# Voice
ELEVENLABS_VOICE_ID=your_voice_id  # Optional, defaults to Rachel

# Database
DATABASE_URL=postgresql+asyncpg://user:pass@host.neon.tech:5432/demo_copilot
SKIP_DATABASE=false

# InSign Demo
INSIGN_DEMO_URL=https://demo.insign.io
INSIGN_DEMO_EMAIL=demo@example.com
INSIGN_DEMO_PASSWORD=your_password

# Redis (optional)
REDIS_URL=redis://localhost:6379

# Audio
PLAY_AUDIO_LOCALLY=false  # Set to false in production
AUDIO_CACHE_DIR=/app/audio_cache

# Server URLs
BACKEND_URL=https://your-backend-url.com
FRONTEND_URL=https://your-frontend-url.com
```

### Complete Frontend .env

```bash
NEXT_PUBLIC_BACKEND_URL=https://your-backend-url.com
```

---

## Post-Deployment

### 1. Test Health Endpoints

```bash
# Backend health
curl https://your-backend.railway.app/health

# Should return:
{"status": "healthy", "version": "1.0.0"}
```

### 2. Initialize Database

The database tables will be created automatically on first startup.

Verify by checking logs for:
```
Database initialized successfully
Created tables: demo_sessions, demo_actions, customer_questions, demo_scripts, demo_analytics
```

### 3. Test a Demo

1. Visit your frontend URL
2. Click "Start Demo"
3. Select a demo type (e.g., InSign)
4. Monitor backend logs for:
   - Browser initialization
   - Voice generation
   - WebSocket connection
   - Demo progress

### 4. Monitor Costs

**ElevenLabs Usage:**
- Audio cache reduces API calls significantly
- Monitor usage at: https://elevenlabs.io/app/usage
- 30k characters/month ≈ 20-30 demos

**Database:**
- Neon free tier: 512MB storage
- Monitor at Neon dashboard

**Railway/Vercel:**
- Monitor usage in platform dashboards
- Set up billing alerts

### 5. Set Up Monitoring (Optional)

**Sentry for Error Tracking:**
```bash
pip install sentry-sdk
```

```python
# backend/api/main.py
import sentry_sdk
sentry_sdk.init(dsn="your-sentry-dsn")
```

**LogDNA/Datadog for Logs:**
Configure in Railway dashboard under service settings.

---

## Troubleshooting

### Issue: WebSocket Connection Failed

**Solution:**
- Ensure WebSocket URL uses `wss://` (not `ws://`) in production
- Check CORS settings allow your frontend domain
- Verify Railway service is running

### Issue: Audio Not Generating

**Check:**
1. ELEVENLABS_API_KEY is set correctly
2. ElevenLabs quota not exceeded
3. ELEVENLABS_VOICE_ID is valid (check at elevenlabs.io)
4. Backend logs for ElevenLabs errors

### Issue: Browser Actions Timeout

**Solutions:**
- Increase timeout in `browser_controller.py` (already set to 60s)
- Check demo script selectors are correct
- Verify target website is accessible from Railway's network
- Review browser logs in recordings

### Issue: Database Connection Error

**Check:**
1. DATABASE_URL uses `postgresql+asyncpg://` protocol
2. Database allows connections from Railway IPs
3. SSL mode is correct (`?ssl=require` for Neon)
4. Database exists and credentials are correct

### Issue: Frontend Can't Reach Backend

**Check:**
1. `NEXT_PUBLIC_BACKEND_URL` is set correctly in Vercel
2. Backend CORS allows frontend domain
3. Backend health endpoint responds
4. Railway backend service is running

---

## Scaling

### Horizontal Scaling

**Railway:**
- Click service → **"Settings"** → **"Replicas"**
- Increase to 2+ instances
- Add Redis for session management

**Load Balancer:**
Railway handles this automatically.

### Vertical Scaling

**Railway:**
- Upgrade plan for more resources
- Monitor CPU/RAM usage in dashboard

### Optimizations

1. **Audio Cache:** Already implemented - saves 90% of ElevenLabs calls
2. **Database Connection Pooling:** Add pgbouncer
3. **CDN for Static Assets:** Vercel does this automatically
4. **Redis Caching:** For demo session state

---

## Security Checklist

✅ **Secrets Management:**
- All API keys in environment variables (never committed)
- Rotate keys periodically

✅ **Database:**
- Use SSL connections
- Restrict database access by IP if possible
- Regular backups (Neon does this automatically)

✅ **CORS:**
- Only allow specific frontend domains
- No `allow_origins=["*"]` in production

✅ **Rate Limiting:**
- Add rate limiting to API endpoints
- Prevent demo spam

✅ **Error Handling:**
- Don't expose API keys in error messages
- Use Sentry for error tracking

---

## Support

For issues:
1. Check Railway/Vercel logs
2. Review backend logs for errors
3. Test health endpoints
4. Verify environment variables

---

**Need Help?** Open an issue in the GitHub repository or contact Number Labs.
