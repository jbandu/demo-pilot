# 🔧 Troubleshooting Common Deployment Errors

## Frontend Errors

### 1. `Failed to fetch` or CORS errors
**Symptoms:**
```
Access to fetch at 'https://backend.railway.app/api/demo/start' from origin 'https://frontend.railway.app' has been blocked by CORS policy
```

**Fix:**
- Check `NEXT_PUBLIC_BACKEND_URL` is set in frontend environment variables
- Verify backend CORS settings in `backend/api/main.py` include your frontend URL
- Make sure URLs don't have trailing slashes

### 2. WebSocket connection failed
**Symptoms:**
```
WebSocket connection to 'wss://backend.railway.app/ws/demo/...' failed
```

**Fix:**
- Ensure backend URL in frontend uses `https://` (automatically converts to `wss://`)
- Check backend is running and accessible
- Verify WebSocket endpoint exists: `/ws/demo/{session_id}`

### 3. `/demo/undefined` route error
**Symptoms:**
```
Application error: a client-side exception has occurred
GET /demo/undefined 200
```

**Fix:** ✅ **ALREADY FIXED** in latest commit
- Error handling now validates `session_id` before navigation
- Shows meaningful error message if backend fails

### 4. Hydration errors or React errors
**Symptoms:**
```
Error: Text content does not match server-rendered HTML
Error: Hydration failed because the initial UI does not match
```

**Fix:**
- Clear browser cache and hard reload (Ctrl+Shift+R)
- Rebuild frontend with `npm run build`
- Check for client-only code in server components

## Backend Errors

### 1. Missing environment variables
**Symptoms:**
```
KeyError: 'ANTHROPIC_API_KEY'
Environment variable not found
```

**Fix:**
- Set all required environment variables in deployment platform:
  - `ANTHROPIC_API_KEY`
  - `ELEVENLABS_API_KEY`
  - `OPENAI_API_KEY`
  - `DATABASE_URL` (or `SKIP_DATABASE=true`)

### 2. Database connection errors
**Symptoms:**
```
Could not connect to database
asyncpg.exceptions.InvalidPasswordError
```

**Fix:**
- Ensure `DATABASE_URL` uses `postgresql+asyncpg://` protocol
- Check database credentials are correct
- Verify database accepts connections from your deployment IP
- Or set `SKIP_DATABASE=true` to run without database

### 3. Playwright browser errors
**Symptoms:**
```
playwright._impl._api_types.Error: Browser closed unexpectedly
Executable doesn't exist at /root/.cache/ms-playwright
```

**Fix:**
- Ensure Dockerfile installs Playwright browsers:
  ```dockerfile
  RUN playwright install --with-deps chromium
  ```
- Increase memory allocation in Railway/Render settings
- Check logs for OOM (out of memory) errors

### 4. ElevenLabs API errors
**Symptoms:**
```
ElevenLabs API error: 401 Unauthorized
Voice ID not found
```

**Fix:**
- Verify `ELEVENLABS_API_KEY` is set correctly
- Check API quota at https://elevenlabs.io/app/usage
- If using custom voice, ensure `ELEVENLABS_VOICE_ID` is valid

## Build Errors

### 1. Next.js font loading errors (Google Fonts)
**Symptoms:**
```
Failed to fetch font `Inter` from Google Fonts
NextFontError
```

**Fix:**
- This is expected in restricted networks (local builds)
- **Production builds should work fine** - fonts are cached during build
- If failing in production, check network access from build server

### 2. Standalone build warning
**Symptoms:**
```
⚠ "next start" does not work with "output: standalone" configuration
```

**Fix:** ✅ **ALREADY FIXED** in latest commit
- `package.json` now uses `node server.js` instead of `next start`
- Dockerfile already configured correctly

### 3. Module not found errors
**Symptoms:**
```
Module not found: Can't resolve '@/components/ui/button'
Error: Cannot find module 'next'
```

**Fix:**
- Run `npm install` in frontend directory
- Check `tsconfig.json` has correct path aliases
- Verify all imports use correct paths

## Deployment Platform Issues

### Railway

**Build fails:**
- Check service is using correct Dockerfile
- Verify root directory is set (`/frontend` or `/backend`)
- Increase build timeout in settings

**Service crashes:**
- Check logs for OOM errors → Increase memory
- Verify health check endpoint works
- Check environment variables are set

### Render

**Service won't start:**
- Ensure Docker command is: `npm start` or correct entrypoint
- Check port matches `PORT` environment variable (Render sets this automatically)
- Verify free tier limits aren't exceeded

## How to Debug

### 1. Check Deployment Logs
```bash
# Railway CLI
railway logs --service=backend
railway logs --service=frontend

# Check build logs in Railway dashboard
```

### 2. Test Backend Health
```bash
curl https://your-backend.railway.app/health

# Should return:
{"status":"healthy","version":"1.0.0"}
```

### 3. Test Frontend Build Locally
```bash
cd frontend
npm install
npm run build
npm start
```

### 4. Test Backend Locally
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your API keys
python -m uvicorn api.main:app --host 0.0.0.0 --port 8000
```

### 5. Check Browser Console
- Open DevTools (F12)
- Console tab for JavaScript errors
- Network tab for failed API calls
- Sources tab to set breakpoints

## Still Having Issues?

**Provide these details:**
1. **Exact error messages** from browser console
2. **Failed network requests** from Network tab (URLs, status codes)
3. **Deployment platform logs** (backend and frontend)
4. **Environment** (Railway, Render, etc.)
5. **What actions trigger the error** (page load, button click, etc.)

This will help diagnose the specific issue quickly.
