"""
Optimization utilities for model quantization and pruning benchmarking.
"""
import time
import psutil
import subprocess
import json
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
import os


@dataclass
class BenchmarkMetrics:
    """Metrics for benchmarking model performance."""
    response_time: float  # seconds
    memory_usage_mb: float  # MB
    cpu_usage_percent: float  # %
    tokens_per_second: float  # tokens/sec
    model_size_mb: Optional[float] = None  # MB
    latency_p50: Optional[float] = None  # ms
    latency_p95: Optional[float] = None  # ms
    latency_p99: Optional[float] = None  # ms


@dataclass
class OptimizationResult:
    """Result of an optimization benchmark."""
    technique: str  # "quantization" or "pruning"
    model_name: str
    metrics: BenchmarkMetrics
    before_metrics: Optional[BenchmarkMetrics] = None
    improvement_percent: Optional[Dict[str, float]] = None


class ModelOptimizer:
    """Handles model optimization and benchmarking."""
    
    def __init__(self):
        self.benchmark_history: List[OptimizationResult] = []
        self.current_model = "mistral"
        self.quantization_levels = ["q4_0", "q5_0", "q8_0"]  # Ollama quantization formats
        self.process = psutil.Process()
    
    def get_ollama_model_size(self, model_name: str) -> Optional[float]:
        """Get model size from Ollama."""
        try:
            result = subprocess.run(
                ["ollama", "show", model_name, "--modelfile"],
                capture_output=True,
                text=True,
                timeout=5
            )
            # Try to get size from ollama list
            list_result = subprocess.run(
                ["ollama", "list"],
                capture_output=True,
                text=True,
                timeout=5
            )
            # Parse size from list output (format: "model_name  size")
            for line in list_result.stdout.split('\n'):
                if model_name in line:
                    parts = line.split()
                    if len(parts) >= 2:
                        size_str = parts[-1]  # Last part is usually size
                        # Convert size string to MB
                        if 'GB' in size_str:
                            return float(size_str.replace('GB', '')) * 1024
                        elif 'MB' in size_str:
                            return float(size_str.replace('MB', ''))
            return None
        except Exception as e:
            print(f"Error getting model size: {e}")
            return None
    
    def measure_query_performance(
        self, 
        query_func, 
        query_text: str,
        iterations: int = 3
    ) -> BenchmarkMetrics:
        """Measure performance of a query function."""
        response_times = []
        memory_readings = []
        cpu_readings = []
        token_counts = []
        
        # Warm-up run
        try:
            _ = query_func(query_text)
        except:
            pass
        
        for i in range(iterations):
            # Measure memory before
            memory_before = self.process.memory_info().rss / 1024 / 1024  # MB
            cpu_before = self.process.cpu_percent(interval=0.1)
            
            # Measure query time
            start_time = time.time()
            try:
                response = query_func(query_text)
                end_time = time.time()
                response_time = end_time - start_time
                response_times.append(response_time)
                
                # Estimate tokens (rough approximation: ~4 chars per token)
                if isinstance(response, str):
                    estimated_tokens = len(response) / 4
                    tokens_per_sec = estimated_tokens / response_time if response_time > 0 else 0
                    token_counts.append(tokens_per_sec)
            except Exception as e:
                print(f"Error in query: {e}")
                continue
            
            # Measure memory after
            memory_after = self.process.memory_info().rss / 1024 / 1024  # MB
            cpu_after = self.process.cpu_percent(interval=0.1)
            
            memory_readings.append(memory_after - memory_before)
            cpu_readings.append((cpu_before + cpu_after) / 2)
            
            # Small delay between iterations
            time.sleep(0.5)
        
        if not response_times:
            raise ValueError("No successful queries")
        
        # Calculate percentiles
        sorted_times = sorted([t * 1000 for t in response_times])  # Convert to ms
        n = len(sorted_times)
        p50 = sorted_times[n // 2] if n > 0 else 0
        p95 = sorted_times[int(n * 0.95)] if n > 1 else sorted_times[-1]
        p99 = sorted_times[int(n * 0.99)] if n > 1 else sorted_times[-1]
        
        return BenchmarkMetrics(
            response_time=sum(response_times) / len(response_times),
            memory_usage_mb=sum(memory_readings) / len(memory_readings) if memory_readings else 0,
            cpu_usage_percent=sum(cpu_readings) / len(cpu_readings) if cpu_readings else 0,
            tokens_per_second=sum(token_counts) / len(token_counts) if token_counts else 0,
            latency_p50=p50,
            latency_p95=p95,
            latency_p99=p99
        )
    
    def benchmark_model(
        self,
        model_name: str,
        query_func,
        test_queries: List[str],
        technique: str = "baseline"
    ) -> OptimizationResult:
        """Benchmark a model configuration."""
        # Use first test query for benchmarking
        test_query = test_queries[0] if test_queries else "What is autism?"
        
        metrics = self.measure_query_performance(query_func, test_query, iterations=3)
        model_size = self.get_ollama_model_size(model_name)
        if model_size:
            metrics.model_size_mb = model_size
        
        result = OptimizationResult(
            technique=technique,
            model_name=model_name,
            metrics=metrics
        )
        
        return result
    
    def calculate_improvement(
        self,
        before: BenchmarkMetrics,
        after: BenchmarkMetrics
    ) -> Dict[str, float]:
        """Calculate improvement percentage between two benchmark results."""
        improvements = {}
        
        # Response time improvement (lower is better)
        if before.response_time > 0:
            improvements["response_time"] = ((before.response_time - after.response_time) / before.response_time) * 100
        
        # Memory improvement (lower is better)
        if before.memory_usage_mb > 0:
            improvements["memory"] = ((before.memory_usage_mb - after.memory_usage_mb) / before.memory_usage_mb) * 100
        
        # CPU improvement (lower is better)
        if before.cpu_usage_percent > 0:
            improvements["cpu"] = ((before.cpu_usage_percent - after.cpu_usage_percent) / before.cpu_usage_percent) * 100
        
        # Throughput improvement (higher is better)
        if before.tokens_per_second > 0:
            improvements["throughput"] = ((after.tokens_per_second - before.tokens_per_second) / before.tokens_per_second) * 100
        
        # Model size improvement (lower is better)
        if before.model_size_mb and after.model_size_mb and before.model_size_mb > 0:
            improvements["model_size"] = ((before.model_size_mb - after.model_size_mb) / before.model_size_mb) * 100
        
        return improvements
    
    def simulate_pruning(self, base_metrics: BenchmarkMetrics, pruning_ratio: float = 0.3) -> BenchmarkMetrics:
        """Simulate pruning by adjusting metrics (since actual pruning requires model retraining)."""
        # Simulate improvements from pruning:
        # - Reduced model size
        # - Faster inference (slightly)
        # - Lower memory usage
        # - Slightly reduced throughput (due to sparsity overhead)
        
        return BenchmarkMetrics(
            response_time=base_metrics.response_time * (1 - pruning_ratio * 0.2),  # ~20% improvement per 30% pruning
            memory_usage_mb=base_metrics.memory_usage_mb * (1 - pruning_ratio),
            cpu_usage_percent=base_metrics.cpu_usage_percent * (1 - pruning_ratio * 0.15),
            tokens_per_second=base_metrics.tokens_per_second * (1 - pruning_ratio * 0.1),  # Slight decrease
            model_size_mb=base_metrics.model_size_mb * (1 - pruning_ratio) if base_metrics.model_size_mb else None,
            latency_p50=base_metrics.latency_p50 * (1 - pruning_ratio * 0.2) if base_metrics.latency_p50 else None,
            latency_p95=base_metrics.latency_p95 * (1 - pruning_ratio * 0.2) if base_metrics.latency_p95 else None,
            latency_p99=base_metrics.latency_p99 * (1 - pruning_ratio * 0.2) if base_metrics.latency_p99 else None,
        )




