# Deployment Guide

This guide will help you deploy the Autism Chatbot to production.

## Prerequisites

- GitHub account
- Vercel account (for frontend) - [Sign up here](https://vercel.com)
- Railway account (for backend) - [Sign up here](https://railway.app) OR Render account - [Sign up here](https://render.com)

## Step 1: Deploy Backend (FastAPI)

### Option A: Deploy to Railway (Recommended)

1. **Push your code to GitHub** (if not already done):
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin <your-github-repo-url>
   git push -u origin main
   ```

2. **Go to Railway**:
   - Visit [railway.app](https://railway.app)
   - Sign in with GitHub
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository

3. **Configure the service**:
   - Railway will auto-detect Python
   - Set the start command: `uvicorn api_server:app --host 0.0.0.0 --port $PORT`
   - Add environment variables (if needed):
     - `PORT` (auto-set by Railway)
     - `OLLAMA_BASE_URL` (if using remote Ollama instance)

4. **Deploy**:
   - Railway will automatically build and deploy
   - Copy the generated URL (e.g., `https://your-app.railway.app`)

### Option B: Deploy to Render

1. **Go to Render Dashboard**:
   - Visit [render.com](https://render.com)
   - Sign in with GitHub
   - Click "New +" → "Web Service"
   - Connect your GitHub repository

2. **Configure the service**:
   - Name: `autism-chatbot-backend`
   - Environment: `Python 3`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn api_server:app --host 0.0.0.0 --port $PORT`
   - Add environment variables as needed

3. **Deploy**:
   - Render will build and deploy automatically
   - Copy the generated URL

### Important Notes for Backend:

⚠️ **Ollama Requirement**: The backend requires Ollama to be running. You have two options:

1. **Local Ollama** (for development/testing):
   - Install Ollama on your local machine
   - Run `ollama pull mistral` and `ollama pull nomic-embed-text`
   - The backend will connect to `http://localhost:11434` by default

2. **Remote Ollama** (for production):
   - Deploy Ollama on a separate server/VPS
   - Set `OLLAMA_BASE_URL` environment variable to point to your Ollama instance
   - Or use a cloud Ollama service

3. **Alternative**: Replace Ollama with cloud services:
   - Use OpenAI embeddings and GPT models
   - Use HuggingFace models
   - Modify `get_embedding_function.py` and `api_server.py` accordingly

## Step 2: Deploy Frontend (Next.js)

### Deploy to Vercel

1. **Go to Vercel**:
   - Visit [vercel.com](https://vercel.com)
   - Sign in with GitHub
   - Click "Add New..." → "Project"
   - Import your GitHub repository

2. **Configure the project**:
   - Framework Preset: **Next.js** (auto-detected)
   - Root Directory: `frontend`
   - Build Command: `npm run build` (auto-detected)
   - Output Directory: `.next` (auto-detected)

3. **Add Environment Variables**:
   - Click "Environment Variables"
   - Add: `NEXT_PUBLIC_API_URL` = `https://your-backend-url.railway.app` (or your Render URL)
   - Make sure it's available for Production, Preview, and Development

4. **Deploy**:
   - Click "Deploy"
   - Vercel will build and deploy automatically
   - You'll get a URL like `https://your-app.vercel.app`

## Step 3: Update CORS Settings

After deploying, update the backend CORS settings in `api_server.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://your-frontend.vercel.app",  # Add your Vercel URL
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Then redeploy the backend.

## Step 4: Verify Deployment

1. Visit your frontend URL (Vercel)
2. Check the health indicator - it should show "Backend connected"
3. Try asking a question to verify everything works

## Troubleshooting

### Backend Issues

- **Ollama connection errors**: Make sure Ollama is running and accessible
- **Database errors**: Ensure the `chroma/` directory is included in deployment
- **Port issues**: Use `$PORT` environment variable (Railway/Render set this automatically)

### Frontend Issues

- **API connection errors**: Verify `NEXT_PUBLIC_API_URL` is set correctly
- **CORS errors**: Add your frontend URL to backend CORS origins
- **Build errors**: Check that all dependencies are in `package.json`

## Quick Deploy Commands

### Railway CLI (Alternative)
```bash
npm i -g @railway/cli
railway login
railway init
railway up
```

### Vercel CLI (Alternative)
```bash
npm i -g vercel
cd frontend
vercel
```

## Production Checklist

- [ ] Backend deployed and accessible
- [ ] Frontend deployed and accessible
- [ ] Environment variables configured
- [ ] CORS settings updated
- [ ] Health check endpoint working
- [ ] Test query working
- [ ] PDF serving working (if applicable)
- [ ] Database populated with documents

