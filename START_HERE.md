# Quick Start Guide

## Step 1: Install Ollama Models

Make sure Ollama is installed and pull the required models:

```bash
ollama pull mistral
ollama pull nomic-embed-text
```

## Step 2: Set Up Backend

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Populate the database (first time only):
```bash
python populate_database.py
```

3. Start the backend server:
```bash
python api_server.py
```

The backend will run on `http://localhost:8000`

## Step 3: Set Up Frontend

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

The frontend will run on `http://localhost:3000`

## Step 4: Use the Application

1. Open `http://localhost:3000` in your browser
2. Check that the backend connection indicator shows "Backend connected" (green)
3. Start asking questions about the documents in the `data/` directory

## Troubleshooting

- **Backend not connecting**: Make sure the FastAPI server is running on port 8000
- **Ollama errors**: Ensure Ollama is running and the models are pulled
- **Database errors**: Run `python populate_database.py` to initialize the database
- **Port conflicts**: Change ports in `api_server.py` (backend) or `.env.local` (frontend)

## Production Deployment

### Backend
- Use a production ASGI server like `gunicorn` with `uvicorn` workers
- Set up environment variables for configuration
- Use a reverse proxy (nginx) for production

### Frontend
- Build: `npm run build`
- Start: `npm start`
- Deploy to Vercel, Netlify, or any Node.js hosting platform


