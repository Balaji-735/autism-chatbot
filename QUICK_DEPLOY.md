# Quick Deployment Guide

Follow these steps to deploy your Autism Chatbot and get a live website link.

## 🚀 Step 1: Deploy Frontend to Vercel (5 minutes)

### Option A: Using Web Interface (Easiest)

1. **Push to GitHub** (if not already):
   ```bash
   git init
   git add .
   git commit -m "Ready for deployment"
   git remote add origin <your-github-repo-url>
   git push -u origin main
   ```

2. **Go to Vercel**:
   - Visit: https://vercel.com/new
   - Click "Sign up" or "Log in" (use GitHub)
   - Click "Add New..." → "Project"
   - Import your GitHub repository

3. **Configure Project**:
   - **Framework Preset**: Next.js (auto-detected)
   - **Root Directory**: `frontend` ⚠️ IMPORTANT!
   - **Build Command**: `npm run build` (auto)
   - **Output Directory**: `.next` (auto)

4. **Environment Variables** (Add after first deploy):
   - Go to Project Settings → Environment Variables
   - Add: `NEXT_PUBLIC_API_URL` = `http://localhost:8000` (we'll update this later)

5. **Deploy**:
   - Click "Deploy"
   - Wait 2-3 minutes
   - **Copy your Vercel URL** (e.g., `https://autism-chatbot.vercel.app`)

### Option B: Using CLI

```bash
cd frontend
vercel login
vercel --prod
```

## 🔧 Step 2: Deploy Backend to Railway (10 minutes)

1. **Go to Railway**:
   - Visit: https://railway.app
   - Sign in with GitHub
   - Click "New Project" → "Deploy from GitHub repo"
   - Select your repository

2. **Configure Service**:
   - Railway auto-detects Python
   - **Start Command**: `uvicorn api_server:app --host 0.0.0.0 --port $PORT`
   - **Environment Variables**:
     - `CORS_ORIGINS`: `https://your-frontend.vercel.app,http://localhost:3000`
     - `OLLAMA_BASE_URL`: (if using remote Ollama, otherwise leave empty for local)

3. **Deploy**:
   - Railway builds automatically
   - **Copy your Railway URL** (e.g., `https://autism-chatbot.up.railway.app`)

4. **Important**: The backend needs Ollama running. Options:
   - **Option 1**: Run Ollama locally and use ngrok to expose it
   - **Option 2**: Deploy Ollama on a separate VPS/server
   - **Option 3**: Use cloud LLM services (OpenAI, HuggingFace) instead

## 🔗 Step 3: Connect Frontend to Backend

1. **Update Vercel Environment Variable**:
   - Go to your Vercel project → Settings → Environment Variables
   - Update `NEXT_PUBLIC_API_URL` = `https://your-railway-url.railway.app`
   - Redeploy (or it auto-redeploys)

2. **Update Backend CORS**:
   - In Railway, add environment variable:
     - `CORS_ORIGINS` = `https://your-vercel-url.vercel.app,http://localhost:3000`
   - Railway will restart automatically

## ✅ Step 4: Verify Deployment

1. Visit your Vercel URL
2. Check health indicator (should show "Backend connected")
3. Try asking a question

## 🎉 You're Live!

Your website is now accessible at: `https://your-app.vercel.app`

## Alternative: Deploy Backend to Render

If Railway doesn't work, try Render:

1. Go to https://render.com
2. New → Web Service
3. Connect GitHub repo
4. Settings:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn api_server:app --host 0.0.0.0 --port $PORT`
5. Add environment variables as above

## Troubleshooting

- **Frontend can't connect to backend**: Check `NEXT_PUBLIC_API_URL` is set correctly
- **CORS errors**: Make sure backend `CORS_ORIGINS` includes your Vercel URL
- **Backend errors**: Check Railway/Render logs
- **Ollama not working**: Consider using cloud LLM services

## Quick Commands Reference

```bash
# Frontend deployment
cd frontend
vercel login
vercel --prod

# Check deployment status
vercel ls

# View logs
vercel logs
```

