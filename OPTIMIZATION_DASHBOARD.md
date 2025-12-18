# Optimization Dashboard Guide

## Overview

The Optimization Dashboard provides a comprehensive interface for benchmarking and comparing model optimization techniques (Quantization and Pruning) against the baseline model performance.

## Features

### 1. Baseline Benchmark
- **Purpose**: Establish baseline performance metrics before applying optimizations
- **Metrics Measured**:
  - Response Time (seconds)
  - Memory Usage (MB)
  - CPU Usage (%)
  - Throughput (tokens/second)
  - Model Size (MB)
  - Latency percentiles (P50, P95, P99)

### 2. Quantization Optimization
- **Purpose**: Reduce model precision to improve inference speed and reduce memory usage
- **Quantization Levels**:
  - `q4_0`: 4-bit quantization (most aggressive, best compression)
  - `q5_0`: 5-bit quantization (balanced)
  - `q8_0`: 8-bit quantization (less aggressive, better quality)
- **Expected Improvements**:
  - 40% faster response time
  - 50% less memory usage
  - 30% less CPU usage
  - 50% faster throughput
  - 60% smaller model size

### 3. Pruning Optimization
- **Purpose**: Remove less important weights/neurons to reduce model size
- **Pruning Ratio**: Adjustable from 10% to 50% (slider control)
- **Expected Improvements** (for 30% pruning):
  - 20% faster response time
  - 30% less memory usage
  - 15% less CPU usage
  - Slight decrease in throughput (~10%)
  - 30% smaller model size

## How to Use

### Step 1: Run Baseline Benchmark
1. Click the **"Run"** button in the Baseline Benchmark section
2. Wait for the benchmark to complete (takes ~10-30 seconds)
3. Review the baseline metrics displayed

### Step 2: Run Quantization Benchmark
1. Select a quantization level from the dropdown (Q4_0, Q5_0, or Q8_0)
2. Click the **"Run"** button in the Quantization section
3. The dashboard will:
   - Run the benchmark with the selected quantization level
   - Compare results against the baseline
   - Display improvement percentages for each metric

### Step 3: Run Pruning Benchmark
1. Adjust the pruning ratio slider (10% to 50%)
2. Click the **"Run"** button in the Pruning section
3. The dashboard will:
   - Run the benchmark with the selected pruning ratio
   - Compare results against the baseline
   - Display improvement percentages for each metric

## Understanding the Metrics

### Response Time
- **Lower is better**
- Time taken to generate a complete response
- Measured in seconds

### Memory Usage
- **Lower is better**
- RAM consumed during inference
- Measured in MB

### CPU Usage
- **Lower is better**
- CPU utilization percentage
- Measured in %

### Throughput
- **Higher is better**
- Number of tokens generated per second
- Measured in tokens/second

### Model Size
- **Lower is better**
- Size of the model file on disk
- Measured in MB

### Latency Percentiles
- **Lower is better**
- P50: Median latency (50th percentile)
- P95: 95th percentile latency
- P99: 99th percentile latency
- Measured in milliseconds

## Improvement Indicators

- **Green with ↓**: Positive improvement (lower is better metrics)
- **Green with ↑**: Positive improvement (higher is better metrics)
- **Red**: Negative change (worse performance)

## Technical Details

### Backend Implementation
- Uses `psutil` for system resource monitoring
- Measures performance over 3 iterations for accuracy
- Calculates percentiles for latency distribution
- Simulates optimization effects based on research data

### Frontend Implementation
- Real-time metric display
- Side-by-side comparison with baseline
- Responsive design (hidden on mobile, visible on desktop)
- Loading states during benchmark execution

## API Endpoints

### `POST /api/benchmark/baseline`
Run baseline benchmark.

**Request:**
```json
{
  "test_queries": ["What is autism?", "What are the symptoms?"]
}
```

**Response:**
```json
{
  "technique": "baseline",
  "model_name": "mistral",
  "metrics": {
    "response_time": 2.5,
    "memory_usage_mb": 512.0,
    "cpu_usage_percent": 45.2,
    "tokens_per_second": 25.3,
    "model_size_mb": 4096.0
  }
}
```

### `POST /api/benchmark/quantization`
Run quantization benchmark.

**Request:**
```json
{
  "technique": "quantization",
  "quantization_level": "q4_0"
}
```

**Response:**
```json
{
  "technique": "quantization",
  "quantization_level": "q4_0",
  "model_name": "mistral-q4_0",
  "metrics": { ... },
  "baseline_metrics": { ... },
  "improvements": {
    "response_time": 40.0,
    "memory": 50.0,
    "cpu": 30.0,
    "throughput": 50.0,
    "model_size": 60.0
  }
}
```

### `POST /api/benchmark/pruning`
Run pruning benchmark.

**Request:**
```json
{
  "technique": "pruning",
  "pruning_ratio": 0.3
}
```

**Response:**
```json
{
  "technique": "pruning",
  "pruning_ratio": 0.3,
  "model_name": "mistral-pruned-30%",
  "metrics": { ... },
  "baseline_metrics": { ... },
  "improvements": { ... }
}
```

## Best Practices

1. **Always run baseline first**: You need baseline metrics to compare optimizations
2. **Run benchmarks sequentially**: Don't run multiple benchmarks simultaneously
3. **Use consistent test queries**: For accurate comparisons
4. **Monitor system resources**: Ensure sufficient RAM and CPU available
5. **Compare trade-offs**: Consider accuracy vs. performance when choosing optimization levels

## Limitations

- Current implementation simulates optimization effects (doesn't actually quantize/prune the model)
- Real quantization/pruning would require model retraining or conversion
- Benchmarks are approximate and may vary based on system load
- Model size detection depends on Ollama CLI availability

## Future Enhancements

- Real model quantization using GGML/GGUF formats
- Actual pruning implementation with weight removal
- Accuracy metrics comparison
- Historical benchmark tracking
- Export benchmark results to CSV/JSON
- Visualization charts for trend analysis




