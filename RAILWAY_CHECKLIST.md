# ✅ Railway Deployment Checklist

Quick reference guide for deploying Demo Copilot to Railway.app

## 📋 Pre-Deployment

### API Keys Ready
- [ ] Anthropic API key (Claude)
- [ ] ElevenLabs API key + Voice ID
- [ ] OpenAI API key (Whisper)

### InSign Demo Credentials
- [ ] Demo URL
- [ ] Demo email
- [ ] Demo password

---

## 🚀 Deployment Steps

### 1. Create Railway Project
- [ ] Sign up at [railway.app](https://railway.app)
- [ ] Connect GitHub account
- [ ] Create new project from `demo-pilot` repo

### 2. Add PostgreSQL Database
- [ ] Click "+ New" → "Database" → "PostgreSQL"
- [ ] Note the auto-generated DATABASE_URL

### 3. Deploy Backend Service
- [ ] "+ New" → Select `demo-pilot` repo → "backend"
- [ ] Verify Dockerfile detected: `backend/Dockerfile`
- [ ] Wait for build to complete

### 4. Configure Backend Variables
```bash
ANTHROPIC_API_KEY=sk-ant-...
ELEVENLABS_API_KEY=sk_...
ELEVENLABS_VOICE_ID=your_voice_id
OPENAI_API_KEY=sk-...
DATABASE_URL=${{Postgres.DATABASE_URL}}  # Auto-filled
SKIP_DATABASE=false
INSIGN_DEMO_URL=https://demo.insign.io
INSIGN_DEMO_EMAIL=demo@example.com
INSIGN_DEMO_PASSWORD=your_password
PLAY_AUDIO_LOCALLY=false
AUDIO_CACHE_DIR=/app/audio_cache
```

### 5. Deploy Frontend Service
- [ ] "+ New" → Select `demo-pilot` repo → "frontend"
- [ ] Verify Dockerfile detected: `frontend/Dockerfile`
- [ ] Wait for build to complete

### 6. Configure Frontend Variables
```bash
NEXT_PUBLIC_BACKEND_URL=https://${{backend.RAILWAY_PUBLIC_DOMAIN}}
```

### 7. Enable Public Domains
- [ ] Backend → Settings → Networking → "Generate Domain"
- [ ] Frontend → Settings → Networking → "Generate Domain"
- [ ] Copy frontend URL (this is your demo URL!)

---

## 🧪 Testing

### Health Checks
```bash
# Backend health
curl https://your-backend.railway.app/health

# Expected: {"status": "healthy", "version": "1.0.0"}
```

### Database Connection
```bash
# Check database
curl https://your-backend.railway.app/api/health/database

# Expected: {"database": "connected"}
```

### Run Demo
- [ ] Visit frontend URL
- [ ] Click "Start Demo"
- [ ] Select demo type (InSign)
- [ ] Verify:
  - [ ] Browser opens
  - [ ] Voice narration plays
  - [ ] Actions execute
  - [ ] No errors in Railway logs

---

## 🔍 Verify Everything

### Backend Service
- [ ] Status: Running (green)
- [ ] Health check passing
- [ ] Logs show: "Application startup complete"
- [ ] Logs show: "Database initialized successfully"
- [ ] Logs show: "ElevenLabs voice engine initialized"

### Frontend Service
- [ ] Status: Running (green)
- [ ] Can load homepage
- [ ] Can start demo
- [ ] WebSocket connects

### Database
- [ ] Status: Running (green)
- [ ] Tables created (check Data tab)
- [ ] Backend can connect

---

## 📊 Monitor First 24 Hours

### Check Every Few Hours
- [ ] Any deployment errors?
- [ ] Any service crashes?
- [ ] Memory usage normal? (backend ~500MB, frontend ~256MB)
- [ ] CPU usage normal? (< 50% average)

### Run Test Demos
- [ ] Run 3-5 complete demos
- [ ] Verify audio caching working (check logs)
- [ ] Verify database saving demos
- [ ] Check ElevenLabs quota

### Cost Monitoring
- [ ] Check Railway usage dashboard
- [ ] Estimated monthly cost reasonable? (~$15-25)
- [ ] No unexpected spikes?

---

## 🐛 Troubleshooting Quick Fixes

### Service Won't Start
```bash
# Check logs for:
- Port binding (should use $PORT)
- Missing environment variables
- Dockerfile errors
```

### Database Connection Failed
```bash
# Verify:
1. DATABASE_URL is set
2. Postgres service is running
3. Check backend logs for connection error
4. main.py has fix_database_url() function
```

### WebSocket Won't Connect
```bash
# Check:
1. CORS allows frontend domain
2. Frontend has correct BACKEND_URL
3. Backend WebSocket endpoint exists
4. Railway domains support WSS (they do!)
```

### Audio Not Working
```bash
# Verify:
1. ELEVENLABS_API_KEY is correct
2. ELEVENLABS_VOICE_ID is valid
3. Check quota at elevenlabs.io
4. Backend logs show "Audio cached to..."
```

---

## 🎯 Optional: Custom Domain

### Add Custom Domain (e.g., demo.yourcompany.com)

**Frontend:**
1. Railway → Frontend service → Settings → Networking
2. Click "Custom Domain"
3. Enter: `demo.yourcompany.com`
4. Add CNAME record in your DNS:
   ```
   demo.yourcompany.com → frontend-production-xxxx.up.railway.app
   ```
5. Wait for SSL certificate (automatic)

**Backend:**
1. Railway → Backend service → Settings → Networking
2. Click "Custom Domain"
3. Enter: `api.yourcompany.com`
4. Add CNAME record:
   ```
   api.yourcompany.com → backend-production-xxxx.up.railway.app
   ```

**Update Frontend Variable:**
```bash
NEXT_PUBLIC_BACKEND_URL=https://api.yourcompany.com
```

---

## 🔄 Future: Add InSign App

When ready to migrate InSign to Railway:

### 1. Add InSign Database
- [ ] "+ New" → "Database" → "PostgreSQL"
- [ ] Name it: `insign-postgres`

### 2. Migrate Data
```bash
# Export from old DB
pg_dump $OLD_DB_URL > insign-backup.sql

# Import to Railway
railway run psql ${{insign-postgres.DATABASE_URL}} < insign-backup.sql
```

### 3. Deploy InSign Backend
- [ ] "+ New" → GitHub repo (InSign)
- [ ] Configure environment variables
- [ ] Set DATABASE_URL=${{insign-postgres.DATABASE_URL}}

### 4. Connect to Demo Copilot
```bash
# In Demo Copilot backend variables:
INSIGN_API_URL=http://insign-backend.railway.internal:${{insign-backend.PORT}}
INSIGN_DEMO_URL=https://${{insign-frontend.RAILWAY_PUBLIC_DOMAIN}}
```

---

## 📞 Support

### Railway Issues
- Check: [Railway Status](https://status.railway.app)
- Docs: [docs.railway.app](https://docs.railway.app)
- Discord: [discord.gg/railway](https://discord.gg/railway)

### Demo Copilot Issues
- Check deployment logs
- Review RAILWAY.md for detailed troubleshooting
- Verify all environment variables set correctly

---

## ✨ Success Criteria

Your deployment is successful when:

✅ **All services running** (green status)
✅ **Health checks passing** (backend /health returns 200)
✅ **Database connected** (tables created, queries work)
✅ **Demo runs end-to-end** (browser + voice + database)
✅ **No errors in logs** (or only minor warnings)
✅ **Audio caching works** (logs show "Using disk-cached audio")
✅ **Cost is reasonable** (~$15-25/month projected)

---

**You're deployed!** 🎉

Monitor for 24-48 hours, run a few test demos, and you're ready for production traffic.
