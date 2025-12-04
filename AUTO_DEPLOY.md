# Automatic Backend Deployment

I've set up deployment configurations for multiple platforms. Choose one:

## Option 1: Render (Free Tier - Easiest)

1. **Go to Render Dashboard**: https://dashboard.render.com
2. **Sign in** with GitHub
3. **Click "New +"** → **"Blueprint"**
4. **Connect your GitHub repository**
5. **Select the repository** containing this project
6. Render will auto-detect `render.yaml` and deploy automatically!

**That's it!** Render will:
- Build your Python app
- Deploy it
- Give you a URL like `https://autism-chatbot-backend.onrender.com`

## Option 2: Railway (Free Tier - Requires GitHub)

1. **Push code to GitHub** (if not already):
   ```bash
   git init
   git add .
   git commit -m "Ready for deployment"
   git remote add origin <your-github-repo-url>
   git push -u origin main
   ```

2. **Go to Railway**: https://railway.app
3. **Sign in** with GitHub
4. **New Project** → **Deploy from GitHub repo**
5. **Select your repository**
6. Railway will auto-detect and deploy!

## Option 3: Manual Railway Setup

If Railway doesn't auto-detect:

1. In Railway project, click **"+ New"** → **"Empty Service"**
2. Click the service → **"Settings"**
3. **Connect GitHub Repo**
4. **Settings** → **Deploy**:
   - **Start Command**: `uvicorn api_server:app --host 0.0.0.0 --port $PORT`
5. **Variables** tab:
   - Add: `CORS_ORIGINS` = `https://frontend-30f3yggta-balajiajai0407-6612s-projects.vercel.app`
6. Railway will deploy automatically!

## After Deployment

1. **Copy your backend URL** (e.g., `https://autism-chatbot-backend.onrender.com`)

2. **Update Vercel Environment Variable**:
   - Go to: https://vercel.com/dashboard
   - Select your project → **Settings** → **Environment Variables**
   - Update `NEXT_PUBLIC_API_URL` = `https://your-backend-url.onrender.com`
   - Save (auto-redeploys)

3. **Update Backend CORS** (if needed):
   - In Render/Railway dashboard
   - Update `CORS_ORIGINS` environment variable
   - Include your Vercel URL

## Important Notes

⚠️ **Ollama Requirement**: The backend needs Ollama running. Options:

1. **Use Remote Ollama**: Deploy Ollama separately and set `OLLAMA_BASE_URL`
2. **Use Cloud LLM**: Replace Ollama with OpenAI/HuggingFace (requires code changes)
3. **Local Development**: Keep Ollama local for now

The deployment will work, but queries won't function until Ollama is accessible.

