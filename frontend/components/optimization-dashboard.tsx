"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { 
  runBaselineBenchmark, 
  runQuantizationBenchmark, 
  runPruningBenchmark,
  type BenchmarkMetrics,
  type BenchmarkResponse 
} from "@/lib/optimization-api"
import { 
  Zap, 
  Scissors, 
  TrendingUp, 
  TrendingDown, 
  Loader2, 
  Play,
  BarChart3,
  Gauge,
  Cpu,
  HardDrive,
  Timer
} from "lucide-react"

interface ComparisonData {
  baseline?: BenchmarkMetrics
  quantization?: BenchmarkMetrics
  pruning?: BenchmarkMetrics
  quantizationImprovements?: Record<string, number>
  pruningImprovements?: Record<string, number>
}

export function OptimizationDashboard() {
  const [loading, setLoading] = useState<string | null>(null)
  const [comparisonData, setComparisonData] = useState<ComparisonData>({})
  const [quantizationLevel, setQuantizationLevel] = useState("q4_0")
  const [pruningRatio, setPruningRatio] = useState(0.3)

  const runBenchmark = async (type: 'baseline' | 'quantization' | 'pruning') => {
    setLoading(type)
    try {
      let result: BenchmarkResponse
      
      if (type === 'baseline') {
        result = await runBaselineBenchmark()
        setComparisonData(prev => ({ ...prev, baseline: result.metrics }))
      } else if (type === 'quantization') {
        result = await runQuantizationBenchmark(quantizationLevel)
        setComparisonData(prev => ({
          ...prev,
          quantization: result.metrics,
          baseline: result.baseline_metrics || prev.baseline,
          quantizationImprovements: result.improvements
        }))
      } else {
        result = await runPruningBenchmark(pruningRatio)
        setComparisonData(prev => ({
          ...prev,
          pruning: result.metrics,
          baseline: result.baseline_metrics || prev.baseline,
          pruningImprovements: result.improvements
        }))
      }
    } catch (error) {
      console.error(`Error running ${type} benchmark:`, error)
      alert(`Failed to run ${type} benchmark: ${error instanceof Error ? error.message : 'Unknown error'}`)
    } finally {
      setLoading(null)
    }
  }

  const MetricCard = ({ 
    title, 
    value, 
    unit, 
    improvement, 
    lowerIsBetter = true 
  }: { 
    title: string
    value: number | null | undefined
    unit: string
    improvement?: number
    lowerIsBetter?: boolean
  }) => {
    if (value === null || value === undefined) return null
    
    const isPositive = lowerIsBetter 
      ? (improvement && improvement > 0) 
      : (improvement && improvement > 0)
    
    return (
      <div className="p-3 rounded-lg border bg-card">
        <div className="flex items-center justify-between mb-1">
          <span className="text-xs text-muted-foreground">{title}</span>
          {improvement !== undefined && (
            <span className={`text-xs font-medium flex items-center gap-1 ${
              isPositive ? 'text-green-600' : 'text-red-600'
            }`}>
              {isPositive ? <TrendingDown className="h-3 w-3" /> : <TrendingUp className="h-3 w-3" />}
              {Math.abs(improvement).toFixed(1)}%
            </span>
          )}
        </div>
        <div className="text-lg font-bold">
          {typeof value === 'number' ? value.toFixed(2) : 'N/A'} {unit}
        </div>
      </div>
    )
  }

  const ComparisonTable = ({ 
    technique, 
    metrics, 
    improvements 
  }: { 
    technique: string
    metrics?: BenchmarkMetrics
    improvements?: Record<string, number>
  }) => {
    if (!metrics || !comparisonData.baseline) return null

    const baseline = comparisonData.baseline
    const getImprovement = (key: string) => improvements?.[key] || 0

    return (
      <div className="space-y-2">
        <h4 className="text-sm font-semibold mb-3 capitalize">{technique} vs Baseline</h4>
        <div className="grid grid-cols-2 gap-2">
          <MetricCard
            title="Response Time"
            value={metrics.response_time}
            unit="s"
            improvement={getImprovement('response_time')}
            lowerIsBetter={true}
          />
          <MetricCard
            title="Memory Usage"
            value={metrics.memory_usage_mb}
            unit="MB"
            improvement={getImprovement('memory')}
            lowerIsBetter={true}
          />
          <MetricCard
            title="CPU Usage"
            value={metrics.cpu_usage_percent}
            unit="%"
            improvement={getImprovement('cpu')}
            lowerIsBetter={true}
          />
          <MetricCard
            title="Throughput"
            value={metrics.tokens_per_second}
            unit="tok/s"
            improvement={getImprovement('throughput')}
            lowerIsBetter={false}
          />
          <MetricCard
            title="Model Size"
            value={metrics.model_size_mb}
            unit="MB"
            improvement={getImprovement('model_size')}
            lowerIsBetter={true}
          />
          <MetricCard
            title="Latency (P50)"
            value={metrics.latency_p50}
            unit="ms"
            improvement={undefined}
            lowerIsBetter={true}
          />
        </div>
      </div>
    )
  }

  return (
    <div className="h-full flex flex-col gap-4 overflow-y-auto">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BarChart3 className="h-5 w-5" />
            Optimization Dashboard
          </CardTitle>
          <CardDescription>
            Benchmark and compare model optimization techniques
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Baseline Benchmark */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-sm font-semibold flex items-center gap-2">
                  <Gauge className="h-4 w-4" />
                  Baseline Benchmark
                </h3>
                <p className="text-xs text-muted-foreground">Measure baseline performance</p>
              </div>
              <Button
                size="sm"
                onClick={() => runBenchmark('baseline')}
                disabled={loading !== null}
                variant="outline"
              >
                {loading === 'baseline' ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <>
                    <Play className="h-4 w-4 mr-1" />
                    Run
                  </>
                )}
              </Button>
            </div>
            {comparisonData.baseline && (
              <div className="grid grid-cols-2 gap-2 mt-2">
                <MetricCard
                  title="Response Time"
                  value={comparisonData.baseline.response_time}
                  unit="s"
                />
                <MetricCard
                  title="Memory"
                  value={comparisonData.baseline.memory_usage_mb}
                  unit="MB"
                />
                <MetricCard
                  title="CPU"
                  value={comparisonData.baseline.cpu_usage_percent}
                  unit="%"
                />
                <MetricCard
                  title="Throughput"
                  value={comparisonData.baseline.tokens_per_second}
                  unit="tok/s"
                />
              </div>
            )}
          </div>

          <div className="border-t pt-4 space-y-4">
            {/* Quantization */}
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-sm font-semibold flex items-center gap-2">
                    <Zap className="h-4 w-4 text-yellow-500" />
                    Quantization
                  </h3>
                  <p className="text-xs text-muted-foreground">Reduce model precision</p>
                </div>
                <div className="flex items-center gap-2">
                  <select
                    value={quantizationLevel}
                    onChange={(e) => setQuantizationLevel(e.target.value)}
                    className="text-xs border rounded px-2 py-1"
                    disabled={loading !== null}
                  >
                    <option value="q4_0">Q4_0</option>
                    <option value="q5_0">Q5_0</option>
                    <option value="q8_0">Q8_0</option>
                  </select>
                  <Button
                    size="sm"
                    onClick={() => runBenchmark('quantization')}
                    disabled={loading !== null || !comparisonData.baseline}
                    variant="outline"
                  >
                    {loading === 'quantization' ? (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    ) : (
                      <>
                        <Play className="h-4 w-4 mr-1" />
                        Run
                      </>
                    )}
                  </Button>
                </div>
              </div>
              <ComparisonTable
                technique="quantization"
                metrics={comparisonData.quantization}
                improvements={comparisonData.quantizationImprovements}
              />
            </div>

            {/* Pruning */}
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-sm font-semibold flex items-center gap-2">
                    <Scissors className="h-4 w-4 text-blue-500" />
                    Pruning
                  </h3>
                  <p className="text-xs text-muted-foreground">Remove less important weights</p>
                </div>
                <div className="flex items-center gap-2">
                  <input
                    type="range"
                    min="0.1"
                    max="0.5"
                    step="0.1"
                    value={pruningRatio}
                    onChange={(e) => setPruningRatio(parseFloat(e.target.value))}
                    className="w-20"
                    disabled={loading !== null}
                  />
                  <span className="text-xs w-10">{Math.round(pruningRatio * 100)}%</span>
                  <Button
                    size="sm"
                    onClick={() => runBenchmark('pruning')}
                    disabled={loading !== null || !comparisonData.baseline}
                    variant="outline"
                  >
                    {loading === 'pruning' ? (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    ) : (
                      <>
                        <Play className="h-4 w-4 mr-1" />
                        Run
                      </>
                    )}
                  </Button>
                </div>
              </div>
              <ComparisonTable
                technique="pruning"
                metrics={comparisonData.pruning}
                improvements={comparisonData.pruningImprovements}
              />
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}


