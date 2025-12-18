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

export interface OptimizationRequest {
  technique: 'quantization' | 'pruning';
  quantization_level?: string;
  pruning_ratio?: number;
}

export interface BenchmarkResponse {
  technique: string;
  model_name: string;
  metrics: BenchmarkMetrics;
  baseline_metrics?: BenchmarkMetrics;
  improvements?: Record<string, number>;
  quantization_level?: string;
  pruning_ratio?: number;
}

export async function runBaselineBenchmark(question: string): Promise<BenchmarkResponse> {
  const response = await fetch(`${API_BASE_URL}/api/benchmark/baseline`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ question }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail || `HTTP error! status: ${response.status}`);
  }

  const data = await response.json();
  return {
    technique: data.technique,
    model_name: data.model_name,
    metrics: data.metrics,
  };
}

export async function runQuantizationBenchmark(
  quantizationLevel: string = 'q4_0',
  question: string,
): Promise<BenchmarkResponse> {
  const response = await fetch(`${API_BASE_URL}/api/benchmark/quantization`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      technique: 'quantization',
      quantization_level: quantizationLevel,
      question,
    }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail || `HTTP error! status: ${response.status}`);
  }

  return response.json();
}

export async function runPruningBenchmark(
  pruningRatio: number = 0.3,
  question: string,
): Promise<BenchmarkResponse> {
  const response = await fetch(`${API_BASE_URL}/api/benchmark/pruning`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      technique: 'pruning',
      pruning_ratio: pruningRatio,
      question,
    }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail || `HTTP error! status: ${response.status}`);
  }

  return response.json();
}

export async function getBenchmarkHistory() {
  const response = await fetch(`${API_BASE_URL}/api/benchmark/history`);
  if (!response.ok) {
    throw new Error('Failed to fetch benchmark history');
  }
  return response.json();
}




