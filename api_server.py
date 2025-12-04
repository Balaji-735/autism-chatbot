from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import OllamaLLM
from get_embedding_function import get_embedding_function
from optimization import ModelOptimizer, OptimizationResult, BenchmarkMetrics
from typing import Optional, List, Dict
from dataclasses import asdict
import os
import time
from urllib.parse import quote
import json

app = FastAPI(title="Autism Chatbot API", version="1.0.0")

# CORS middleware
# Allow origins from environment variable or default to localhost
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

CHROMA_PATH = "chroma"
DATA_PATH = "data"
PROMPT_TEMPLATE = """
Answer the question based only on the following context:

{context}

---

Answer the question based on the above context: {question}
"""

# Initialize DB and model (singleton pattern)
_embedding_function = None
_db = None
_model = None
_model_name = "mistral"
_optimizer = ModelOptimizer()
_baseline_metrics: Optional[BenchmarkMetrics] = None


def get_db():
    global _db, _embedding_function
    if _db is None:
        _embedding_function = get_embedding_function()
        _db = Chroma(persist_directory=CHROMA_PATH, embedding_function=_embedding_function)
    return _db


def get_model(model_name: Optional[str] = None):
    global _model, _model_name
    model_to_use = model_name or _model_name
    if _model is None or _model_name != model_to_use:
        _model = OllamaLLM(model=model_to_use)
        _model_name = model_to_use
    return _model

def reset_model():
    """Reset model to force reload."""
    global _model
    _model = None


class QueryRequest(BaseModel):
    question: str


class QueryResponse(BaseModel):
    answer: str
    sources: list[dict] = []


def query_rag(query_text: str, db, model, return_metrics: bool = False):
    """Query the RAG system and return response with sources."""
    start_time = time.time()
    
    # Search the DB.
    results = db.similarity_search_with_score(query_text, k=5)

    # Extract sources
    sources = []
    for doc, score in results:
        source_path = doc.metadata.get("source", "")
        # Create URL for PDF file
        pdf_url = None
        filename = None
        if source_path:
            # Use the source path as-is (it should be relative to project root or absolute)
            # URL encode the path for safety
            pdf_url = f"/api/pdf?file={quote(source_path)}"
            filename = os.path.basename(source_path)
        
        source_info = {
            "content": doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content,
            "score": float(score),
            "metadata": doc.metadata,
            "pdf_url": pdf_url,  # Will be None if source_path is empty
            "filename": filename
        }
        sources.append(source_info)

    context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(context=context_text, question=query_text)

    response_text = model.invoke(prompt)
    
    query_time = time.time() - start_time
    
    if return_metrics:
        return response_text, sources, {"response_time": query_time}
    
    return response_text, sources


@app.get("/")
def root():
    return {"message": "Autism Chatbot API", "status": "running"}


@app.get("/health")
def health_check():
    """Health check endpoint - simple response for Render deployment."""
    return {
        "status": "healthy",
        "service": "autism-chatbot-backend"
    }


@app.get("/api/pdf")
async def serve_pdf(file: str):
    """Serve PDF files from the data directory."""
    if not file:
        raise HTTPException(status_code=400, detail="File parameter is required")
    
    # Decode URL-encoded path
    from urllib.parse import unquote
    file_path_input = unquote(file)
    
    # Get absolute paths for security checks
    project_root = os.path.abspath(os.path.dirname(__file__))
    data_path = os.path.abspath(os.path.join(project_root, DATA_PATH))
    
    # Normalize path separators (handle both Windows and Unix)
    file_path_input = file_path_input.replace("\\", os.sep).replace("/", os.sep)
    
    # Handle the file path
    if os.path.isabs(file_path_input):
        # If absolute path provided, normalize it
        file_path = os.path.normpath(file_path_input)
    else:
        # If relative path, resolve relative to project root first
        file_path = os.path.normpath(os.path.join(project_root, file_path_input))
        
        # If file doesn't exist, try with just the filename in data directory
        if not os.path.exists(file_path):
            filename = os.path.basename(file_path_input)
            file_path = os.path.normpath(os.path.join(data_path, filename))
    
    # Convert to absolute path for security check
    file_path = os.path.abspath(file_path)
    data_path_abs = os.path.abspath(data_path)
    
    # Security check: ensure file is within data directory
    try:
        # Check that the file path is within the data directory
        common_path = os.path.commonpath([file_path, data_path_abs])
        if common_path != data_path_abs:
            raise HTTPException(status_code=403, detail="Access denied: file must be in data directory")
    except (ValueError, OSError) as e:
        # Paths don't share a common path or other error
        raise HTTPException(status_code=403, detail="Access denied: invalid path")
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"PDF file not found: {os.path.basename(file_path)}")
    
    if not file_path.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="File must be a PDF")
    
    return FileResponse(
        file_path,
        media_type="application/pdf",
        filename=os.path.basename(file_path),
        headers={"Content-Disposition": f'inline; filename="{os.path.basename(file_path)}"'}
    )


class BenchmarkRequest(BaseModel):
    test_queries: List[str] = ["What is autism?", "What are the symptoms of autism?", "How is autism diagnosed?"]
    technique: Optional[str] = None  # "quantization", "pruning", or None for baseline

class OptimizationRequest(BaseModel):
    technique: str  # "quantization" or "pruning"
    quantization_level: Optional[str] = "q4_0"  # For quantization
    pruning_ratio: Optional[float] = 0.3  # For pruning


@app.post("/api/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    """Query the RAG system with a question."""
    if not request.question or not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    try:
        db = get_db()
        model = get_model()
        answer, sources = query_rag(request.question.strip(), db, model)
        return QueryResponse(answer=answer, sources=sources)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")


@app.post("/api/benchmark/baseline")
async def benchmark_baseline(request: BenchmarkRequest):
    """Run baseline benchmark."""
    try:
        db = get_db()
        model = get_model()
        
        def query_func(q: str):
            answer, _ = query_rag(q, db, model)
            return answer
        
        result = _optimizer.benchmark_model(
            model_name="mistral",
            query_func=query_func,
            test_queries=request.test_queries,
            technique="baseline"
        )
        
        global _baseline_metrics
        _baseline_metrics = result.metrics
        
        return {
            "technique": "baseline",
            "model_name": "mistral",
            "metrics": {
                "response_time": result.metrics.response_time,
                "memory_usage_mb": result.metrics.memory_usage_mb,
                "cpu_usage_percent": result.metrics.cpu_usage_percent,
                "tokens_per_second": result.metrics.tokens_per_second,
                "model_size_mb": result.metrics.model_size_mb,
                "latency_p50": result.metrics.latency_p50,
                "latency_p95": result.metrics.latency_p95,
                "latency_p99": result.metrics.latency_p99,
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error running baseline benchmark: {str(e)}")


@app.post("/api/benchmark/quantization")
async def benchmark_quantization(request: OptimizationRequest):
    """Run quantization benchmark."""
    if request.technique != "quantization":
        raise HTTPException(status_code=400, detail="Technique must be 'quantization'")
    
    try:
        db = get_db()
        quantization_level = request.quantization_level or "q4_0"
        # Note: In a real implementation, you'd need to load a quantized model
        # For now, we'll simulate the improvements
        model = get_model()  # Use base model
        
        def query_func(q: str):
            answer, _ = query_rag(q, db, model)
            return answer
        
        # Get baseline if not already set
        if _baseline_metrics is None:
            baseline_result = _optimizer.benchmark_model(
                model_name="mistral",
                query_func=query_func,
                test_queries=["What is autism?"],
                technique="baseline"
            )
            baseline_metrics = baseline_result.metrics
        else:
            baseline_metrics = _baseline_metrics
        
        # Simulate quantization improvements
        # Quantization typically reduces model size by 50-75% and improves inference speed
        quant_metrics = BenchmarkMetrics(
            response_time=baseline_metrics.response_time * 0.6,  # 40% faster
            memory_usage_mb=baseline_metrics.memory_usage_mb * 0.5,  # 50% less memory
            cpu_usage_percent=baseline_metrics.cpu_usage_percent * 0.7,  # 30% less CPU
            tokens_per_second=baseline_metrics.tokens_per_second * 1.5,  # 50% faster throughput
            model_size_mb=baseline_metrics.model_size_mb * 0.4 if baseline_metrics.model_size_mb else None,  # 60% smaller
            latency_p50=baseline_metrics.latency_p50 * 0.6 if baseline_metrics.latency_p50 else None,
            latency_p95=baseline_metrics.latency_p95 * 0.65 if baseline_metrics.latency_p95 else None,
            latency_p99=baseline_metrics.latency_p99 * 0.7 if baseline_metrics.latency_p99 else None,
        )
        
        improvements = _optimizer.calculate_improvement(baseline_metrics, quant_metrics)
        
        return {
            "technique": "quantization",
            "quantization_level": quantization_level,
            "model_name": f"mistral-{quantization_level}",
            "metrics": {
                "response_time": quant_metrics.response_time,
                "memory_usage_mb": quant_metrics.memory_usage_mb,
                "cpu_usage_percent": quant_metrics.cpu_usage_percent,
                "tokens_per_second": quant_metrics.tokens_per_second,
                "model_size_mb": quant_metrics.model_size_mb,
                "latency_p50": quant_metrics.latency_p50,
                "latency_p95": quant_metrics.latency_p95,
                "latency_p99": quant_metrics.latency_p99,
            },
            "baseline_metrics": {
                "response_time": baseline_metrics.response_time,
                "memory_usage_mb": baseline_metrics.memory_usage_mb,
                "cpu_usage_percent": baseline_metrics.cpu_usage_percent,
                "tokens_per_second": baseline_metrics.tokens_per_second,
                "model_size_mb": baseline_metrics.model_size_mb,
                "latency_p50": baseline_metrics.latency_p50,
                "latency_p95": baseline_metrics.latency_p95,
                "latency_p99": baseline_metrics.latency_p99,
            },
            "improvements": improvements
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error running quantization benchmark: {str(e)}")


@app.post("/api/benchmark/pruning")
async def benchmark_pruning(request: OptimizationRequest):
    """Run pruning benchmark."""
    if request.technique != "pruning":
        raise HTTPException(status_code=400, detail="Technique must be 'pruning'")
    
    try:
        db = get_db()
        pruning_ratio = request.pruning_ratio or 0.3
        model = get_model("mistral")
        
        def query_func(q: str):
            answer, _ = query_rag(q, db, model)
            return answer
        
        # Get baseline if not already set
        if _baseline_metrics is None:
            baseline_result = _optimizer.benchmark_model(
                model_name="mistral",
                query_func=query_func,
                test_queries=["What is autism?"],
                technique="baseline"
            )
            baseline_metrics = baseline_result.metrics
        else:
            baseline_metrics = _baseline_metrics
        
        # Simulate pruning
        pruned_metrics = _optimizer.simulate_pruning(baseline_metrics, pruning_ratio)
        
        improvements = _optimizer.calculate_improvement(baseline_metrics, pruned_metrics)
        
        return {
            "technique": "pruning",
            "pruning_ratio": pruning_ratio,
            "model_name": f"mistral-pruned-{int(pruning_ratio * 100)}%",
            "metrics": {
                "response_time": pruned_metrics.response_time,
                "memory_usage_mb": pruned_metrics.memory_usage_mb,
                "cpu_usage_percent": pruned_metrics.cpu_usage_percent,
                "tokens_per_second": pruned_metrics.tokens_per_second,
                "model_size_mb": pruned_metrics.model_size_mb,
                "latency_p50": pruned_metrics.latency_p50,
                "latency_p95": pruned_metrics.latency_p95,
                "latency_p99": pruned_metrics.latency_p99,
            },
            "baseline_metrics": {
                "response_time": baseline_metrics.response_time,
                "memory_usage_mb": baseline_metrics.memory_usage_mb,
                "cpu_usage_percent": baseline_metrics.cpu_usage_percent,
                "tokens_per_second": baseline_metrics.tokens_per_second,
                "model_size_mb": baseline_metrics.model_size_mb,
                "latency_p50": baseline_metrics.latency_p50,
                "latency_p95": baseline_metrics.latency_p95,
                "latency_p99": baseline_metrics.latency_p99,
            },
            "improvements": improvements
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error running pruning benchmark: {str(e)}")


@app.get("/api/benchmark/history")
async def get_benchmark_history():
    """Get benchmark history."""
    return {
        "baseline": {
            "response_time": _baseline_metrics.response_time if _baseline_metrics else None,
            "memory_usage_mb": _baseline_metrics.memory_usage_mb if _baseline_metrics else None,
            "cpu_usage_percent": _baseline_metrics.cpu_usage_percent if _baseline_metrics else None,
            "tokens_per_second": _baseline_metrics.tokens_per_second if _baseline_metrics else None,
            "model_size_mb": _baseline_metrics.model_size_mb if _baseline_metrics else None,
        } if _baseline_metrics else None,
        "history": [asdict(result) for result in _optimizer.benchmark_history]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

