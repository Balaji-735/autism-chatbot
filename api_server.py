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
# For local development, allow all origins so the frontend can run on any port (3000, 3001, 3003, etc.)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

CHROMA_PATH = "chroma"
DATA_PATH = "data"

# Base and optimized model names (can be overridden via environment variables)
BASE_MODEL_NAME = os.getenv("BASE_MODEL_NAME", "mistral")
# Template for quantized models - Now using actual pre-quantized Mistral models!
# mistral:7b-instruct-q4_0 is a real quantized model (4.1GB vs 4.4GB baseline)
QUANT_MODEL_TEMPLATE = os.getenv("QUANT_MODEL_TEMPLATE", "mistral:7b-instruct-q4_0")
# Name of a pruned / smaller model - using llama3.2:1b-instruct-q4_0 (770MB) as a smaller alternative
PRUNED_MODEL_NAME = os.getenv("PRUNED_MODEL_NAME", "llama3.2:1b-instruct-q4_0")  # 770MB vs 4.4GB baseline

PROMPT_TEMPLATE = """
Answer the question based only on the following context:

{context}

---

Answer the question based on the above context: {question}
"""

# Initialize DB and model (singleton / cached pattern)
_embedding_function = None
_db = None
# Cache multiple models by name so we can benchmark different variants
_models: Dict[str, OllamaLLM] = {}
_model_name = BASE_MODEL_NAME
_optimizer = ModelOptimizer()
_baseline_metrics: Optional[BenchmarkMetrics] = None


def get_db():
    global _db, _embedding_function
    if _db is None:
        _embedding_function = get_embedding_function()
        _db = Chroma(persist_directory=CHROMA_PATH, embedding_function=_embedding_function)
    return _db


def get_model(model_name: Optional[str] = None):
    """
    Get (and cache) an Ollama model by name.
    This allows us to benchmark different model variants (baseline, quantized, pruned).
    """
    global _models, _model_name
    model_to_use = model_name or _model_name
    if model_to_use not in _models:
        _models[model_to_use] = OllamaLLM(model=model_to_use)
    return _models[model_to_use]


def reset_model():
    """Reset all cached models to force reload."""
    global _models
    _models = {}


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
    """Health check endpoint - simple response for local development."""
    return {
        "status": "healthy",
        "service": "autism-chatbot-backend",
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
    # Optional free-form list of test queries (kept for backwards compatibility)
    test_queries: List[str] = ["What is autism?", "What are the symptoms of autism?", "How is autism diagnosed?"]
    technique: Optional[str] = None  # "quantization", "pruning", or None for baseline
    # New: single question to benchmark on (e.g., current chat question)
    question: Optional[str] = None


class OptimizationRequest(BaseModel):
    technique: str  # "quantization" or "pruning"
    quantization_level: Optional[str] = "q4_0"  # For quantization
    pruning_ratio: Optional[float] = 0.3  # For pruning
    # Question to benchmark on (typically the current chat question)
    question: Optional[str] = None


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
    """Run baseline benchmark on the current question using the baseline model."""
    try:
        db = get_db()
        model = get_model(BASE_MODEL_NAME)

        # Determine the question to benchmark on
        question = (request.question or (request.test_queries[0] if request.test_queries else "What is autism?")).strip()
        if not question:
            raise HTTPException(status_code=400, detail="Question for benchmark cannot be empty")

        def query_func(q: str):
            # Always benchmark on the chosen question, not on q
            answer, _ = query_rag(question, db, model)
            return answer

        result = _optimizer.benchmark_model(
            model_name=BASE_MODEL_NAME,
            query_func=query_func,
            test_queries=[question],
            technique="baseline",
        )

        global _baseline_metrics
        _baseline_metrics = result.metrics

        return {
            "technique": "baseline",
            "model_name": BASE_MODEL_NAME,
            "metrics": {
                "response_time": result.metrics.response_time,
                "memory_usage_mb": result.metrics.memory_usage_mb,
                "cpu_usage_percent": result.metrics.cpu_usage_percent,
                "tokens_per_second": result.metrics.tokens_per_second,
                "model_size_mb": result.metrics.model_size_mb,
                "latency_p50": result.metrics.latency_p50,
                "latency_p95": result.metrics.latency_p95,
                "latency_p99": result.metrics.latency_p99,
            },
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error running baseline benchmark: {str(e)}")


@app.post("/api/benchmark/quantization")
async def benchmark_quantization(request: OptimizationRequest):
    """Run quantization benchmark using a real quantized model."""
    if request.technique != "quantization":
        raise HTTPException(status_code=400, detail="Technique must be 'quantization'")
    
    try:
        # Determine question
        question = (request.question or "What is autism?").strip()
        if not question:
            raise HTTPException(status_code=400, detail="Question for benchmark cannot be empty")

        db = get_db()
        quantization_level = request.quantization_level or "q4_0"
        
        # Map quantization levels to actual pre-quantized models available in Ollama
        quant_model_map = {
            "q4_0": "mistral:7b-instruct-q4_0",   # 4.1GB - Real quantized Mistral model
            "q5_0": "llama3.2:3b",   # 2.0GB - Alternative smaller model
            "q8_0": "llama3.2:1b-instruct-q4_0"   # 770MB - Very small quantized model
        }
        
        # Get quantized model name from map, fallback to template if custom
        quant_model_name = quant_model_map.get(quantization_level)
        if not quant_model_name:
            # Try template format as fallback (for custom quantization levels)
            try:
                quant_model_name = QUANT_MODEL_TEMPLATE.format(level=quantization_level)
            except (KeyError, ValueError):
                # If template doesn't support {level}, use the default quantized model
                quant_model_name = QUANT_MODEL_TEMPLATE if "{level}" not in QUANT_MODEL_TEMPLATE else "mistral:7b-instruct-q4_0"

        # Baseline: real benchmark on base model
        base_model = get_model(BASE_MODEL_NAME)

        def baseline_query(q: str):
            answer, _ = query_rag(question, db, base_model)
            return answer

        baseline_result = _optimizer.benchmark_model(
            model_name=BASE_MODEL_NAME,
            query_func=baseline_query,
            test_queries=[question],
            technique="baseline",
        )
        baseline_metrics = baseline_result.metrics

        # Quantized model: real benchmark on quantized model
        quant_model = get_model(quant_model_name)

        def quant_query(q: str):
            answer, _ = query_rag(question, db, quant_model)
            return answer

        quant_result = _optimizer.benchmark_model(
            model_name=quant_model_name,
            query_func=quant_query,
            test_queries=[question],
            technique="quantization",
        )
        quant_metrics = quant_result.metrics

        improvements = _optimizer.calculate_improvement(baseline_metrics, quant_metrics)

        return {
            "technique": "quantization",
            "quantization_level": quantization_level,
            "model_name": quant_model_name,
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
    """Run pruning benchmark using a real pruned / smaller model if available."""
    if request.technique != "pruning":
        raise HTTPException(status_code=400, detail="Technique must be 'pruning'")
    
    try:
        # Determine question
        question = (request.question or "What is autism?").strip()
        if not question:
            raise HTTPException(status_code=400, detail="Question for benchmark cannot be empty")

        db = get_db()
        pruning_ratio = request.pruning_ratio or 0.3
        # Baseline benchmark on base model
        base_model = get_model(BASE_MODEL_NAME)

        def baseline_query(q: str):
            answer, _ = query_rag(question, db, base_model)
            return answer

        baseline_result = _optimizer.benchmark_model(
            model_name=BASE_MODEL_NAME,
            query_func=baseline_query,
            test_queries=[question],
            technique="baseline",
        )
        baseline_metrics = baseline_result.metrics

        # Determine pruned model name
        if PRUNED_MODEL_NAME:
            pruned_model_name = PRUNED_MODEL_NAME
        else:
            # Fallback: construct a name; user must ensure this model exists in Ollama
            pruned_model_name = f"{BASE_MODEL_NAME}-pruned-{int(pruning_ratio * 100)}"

        pruned_model = get_model(pruned_model_name)

        def pruned_query(q: str):
            answer, _ = query_rag(question, db, pruned_model)
            return answer

        pruned_result = _optimizer.benchmark_model(
            model_name=pruned_model_name,
            query_func=pruned_query,
            test_queries=[question],
            technique="pruning",
        )
        pruned_metrics = pruned_result.metrics

        improvements = _optimizer.calculate_improvement(baseline_metrics, pruned_metrics)

        return {
            "technique": "pruning",
            "pruning_ratio": pruning_ratio,
            "model_name": pruned_result.model_name,
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

