const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface BenchmarkMetrics {
  response_time: number;
  memory_usage_mb: number;
  cpu_usage_percent: number;
  tokens_per_second: number;
  model_size_mb?: number | null;
  latency_p50?: number | null;
  latency_p95?: number | null;
  latency_p99?: number | null;
}

export interface BenchmarkResult {
  technique: string;
  model_name: string;
  metrics: BenchmarkMetrics;
  baseline_metrics?: BenchmarkMetrics;
  improvements?: {
    response_time?: number;
    memory?: number;
    cpu?: number;
    throughput?: number;
    model_size?: number;
  };
  quantization_level?: string;
  pruning_ratio?: number;
}

export interface BenchmarkRequest {
  test_queries?: string[];
  technique?: string;
}

export interface OptimizationRequest {
  technique: 'quantization' | 'pruning';
  quantization_level?: string;
  pruning_ratio?: number;
}

export async function runBaselineBenchmark(request: BenchmarkRequest = {}): Promise<BenchmarkResult> {
  const response = await fetch(`${API_BASE_URL}/api/benchmark/baseline`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail || `HTTP error! status: ${response.status}`);
  }

  return response.json();
}

export async function runQuantizationBenchmark(request: OptimizationRequest): Promise<BenchmarkResult> {
  const response = await fetch(`${API_BASE_URL}/api/benchmark/quantization`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail || `HTTP error! status: ${response.status}`);
  }

  return response.json();
}

export async function runPruningBenchmark(request: OptimizationRequest): Promise<BenchmarkResult> {
  const response = await fetch(`${API_BASE_URL}/api/benchmark/pruning`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail || `HTTP error! status: ${response.status}`);
  }

  return response.json();
}

export async function getBenchmarkHistory(): Promise<{
  baseline: BenchmarkMetrics | null;
  history: any[];
}> {
  const response = await fetch(`${API_BASE_URL}/api/benchmark/history`);
  if (!response.ok) {
    throw new Error('Failed to fetch benchmark history');
  }
  return response.json();
}


