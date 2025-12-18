"use client"

import { useEffect, useState } from "react"
import { checkHealth } from "@/lib/api"
import { CheckCircle2, XCircle, Loader2 } from "lucide-react"

export function HealthIndicator() {
  const [status, setStatus] = useState<"checking" | "healthy" | "unhealthy">("checking")

  useEffect(() => {
    const check = async () => {
      try {
        await checkHealth()
        setStatus("healthy")
      } catch {
        setStatus("unhealthy")
      }
    }

    check()
    const interval = setInterval(check, 30000) // Check every 30 seconds
    return () => clearInterval(interval)
  }, [])

  if (status === "checking") {
    return (
      <div className="flex items-center gap-2 text-xs text-muted-foreground">
        <Loader2 className="h-3 w-3 animate-spin" />
        <span>Checking backend...</span>
      </div>
    )
  }

  if (status === "healthy") {
    return (
      <div className="flex items-center gap-2 text-xs text-green-600">
        <CheckCircle2 className="h-3 w-3" />
        <span>Backend connected</span>
      </div>
    )
  }

  return (
    <div className="flex items-center gap-2 text-xs text-red-600">
      <XCircle className="h-3 w-3" />
      <span>Backend unavailable</span>
    </div>
  )
}




