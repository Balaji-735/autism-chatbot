"use client"

import { useState, useRef, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Textarea } from "@/components/ui/textarea"
import { ScrollArea } from "@/components/ui/scroll-area"
import { queryRAG, type QueryResponse, type Source, getPdfUrl } from "@/lib/api"
import { Send, Loader2, Bot, User, FileText, ExternalLink, BarChart3, MessageCircle, ChevronRight, ChevronLeft, X } from "lucide-react"
import { HealthIndicator } from "@/components/health-indicator"
import { OptimizationDashboard } from "@/components/optimization-dashboard"

interface Message {
  id: string
  role: "user" | "assistant"
  content: string
  sources?: Source[]
  timestamp: Date
}

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [lastQuestion, setLastQuestion] = useState<string | null>(null)
  const [showDashboard, setShowDashboard] = useState(true)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim() || isLoading) return

    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content: input.trim(),
      timestamp: new Date(),
    }

    setMessages((prev) => [...prev, userMessage])
    setLastQuestion(userMessage.content)
    setInput("")
    setIsLoading(true)
    setError(null)

    try {
      const response: QueryResponse = await queryRAG(userMessage.content)

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: response.answer,
        sources: response.sources,
        timestamp: new Date(),
      }

      setMessages((prev) => [...prev, assistantMessage])
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "An error occurred"
      setError(errorMessage)
      const errorMsg: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: `Sorry, I encountered an error: ${errorMessage}. Please make sure the backend server is running.`,
        timestamp: new Date(),
      }
      setMessages((prev) => [...prev, errorMsg])
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-background to-muted/20">
      <div className="container mx-auto max-w-[1800px] py-8 px-4">
        <div className={`grid gap-4 h-[calc(100vh-4rem)] transition-all duration-300 ${
          showDashboard ? "grid-cols-1 lg:grid-cols-2" : "grid-cols-1"
        }`}>
          {/* Chat Section */}
          <Card className="h-full flex flex-col relative">
            <CardHeader className="border-b">
              <div className="flex items-start justify-between gap-4">
                <div className="space-y-2 flex-1">
                  <CardTitle className="flex items-center gap-2">
                    <Bot className="h-6 w-6 text-primary" />
                    Autism Chatbot
                  </CardTitle>
                  <CardDescription>
                    Ask questions about autism-related documents.
                  </CardDescription>
                </div>
                <div className="flex items-center gap-2">
                  <HealthIndicator />
                  <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    className="gap-2"
                    onClick={() => setShowDashboard(!showDashboard)}
                    title={showDashboard ? "Hide Dashboard" : "Show Dashboard"}
                  >
                    <BarChart3 className="h-4 w-4" />
                    {showDashboard ? (
                      <>
                        <ChevronRight className="h-4 w-4" />
                        <span className="hidden sm:inline">Hide Dashboard</span>
                      </>
                    ) : (
                      <>
                        <ChevronLeft className="h-4 w-4" />
                        <span className="hidden sm:inline">Show Dashboard</span>
                      </>
                    )}
                  </Button>
                </div>
              </div>
            </CardHeader>

            <CardContent className="flex-1 flex flex-col p-0 overflow-hidden min-h-0">
              <ScrollArea className="flex-1 p-6 min-h-0">
                      {messages.length === 0 ? (
                        <div className="flex flex-col items-center justify-center h-full text-center text-muted-foreground space-y-4">
                          <Bot className="h-12 w-12 opacity-50" />
                          <div>
                            <p className="text-lg font-medium">Welcome to the Autism Chatbot</p>
                            <p className="text-sm mt-2">
                              Start by asking a question about autism-related topics.
                            </p>
                          </div>
                        </div>
                      ) : (
                        <div className="space-y-6">
                          {messages.map((message) => (
                            <div
                              key={message.id}
                              className={`flex gap-4 ${
                                message.role === "user" ? "justify-end" : "justify-start"
                              }`}
                            >
                              {message.role === "assistant" && (
                                <div className="flex-shrink-0">
                                  <div className="h-10 w-10 rounded-full bg-primary/10 flex items-center justify-center">
                                    <Bot className="h-5 w-5 text-primary" />
                                  </div>
                                </div>
                              )}

                              <div
                                className={`flex flex-col gap-2 max-w-[80%] ${
                                  message.role === "user" ? "items-end" : "items-start"
                                }`}
                              >
                                <div
                                  className={`rounded-lg px-4 py-3 ${
                                    message.role === "user"
                                      ? "bg-primary text-primary-foreground"
                                      : "bg-muted"
                                  }`}
                                >
                                  <p className="whitespace-pre-wrap break-words">
                                    {message.content}
                                  </p>
                                </div>

                                {message.sources && message.sources.length > 0 && (
                                  <div className="w-full space-y-2 mt-2">
                                    <div className="flex items-center justify-between">
                                      <p className="text-xs text-muted-foreground font-medium flex items-center gap-1">
                                        <FileText className="h-3 w-3" />
                                        Sources ({message.sources.length})
                                      </p>
                                      <p
                                        className="text-xs text-muted-foreground"
                                        title="Lower distance = higher relevance. Distance of 0 = perfect match, 1 = no match"
                                      >
                                        ℹ️ Lower distance = better match
                                      </p>
                                    </div>
                                    <div className="space-y-1">
                                      {message.sources.map((source, idx) => {
                                        // Try to get PDF URL from multiple sources
                                        let pdfUrl: string | null = null
                                        const API_BASE_URL =
                                          process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

                                        // Debug: Log source structure (remove in production)
                                        if (process.env.NODE_ENV === "development") {
                                          console.log("Source data:", {
                                            hasPdfUrl: !!source.pdf_url,
                                            hasMetadata: !!source.metadata,
                                            hasSource: !!source.metadata?.source,
                                            sourcePath: source.metadata?.source,
                                          })
                                        }

                                        // First, try the pdf_url field from backend
                                        if (source.pdf_url) {
                                          pdfUrl = getPdfUrl(source.pdf_url)
                                        }

                                        // Fallback: construct URL from source metadata if pdf_url is missing
                                        if (!pdfUrl && source.metadata?.source) {
                                          try {
                                            const sourcePath = source.metadata.source
                                            if (sourcePath) {
                                              // Handle both Windows and Unix path separators
                                              const normalizedPath = sourcePath.replace(/\\/g, "/")
                                              const encodedPath = encodeURIComponent(normalizedPath)
                                              pdfUrl = `${API_BASE_URL}/api/pdf?file=${encodedPath}`
                                            }
                                          } catch (error) {
                                            console.error("Error constructing PDF URL:", error)
                                          }
                                        }

                                        // Final fallback: if we have a filename but no URL, we can't create a link
                                        // This should rarely happen if metadata.source exists

                                        const displayName =
                                          source.filename ||
                                          (source.metadata.source
                                            ? source.metadata.source
                                                .split("/")
                                                .pop()
                                                ?.split("\\")
                                                .pop()
                                            : `Source ${idx + 1}`)

                                        return (
                                          <div
                                            key={idx}
                                            className="text-xs p-2 rounded border bg-card/50 border-border"
                                          >
                                            <div className="flex items-start justify-between gap-2 mb-1">
                                              <div className="flex-1 min-w-0">
                                                {pdfUrl ? (
                                                  <a
                                                    href={pdfUrl}
                                                    target="_blank"
                                                    rel="noopener noreferrer"
                                                    className="font-medium text-primary hover:text-primary/90 hover:underline inline-flex items-center gap-1.5 group transition-colors"
                                                    title="Click to open PDF in new tab"
                                                  >
                                                    <span className="truncate">{displayName}</span>
                                                    <ExternalLink className="h-3.5 w-3.5 flex-shrink-0 text-primary/70 group-hover:text-primary" />
                                                    {source.metadata.page !== undefined && (
                                                      <span className="text-muted-foreground ml-1 font-normal flex-shrink-0">
                                                        - Page {source.metadata.page + 1}
                                                      </span>
                                                    )}
                                                  </a>
                                                ) : (
                                                  <p className="font-medium">
                                                    {displayName}
                                                    {source.metadata.page !== undefined && (
                                                      <span className="text-muted-foreground ml-1">
                                                        - Page {source.metadata.page + 1}
                                                      </span>
                                                    )}
                                                  </p>
                                                )}
                                              </div>
                                              {pdfUrl && (
                                                <a
                                                  href={pdfUrl}
                                                  target="_blank"
                                                  rel="noopener noreferrer"
                                                  className="flex items-center gap-1.5 text-primary hover:text-primary/90 transition-all shrink-0 px-2.5 py-1.5 rounded-md hover:bg-primary/10 border border-primary/20 hover:border-primary/40"
                                                  title="Open PDF in new tab"
                                                >
                                                  <ExternalLink className="h-3.5 w-3.5" />
                                                  <span className="text-xs font-semibold">PDF</span>
                                                </a>
                                              )}
                                            </div>
                                            <p className="text-muted-foreground line-clamp-2 mb-2">
                                              {source.content}
                                            </p>
                                            <div className="flex items-center justify-between mt-2 pt-2 border-t border-border/50">
                                              <p className="text-xs text-muted-foreground">
                                                <span className="font-medium">Distance:</span>{" "}
                                                {source.score.toFixed(3)}
                                                <span
                                                  className="ml-2 text-xs"
                                                  title="Lower is better. 0 = perfect match, 1+ = less relevant"
                                                >
                                                  {source.score < 0.3
                                                    ? "🎯 Excellent match"
                                                    : source.score < 0.5
                                                    ? "✅ Good match"
                                                    : "⚡ Fair match"}
                                                </span>
                                              </p>
                                            </div>
                                          </div>
                                        )
                                      })}
                                    </div>
                                  </div>
                                )}

                                <p className="text-xs text-muted-foreground">
                                  {message.timestamp.toLocaleTimeString()}
                                </p>
                              </div>

                              {message.role === "user" && (
                                <div className="flex-shrink-0">
                                  <div className="h-10 w-10 rounded-full bg-primary/10 flex items-center justify-center">
                                    <User className="h-5 w-5 text-primary" />
                                  </div>
                                </div>
                              )}
                            </div>
                          ))}

                          {isLoading && (
                            <div className="flex gap-4 justify-start">
                              <div className="flex-shrink-0">
                                <div className="h-10 w-10 rounded-full bg-primary/10 flex items-center justify-center">
                                  <Bot className="h-5 w-5 text-primary" />
                                </div>
                              </div>
                              <div className="bg-muted rounded-lg px-4 py-3">
                                <Loader2 className="h-5 w-5 animate-spin text-muted-foreground" />
                              </div>
                            </div>
                          )}

                          <div ref={messagesEndRef} />
                        </div>
                      )}
                    </ScrollArea>

                    {error && (
                      <div className="px-6 pb-2">
                        <div className="text-sm text-destructive bg-destructive/10 p-2 rounded">
                          {error}
                        </div>
                      </div>
                    )}

                    <form onSubmit={handleSubmit} className="border-t p-4">
                      <div className="flex gap-2">
                        <Textarea
                          value={input}
                          onChange={(e) => setInput(e.target.value)}
                          placeholder="Ask a question about autism..."
                          className="min-h-[60px] max-h-[120px] resize-none"
                          onKeyDown={(e) => {
                            if (e.key === "Enter" && !e.shiftKey) {
                              e.preventDefault()
                              handleSubmit(e)
                            }
                          }}
                          disabled={isLoading}
                        />
                        <Button
                          type="submit"
                          disabled={isLoading || !input.trim()}
                          className="self-end"
                          size="icon"
                        >
                          {isLoading ? (
                            <Loader2 className="h-4 w-4 animate-spin" />
                          ) : (
                            <Send className="h-4 w-4" />
                          )}
                        </Button>
                      </div>
                    </form>
            </CardContent>
          </Card>

          {/* Dashboard Section */}
          {showDashboard && (
            <Card className="h-full flex flex-col relative">
              <CardHeader className="border-b">
                <div className="flex items-start justify-between gap-4">
                  <div className="space-y-2 flex-1">
                    <CardTitle className="flex items-center gap-2">
                      <BarChart3 className="h-6 w-6 text-primary" />
                      Optimization Dashboard
                    </CardTitle>
                    <CardDescription>
                      Compare baseline, quantized, and pruned model performance.
                    </CardDescription>
                  </div>
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    className="h-8 w-8 p-0"
                    onClick={() => setShowDashboard(false)}
                    title="Hide Dashboard"
                  >
                    <X className="h-4 w-4" />
                  </Button>
                </div>
              </CardHeader>

              <CardContent className="flex-1 min-h-0 p-4 overflow-y-auto">
                <OptimizationDashboard currentQuestion={lastQuestion} />
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  )
}
