# 🚂 Railway Deployment Guide

Complete guide for deploying Demo Copilot entirely on Railway.app with internal networking.

## 📋 What You'll Deploy

```
Railway Project: demo-copilot
├── PostgreSQL Database (managed)
├── Backend Service (Python/FastAPI)
├── Frontend Service (Next.js)
└── [Future] InSign App + Database
```

**Total Cost:** ~$15-25/month for everything

---

## 🚀 Step-by-Step Deployment

### Step 1: Create Railway Account

1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub (recommended)
3. Verify email
4. You'll get $5 free credit to start

### Step 2: Create New Project

1. Click **"New Project"**
2. Select **"Deploy from GitHub repo"**
3. Authorize Railway to access your GitHub
4. Select **`demo-pilot`** repository
5. Railway will analyze the repo

### Step 3: Add PostgreSQL Database

**IMPORTANT: Do this FIRST before deploying services**

1. In your Railway project, click **"+ New"**
2. Select **"Database"** → **"PostgreSQL"**
3. Railway creates a PostgreSQL instance
4. Note: Railway automatically creates a `DATABASE_URL` variable

**Database Details:**
- **Name:** Postgres (Railway auto-names it)
- **Region:** us-west1 (or choose yours)
- **Storage:** Starts at 1GB, scales automatically
- **Connection:** Private networking enabled by default

### Step 4: Deploy Backend Service

1. Click **"+ New"** → **"GitHub Repo"** → Select `demo-pilot`
2. Railway detects multiple services, choose **"backend"**
3. Configure:
   - **Service Name:** `backend`
   - **Root Directory:** `backend`
   - **Dockerfile:** Railway auto-detects `backend/Dockerfile`

**Build Settings:**
```
Builder: Dockerfile
Build Path: backend
Dockerfile Path: backend/Dockerfile
```

### Step 5: Configure Backend Environment Variables

Click on **backend service** → **"Variables"** tab:

```bash
# AI APIs (replace with your keys)
ANTHROPIC_API_KEY=sk-ant-api03-...
ELEVENLABS_API_KEY=sk_...
OPENAI_API_KEY=sk-...

# Voice (your custom voice ID)
ELEVENLABS_VOICE_ID=your_custom_voice_id_from_elevenlabs

# Database - Use Railway's internal reference
DATABASE_URL=${{Postgres.DATABASE_URL}}

# IMPORTANT: Railway provides postgresql:// but we need asyncpg
# We'll fix this in code (see Step 9)

SKIP_DATABASE=false

# InSign Demo Credentials
INSIGN_DEMO_URL=https://demo.insign.io
INSIGN_DEMO_EMAIL=demo@example.com
INSIGN_DEMO_PASSWORD=your_demo_password

# Redis (optional - add later if needed)
# REDIS_URL=redis://localhost:6379

# Audio Settings
PLAY_AUDIO_LOCALLY=false  # Don't play on server in production
AUDIO_CACHE_DIR=/app/audio_cache

# Server URLs (Railway will auto-provide domains)
# Leave these for now, we'll add after deployment
```

**Important Railway Variables:**

Railway provides these automatically (don't set manually):
- `PORT` - Railway assigns this dynamically
- `RAILWAY_ENVIRONMENT` - production/staging/etc
- `RAILWAY_PROJECT_ID` - your project ID

### Step 6: Deploy Frontend Service

1. Click **"+ New"** → **"GitHub Repo"** → Select `demo-pilot` again
2. Choose **"frontend"** service
3. Configure:
   - **Service Name:** `frontend`
   - **Root Directory:** `frontend`
   - **Dockerfile:** Railway auto-detects `frontend/Dockerfile`

**Build Settings:**
```
Builder: Dockerfile
Build Path: frontend
Dockerfile Path: frontend/Dockerfile
```

### Step 7: Configure Frontend Environment Variables

Click on **frontend service** → **"Variables"** tab:

```bash
# Backend URL - Use Railway's internal reference
NEXT_PUBLIC_BACKEND_URL=https://${{backend.RAILWAY_PUBLIC_DOMAIN}}
```

**Railway Magic:** `${{backend.RAILWAY_PUBLIC_DOMAIN}}` automatically resolves to your backend service's URL!

### Step 8: Enable Public Networking

**Backend:**
1. Click **backend service** → **"Settings"** → **"Networking"**
2. Click **"Generate Domain"**
3. You'll get: `backend-production-xxxx.up.railway.app`
4. Note this URL for frontend config

**Frontend:**
1. Click **frontend service** → **"Settings"** → **"Networking"**
2. Click **"Generate Domain"**
3. You'll get: `frontend-production-xxxx.up.railway.app`
4. This is your public demo URL!

### Step 9: Fix Database URL for AsyncPG

Railway provides `postgresql://` but we need `postgresql+asyncpg://`

**Option A: In Code (Recommended)**

Update `backend/api/main.py`:

```python
# Add this function at the top
def fix_database_url(url: str) -> str:
    """Convert Railway's postgres:// URL to asyncpg format"""
    if url and url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+asyncpg://")
    elif url and url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+asyncpg://")
    return url

# Then use it:
database_url = fix_database_url(os.getenv("DATABASE_URL", ""))
```

**Option B: Override Variable**

In backend variables, set:
```bash
DATABASE_URL=postgresql+asyncpg://${{Postgres.POSTGRES_USER}}:${{Postgres.POSTGRES_PASSWORD}}@${{Postgres.RAILWAY_PRIVATE_DOMAIN}}:5432/${{Postgres.POSTGRES_DB}}
```

### Step 10: Deploy!

Railway auto-deploys when you push to GitHub. For manual deploy:

1. Each service has a **"Deployments"** tab
2. Click **"Deploy"** or wait for auto-deploy
3. Monitor build logs in real-time

**Watch the logs for:**
- ✅ Docker build success
- ✅ Dependencies installed
- ✅ Playwright browsers installed
- ✅ Database connection success
- ✅ Server started on PORT

### Step 11: Initialize Database

Railway PostgreSQL starts empty. Initialize tables:

**Method 1: Automatic (Recommended)**

The backend already has auto-initialization in `api/main.py`:

```python
@app.on_event("startup")
async def startup_event():
    if not skip_database:
        await init_db()  # Creates tables automatically
```

Just deploy and it handles it!

**Method 2: Manual SQL**

1. Click **Postgres service** → **"Data"** tab
2. Click **"Query"**
3. Run the initialization SQL from `backend/database/schema.sql`

### Step 12: Verify Deployment

**Health Checks:**

```bash
# Backend
curl https://your-backend.up.railway.app/health

# Should return:
{"status": "healthy", "version": "1.0.0"}

# Database
curl https://your-backend.up.railway.app/api/health/database

# Should return:
{"database": "connected"}
```

**Test a Demo:**
1. Visit `https://your-frontend.up.railway.app`
2. Click "Start Demo"
3. Select demo type
4. Watch it run!

---

## 🔧 Internal Networking

Railway services communicate via **private network** automatically!

**How it works:**

```
Frontend → Internal Network → Backend (< 5ms)
Backend → Internal Network → Database (< 2ms)
```

**Use private domains for internal traffic:**

```bash
# Instead of public domain:
https://backend-production-xxxx.up.railway.app

# Use private domain (Railway provides automatically):
backend.railway.internal:${{PORT}}
```

**Update frontend to use private backend URL for server-side requests:**

Create `frontend/.env.production`:
```bash
# Public URL for browser (client-side)
NEXT_PUBLIC_BACKEND_URL=https://${{backend.RAILWAY_PUBLIC_DOMAIN}}

# Private URL for server-side requests
BACKEND_INTERNAL_URL=http://backend.railway.internal:${{backend.PORT}}
```

---

## 💾 Database Management

### View Database

1. Click **Postgres service**
2. Click **"Data"** tab
3. Browse tables, run queries

### Connect Locally

Railway provides a **temporary public connection**:

1. Click **Postgres service** → **"Connect"**
2. Copy connection command:
```bash
psql postgresql://postgres:password@containers-us-west-xxx.railway.app:5432/railway
```

Or use **TablePlus / pgAdmin**:
- Host: `containers-us-west-xxx.railway.app`
- Port: 5432
- Database: railway
- User: postgres
- Password: (from Railway variables)

### Backups

**Automatic Backups:**
- Railway Pro: Daily automated backups
- Hobby: No automated backups (but data is safe)

**Manual Export:**
```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Link to project
railway link

# Dump database
railway run pg_dump $DATABASE_URL > backup.sql
```

---

## 📊 Monitoring & Logs

### View Logs

1. Click any service
2. Click **"Deployments"** tab
3. Click latest deployment → **"View Logs"**

**Watch for:**
- Application startup
- Database connections
- API requests
- Errors

### Metrics

Railway shows:
- CPU usage
- Memory usage
- Network traffic
- Request volume

Click service → **"Metrics"** tab

### Alerts

Set up in **"Settings"** → **"Notifications"**:
- Deploy failures
- Resource limits
- Crashes

---

## 🔐 Environment Variables Best Practices

### Use Railway References

**Good:**
```bash
DATABASE_URL=${{Postgres.DATABASE_URL}}
BACKEND_URL=https://${{backend.RAILWAY_PUBLIC_DOMAIN}}
```

**Bad:**
```bash
DATABASE_URL=postgresql://hardcoded...  # Don't do this!
BACKEND_URL=https://backend-prod-xxxx.up.railway.app  # Will break if regenerated
```

### Shared Variables

Create **"Shared Variables"** for common values:

1. Project settings → **"Shared Variables"**
2. Add variables used across services:
```bash
ANTHROPIC_API_KEY=sk-ant-...
ELEVENLABS_API_KEY=sk_...
OPENAI_API_KEY=sk-...
```

3. Services can reference: `${{shared.ANTHROPIC_API_KEY}}`

---

## 💰 Cost Breakdown

### Railway Pricing

**Hobby Plan:** $5/month + usage

**Usage Costs:**
- CPU: $0.000463/vCPU-hour
- Memory: $0.000231/GB-hour
- Network: $0.10/GB (external traffic only)

**Estimated Monthly Costs:**

```
PostgreSQL Database:
- Always running: ~$3-5/month
- 1GB storage: Included
- Internal traffic: Free

Backend Service:
- 512MB RAM, 0.5 vCPU: ~$5-8/month
- 1-2GB network: ~$1-2/month

Frontend Service:
- 256MB RAM, 0.25 vCPU: ~$2-3/month
- Network: Included (mostly CDN)

Total: ~$15-20/month
```

**Tips to Reduce Costs:**
1. Use internal networking (free)
2. Enable audio caching (saves ElevenLabs $)
3. Set sleep schedules for dev environments
4. Monitor usage dashboard

---

## 🚀 Adding InSign App Later

When you're ready to migrate InSign:

### Step 1: Add InSign Database

1. Click **"+ New"** → **"Database"** → **"PostgreSQL"**
2. Name it: `insign-postgres`
3. Import existing data:
```bash
# Export from current DB
pg_dump $OLD_DATABASE_URL > insign-backup.sql

# Import to Railway
railway run psql ${{insign-postgres.DATABASE_URL}} < insign-backup.sql
```

### Step 2: Deploy InSign Backend

1. **"+ New"** → **"GitHub Repo"** → Select InSign repo
2. Configure service
3. Set environment variables:
```bash
DATABASE_URL=${{insign-postgres.DATABASE_URL}}
# ... other InSign vars
```

### Step 3: Connect Services

Demo Copilot can talk to InSign internally:

```bash
# In Demo Copilot backend:
INSIGN_API_URL=http://insign-backend.railway.internal:${{insign-backend.PORT}}
```

**No public internet needed!** All communication via Railway's private network.

---

## 🔧 Troubleshooting

### Build Fails

**Check:**
1. Dockerfile syntax
2. Dependencies in requirements.txt/package.json
3. Build logs for specific error

**Common Issues:**
- Missing file paths in COPY commands
- Playwright browser install failure → check base image
- Out of memory → increase service resources

### Database Connection Error

**Check:**
1. `DATABASE_URL` is set correctly
2. Using `postgresql+asyncpg://` protocol
3. Database service is running
4. Railway private networking is enabled

**Fix:**
```bash
# View actual DATABASE_URL value
railway run echo $DATABASE_URL

# Should start with: postgresql://...
# Update in code to: postgresql+asyncpg://...
```

### Service Won't Start

**Check:**
1. Health check endpoint exists (`/health`)
2. App binds to `0.0.0.0` not `localhost`
3. Uses `$PORT` environment variable
4. Logs for startup errors

**Common fix:**
```python
# Make sure using Railway's PORT
port = int(os.getenv("PORT", 8000))
uvicorn.run(app, host="0.0.0.0", port=port)
```

### WebSocket Connection Fails

**Check:**
1. Frontend using correct backend URL
2. CORS allows frontend domain
3. WebSocket endpoint is `/ws/...`
4. Railway domain supports WebSockets (it does!)

---

## 📝 Deployment Checklist

Before going live:

### Backend
- [ ] All environment variables set
- [ ] Database URL uses asyncpg protocol
- [ ] Health endpoint responds
- [ ] Playwright browsers installed
- [ ] Audio cache directory created
- [ ] CORS configured for frontend domain

### Frontend
- [ ] Backend URL environment variable set
- [ ] Standalone mode enabled in next.config.js
- [ ] Can reach backend API
- [ ] WebSocket connects successfully

### Database
- [ ] Tables initialized
- [ ] Can connect from backend
- [ ] Test data inserted (optional)

### Testing
- [ ] Run a complete demo end-to-end
- [ ] Voice generation works
- [ ] Browser automation works
- [ ] Database saves demo data
- [ ] No errors in logs

---

## 🎯 Railway CLI (Optional)

Install for advanced management:

```bash
# Install
npm i -g @railway/cli

# Login
railway login

# Link to project
railway link

# Run commands in Railway environment
railway run npm start
railway run python manage.py migrate

# View logs
railway logs

# Deploy manually
railway up
```

---

## 📚 Next Steps

1. **Deploy Demo Copilot** (follow this guide)
2. **Test thoroughly** (run multiple demos)
3. **Monitor costs** (check usage dashboard)
4. **Set up custom domain** (optional)
5. **Add InSign app** (when ready)
6. **Set up monitoring** (error tracking, logging)

---

## 🆘 Support

**Railway Documentation:**
- [Docs](https://docs.railway.app)
- [Discord](https://discord.gg/railway)
- [Forum](https://help.railway.app)

**Demo Copilot Issues:**
- Check backend/frontend logs
- Test health endpoints
- Verify environment variables
- Review DEPLOYMENT.md troubleshooting section

---

**You're ready to deploy!** 🚀

Railway makes it simple - just connect GitHub, set variables, and deploy. Everything else happens automatically.
