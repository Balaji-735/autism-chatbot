# Deploy Backend Now - Simple 3-Step Guide

I've prepared everything for you. Here's the fastest way to deploy:

## Step 1: Push to GitHub (2 minutes)

```bash
git add .
git commit -m "Ready for deployment"
git remote add origin <your-github-repo-url>  # If not already added
git push -u origin master
```

## Step 2: Deploy to Render (3 minutes)

1. **Go to**: https://dashboard.render.com
2. **Sign in** with GitHub
3. **Click**: "New +" → "Blueprint"
4. **Select**: Your GitHub repository
5. **Click**: "Apply"

**That's it!** Render will:
- Auto-detect `render.yaml`
- Build and deploy automatically
- Give you a URL like: `https://autism-chatbot-backend.onrender.com`

## Step 3: Connect Frontend (2 minutes)

1. **Copy your Render backend URL**

2. **Update Vercel**:
   - Go to: https://vercel.com/dashboard
   - Select: `frontend` project
   - Go to: Settings → Environment Variables
   - Update: `NEXT_PUBLIC_API_URL` = `https://autism-chatbot-backend.onrender.com`
   - Save (auto-redeploys)

3. **Update Backend CORS** (in Render):
   - Go to: Render Dashboard → Your Service → Environment
   - Update: `CORS_ORIGINS` = `https://frontend-30f3yggta-balajiajai0407-6612s-projects.vercel.app`
   - Save

## Done! 🎉

Your full-stack app is now live:
- **Frontend**: https://frontend-30f3yggta-balajiajai0407-6612s-projects.vercel.app
- **Backend**: https://autism-chatbot-backend.onrender.com (after Step 2)

## Important Note

⚠️ The backend requires Ollama to function. You'll need to:
- Deploy Ollama separately, OR
- Use cloud LLM services (OpenAI/HuggingFace) instead

The deployment will work, but queries won't function until Ollama is accessible.

