# Troubleshooting Guide

## "Not Found" Error for Benchmark Endpoints

If you're seeing "Failed to run baseline benchmark: Not Found", follow these steps:

### 1. Install Missing Dependencies
```bash
pip install -r requirements.txt
```

Make sure `psutil` is installed:
```bash
pip install psutil
```

### 2. Restart the Backend Server

The backend server needs to be restarted to register the new optimization endpoints:

1. **Stop the current server** (if running):
   - Press `Ctrl+C` in the terminal where the server is running

2. **Start the server again**:
   ```bash
   python api_server.py
   ```

   You should see output like:
   ```
   INFO:     Started server process
   INFO:     Uvicorn running on http://0.0.0.0:8000
   ```

### 3. Verify Endpoints are Available

You can check if the endpoints are registered by visiting:
- `http://localhost:8000/docs` - FastAPI interactive docs
- Look for `/api/benchmark/baseline`, `/api/benchmark/quantization`, `/api/benchmark/pruning`

### 4. Check Server Logs

When you click "Run" on a benchmark, check the backend server terminal for:
- Any error messages
- Request logs showing the endpoint was hit
- Processing messages

### 5. Verify CORS Settings

Make sure the frontend URL is allowed in CORS:
- Check `api_server.py` line 15: `allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"]`

### 6. Test Endpoint Directly

You can test the endpoint directly using curl or Postman:

```bash
curl -X POST http://localhost:8000/api/benchmark/baseline \
  -H "Content-Type: application/json" \
  -d "{\"test_queries\": [\"What is autism?\"]}"
```

Expected response:
```json
{
  "technique": "baseline",
  "model_name": "mistral",
  "metrics": {
    "response_time": 2.5,
    "memory_usage_mb": 512.0,
    ...
  }
}
```

## Common Issues

### Issue: "ModuleNotFoundError: No module named 'psutil'"
**Solution**: Run `pip install psutil`

### Issue: "Connection refused" or "Failed to fetch"
**Solution**: 
- Make sure the backend server is running on port 8000
- Check if another process is using port 8000
- Verify `NEXT_PUBLIC_API_URL` in frontend `.env.local` matches backend URL

### Issue: "CORS error"
**Solution**: 
- Verify frontend is running on `http://localhost:3000`
- Check CORS settings in `api_server.py`

### Issue: Benchmark takes too long or times out
**Solution**:
- Benchmarks run 3 iterations, which can take 30-60 seconds
- Make sure Ollama is running and the model is loaded
- Check system resources (RAM, CPU)

## Quick Start Checklist

- [ ] Backend dependencies installed (`pip install -r requirements.txt`)
- [ ] Backend server running (`python api_server.py`)
- [ ] Frontend dependencies installed (`cd frontend && npm install`)
- [ ] Frontend server running (`npm run dev`)
- [ ] Ollama running with `mistral` model available
- [ ] Database populated (`python populate_database.py`)

## Still Having Issues?

1. Check browser console (F12) for detailed error messages
2. Check backend server logs for errors
3. Verify all services are running:
   - Backend API: `http://localhost:8000`
   - Frontend: `http://localhost:3000`
   - Ollama: Should be running locally


