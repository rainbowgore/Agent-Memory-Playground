"use client"

import { useState, useCallback, useEffect } from "react"
import { AgentWindow } from "@/components/agent-window"
import { ConfigPanel } from "@/components/config-panel"
import { DisplayTitle } from "@/components/display-title"
import { Settings2, AlertCircle, Database, Cpu, Clock } from "lucide-react"
import { ShortcutsModal, ShortcutsTrigger } from "@/components/shortcuts-modal"
import type { AgentConfig, MasterConfig, Message } from "@/lib/types"
import { DEFAULT_AGENT_CONFIG, DEFAULT_MASTER_CONFIG } from "@/lib/types"
import { createAgent, sendMessage as apiSendMessage, clearMemory, buildStrategyParams, checkBackendHealth } from "@/lib/api"
import { generateId, formatTime, formatNumber } from "@/lib/utils"

export function Playground() {
  const [configOpen, setConfigOpen] = useState(true)
  const [agentAConfig, setAgentAConfig] = useState<AgentConfig>({ ...DEFAULT_AGENT_CONFIG })
  const [agentBConfig, setAgentBConfig] = useState<AgentConfig>({
    ...DEFAULT_AGENT_CONFIG,
    memoryType: "sliding_window",
    model: "gpt-4o-mini",
  })
  const [masterConfig, setMasterConfig] = useState<MasterConfig>({ ...DEFAULT_MASTER_CONFIG })
  const [messagesA, setMessagesA] = useState<Message[]>([])
  const [messagesB, setMessagesB] = useState<Message[]>([])
  const [loadingA, setLoadingA] = useState(false)
  const [loadingB, setLoadingB] = useState(false)
  const [agentAInitialized, setAgentAInitialized] = useState(false)
  const [agentBInitialized, setAgentBInitialized] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [backendOnline, setBackendOnline] = useState<boolean | null>(null)
  const [metricsA, setMetricsA] = useState<{ retrievalTime?: number; generationTime?: number; promptTokens?: number }>({})
  const [metricsB, setMetricsB] = useState<{ retrievalTime?: number; generationTime?: number; promptTokens?: number }>({})
  const [shortcutsOpen, setShortcutsOpen] = useState(false)

  const sessionIdA = "agent-a"
  const sessionIdB = "agent-b"

  // Check backend health on mount
  useEffect(() => {
    checkBackendHealth().then(setBackendOnline)
  }, [])

  // Initialize agents when config changes
  useEffect(() => {
    if (backendOnline && !agentAInitialized) {
      initializeAgent("A", agentAConfig)
    }
  }, [backendOnline, agentAConfig.memoryType, agentAInitialized])

  useEffect(() => {
    if (backendOnline && !agentBInitialized) {
      initializeAgent("B", agentBConfig)
    }
  }, [backendOnline, agentBConfig.memoryType, agentBInitialized])

  const initializeAgent = async (agent: "A" | "B", config: AgentConfig) => {
    try {
      const sessionId = agent === "A" ? sessionIdA : sessionIdB
      const params = buildStrategyParams(config)

      await createAgent(sessionId, config.memoryType, config.model, params, config.systemPrompt)

      if (agent === "A") {
        setAgentAInitialized(true)
      } else {
        setAgentBInitialized(true)
      }
      setError(null)
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "Failed to initialize agent"
      setError(errorMessage)
      console.error(`Failed to initialize agent ${agent}:`, err)
    }
  }

  const sendToAgent = useCallback(
    async (agent: "A" | "B", text: string) => {
      const sessionId = agent === "A" ? sessionIdA : sessionIdB
      const config = agent === "A" ? agentAConfig : agentBConfig
      const setMessages = agent === "A" ? setMessagesA : setMessagesB
      const setLoading = agent === "A" ? setLoadingA : setLoadingB
      const isInitialized = agent === "A" ? agentAInitialized : agentBInitialized

      // Reinitialize if not initialized
      if (!isInitialized) {
        await initializeAgent(agent, config)
      }

      // Add user message immediately
      const userMsg: Message = {
        id: generateId(),
        role: "user",
        content: text,
        timestamp: Date.now(),
      }
      setMessages((prev) => [...prev, userMsg])

      // Set loading state
      setLoading(true)
      setError(null)

      try {
        // Call API
        const response = await apiSendMessage(sessionId, text)

        // Add assistant message
        const assistantMsg: Message = {
          id: generateId(),
          role: "assistant",
          content: response.response,
          timestamp: Date.now(),
        }
        setMessages((prev) => [...prev, assistantMsg])

        // Update metrics
        const setMetrics = agent === "A" ? setMetricsA : setMetricsB
        setMetrics({
          retrievalTime: response.retrieval_time,
          generationTime: response.generation_time,
          promptTokens: response.prompt_tokens,
        })

        // If sync messages is enabled, send to other agent
        if (masterConfig.syncMessages) {
          const otherAgent = agent === "A" ? "B" : "A"
          const otherSessionId = agent === "A" ? sessionIdB : sessionIdA
          const otherConfig = agent === "A" ? agentBConfig : agentAConfig
          const otherSetMessages = agent === "A" ? setMessagesB : setMessagesA
          const otherIsInitialized = agent === "A" ? agentBInitialized : agentAInitialized

          // Reinitialize other agent if needed
          if (!otherIsInitialized) {
            await initializeAgent(otherAgent, otherConfig)
          }

          // Send to other agent
          const otherResponse = await apiSendMessage(otherSessionId, text)

          otherSetMessages((prev) => [
            ...prev,
            { ...userMsg, id: generateId() },
            {
              id: generateId(),
              role: "assistant",
              content: otherResponse.response,
              timestamp: Date.now() + 1,
            },
          ])

          // Update other agent metrics
          const otherSetMetrics = agent === "A" ? setMetricsB : setMetricsA
          otherSetMetrics({
            retrievalTime: otherResponse.retrieval_time,
            generationTime: otherResponse.generation_time,
            promptTokens: otherResponse.prompt_tokens,
          })
        }
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : "Failed to send message"
        setError(errorMessage)
        console.error(`Failed to send message to agent ${agent}:`, err)

        // Add error message to chat
        const errorMsg: Message = {
          id: generateId(),
          role: "assistant",
          content: `Error: ${errorMessage}. Please check that the backend is running.`,
          timestamp: Date.now(),
        }
        setMessages((prev) => [...prev, errorMsg])
      } finally {
        setLoading(false)
      }
    },
    [agentAConfig, agentBConfig, masterConfig.syncMessages, agentAInitialized, agentBInitialized]
  )

  const sendToBothAgents = useCallback(
    async (text: string) => {
      if (!text.trim()) return

      // Send to both agents in parallel
      await Promise.all([
        sendToAgent("A", text),
        sendToAgent("B", text)
      ])
    },
    [sendToAgent]
  )

  const handleClearMessages = useCallback(
    async (agent: "A" | "B") => {
      const sessionId = agent === "A" ? sessionIdA : sessionIdB
      const setMessages = agent === "A" ? setMessagesA : setMessagesB

      try {
        await clearMemory(sessionId)
        setMessages([])
        setError(null)
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : "Failed to clear memory"
        setError(errorMessage)
        console.error(`Failed to clear memory for agent ${agent}:`, err)
      }
    },
    []
  )

  return (
    <div className="relative min-h-screen">
      <ShortcutsModal open={shortcutsOpen} onClose={() => setShortcutsOpen(false)} />
      <a
        href={process.env.NEXT_PUBLIC_GITHUB_URL ?? "https://github.com"}
        target="_blank"
        rel="noopener noreferrer"
        className="github-corner-link fixed bottom-4 right-4 z-20 rounded-lg bg-transparent p-1 transition hover:bg-slate-800/50"
        aria-label="GitHub repository"
      >
        <img
          src="/github.png"
          alt="GitHub"
          className="h-10 w-10 object-contain"
          width={40}
          height={40}
        />
      </a>
      <div className="mx-auto max-w-5xl px-4 py-8 sm:px-6">
        <header className="mb-8 flex flex-wrap items-end justify-between gap-4">
          <div>
            <h1 className="text-2xl text-slate-100 sm:text-3xl">
              <DisplayTitle>Agent Memory Playground</DisplayTitle>
            </h1>
            <p className="mt-1 font-serif text-sm text-slate-200">
              Compare two agents with different memory strategies.
            </p>
            {backendOnline === false && (
              <div className="mt-2 flex items-center gap-2 text-sm text-red-400">
                <AlertCircle className="h-4 w-4" />
                <span>Backend offline. Start the API server on port 8000.</span>
              </div>
            )}
          </div>
          <div className="flex items-center gap-1">
            <ShortcutsTrigger onClick={() => setShortcutsOpen(true)} />
            {!configOpen && (
              <button
                type="button"
                onClick={() => setConfigOpen(true)}
                className="rounded-lg p-2 text-slate-400 transition hover:bg-window hover:text-slate-100"
                aria-label="Open configuration"
              >
                <Settings2 className="h-4 w-4" />
              </button>
            )}
          </div>
        </header>

        {error && (
          <div className="mb-6 rounded-lg border border-red-500/50 bg-red-500/10 px-4 py-3 text-sm text-red-400">
            <div className="flex items-start gap-2">
              <AlertCircle className="h-4 w-4 shrink-0 mt-0.5" />
              <div>
                <strong className="font-semibold">Error:</strong> {error}
              </div>
            </div>
          </div>
        )}

        <div className="flex flex-col gap-6 lg:flex-row">
          {configOpen && (
            <aside className="w-full shrink-0 lg:w-64">
              <ConfigPanel
                agentAConfig={agentAConfig}
                agentBConfig={agentBConfig}
                masterConfig={masterConfig}
                onUpdateAgentA={(cfg) => {
                  setAgentAConfig(cfg)
                  setAgentAInitialized(false)
                }}
                onUpdateAgentB={(cfg) => {
                  setAgentBConfig(cfg)
                  setAgentBInitialized(false)
                }}
                onUpdateMaster={setMasterConfig}
                onClose={() => setConfigOpen(false)}
              />
            </aside>
          )}

          <div className="flex min-w-0 flex-1 flex-col gap-4">
            <div className="grid min-w-0 gap-6 sm:grid-cols-2">
              <AgentWindow
                agentId="A"
                config={agentAConfig}
                messages={messagesA}
                onSendMessage={(msg) => sendToAgent("A", msg)}
                onClearMessages={() => handleClearMessages("A")}
                onSendToBoth={sendToBothAgents}
                metrics={metricsA}
              />
              <AgentWindow
                agentId="B"
                config={agentBConfig}
                messages={messagesB}
                onSendMessage={(msg) => sendToAgent("B", msg)}
                onClearMessages={() => handleClearMessages("B")}
                onSendToBoth={sendToBothAgents}
                metrics={metricsB}
              />
            </div>

            {/* Live analytics - two separate data windows under the agent windows */}
            <section className="mt-4 grid gap-4 sm:grid-cols-2" aria-label="Live analytics">
              {(() => {
                const hasA =
                  metricsA.retrievalTime !== undefined ||
                  metricsA.generationTime !== undefined ||
                  metricsA.promptTokens !== undefined
                const hasB =
                  metricsB.retrievalTime !== undefined ||
                  metricsB.generationTime !== undefined ||
                  metricsB.promptTokens !== undefined
                const hasAnalytics = hasA || hasB

                if (!hasAnalytics) {
                  return (
                    <div className="col-span-full rounded-lg border border-windowBorder bg-window/60 px-3 py-2.5 backdrop-blur-sm">
                      <p className="py-3 text-center text-sm font-semibold text-white">
                        Data will appear when you start playing
                      </p>
                    </div>
                  )
                }

                return (
                  <>
                    <div
                      className="rounded-lg border border-windowBorder bg-window/60 px-3 py-2.5 backdrop-blur-sm"
                      aria-label="Agent A metrics"
                    >
                      <p className="mb-2 text-xs font-semibold text-slate-300">Agent A</p>
                      <div className="grid grid-cols-3 gap-x-4 gap-y-1 text-xs">
                        {metricsA.retrievalTime !== undefined && (
                          <div className="flex items-baseline gap-1.5">
                            <Database className="h-3 w-3 shrink-0 text-slate-500" aria-hidden />
                            <span className="text-slate-500">Retrieval</span>
                            <span className="shrink-0 font-mono text-slate-300 whitespace-nowrap">{formatTime(metricsA.retrievalTime)}</span>
                          </div>
                        )}
                        {metricsA.generationTime !== undefined && (
                          <div className="flex items-baseline gap-1.5">
                            <Cpu className="h-3 w-3 shrink-0 text-slate-500" aria-hidden />
                            <span className="text-slate-500">Generation</span>
                            <span className="shrink-0 font-mono text-slate-300 whitespace-nowrap">{formatTime(metricsA.generationTime)}</span>
                          </div>
                        )}
                        {metricsA.promptTokens !== undefined && (
                          <div className="flex items-baseline gap-1.5">
                            <Clock className="h-3 w-3 shrink-0 text-slate-500" aria-hidden />
                            <span className="text-slate-500">Tokens</span>
                            <span className="shrink-0 font-mono text-slate-300 whitespace-nowrap">{formatNumber(metricsA.promptTokens)}</span>
                          </div>
                        )}
                      </div>
                    </div>
                    <div
                      className="rounded-lg border border-windowBorder bg-window/60 px-3 py-2.5 backdrop-blur-sm"
                      aria-label="Agent B metrics"
                    >
                      <p className="mb-2 text-xs font-semibold text-slate-300">Agent B</p>
                      <div className="grid grid-cols-3 gap-x-4 gap-y-1 text-xs">
                        {metricsB.retrievalTime !== undefined && (
                          <div className="flex items-baseline gap-1.5">
                            <Database className="h-3 w-3 shrink-0 text-slate-500" aria-hidden />
                            <span className="text-slate-500">Retrieval</span>
                            <span className="shrink-0 font-mono text-slate-300 whitespace-nowrap">{formatTime(metricsB.retrievalTime)}</span>
                          </div>
                        )}
                        {metricsB.generationTime !== undefined && (
                          <div className="flex items-baseline gap-1.5">
                            <Cpu className="h-3 w-3 shrink-0 text-slate-500" aria-hidden />
                            <span className="text-slate-500">Generation</span>
                            <span className="shrink-0 font-mono text-slate-300 whitespace-nowrap">{formatTime(metricsB.generationTime)}</span>
                          </div>
                        )}
                        {metricsB.promptTokens !== undefined && (
                          <div className="flex items-baseline gap-1.5">
                            <Clock className="h-3 w-3 shrink-0 text-slate-500" aria-hidden />
                            <span className="text-slate-500">Tokens</span>
                            <span className="shrink-0 font-mono text-slate-300 whitespace-nowrap">{formatNumber(metricsB.promptTokens)}</span>
                          </div>
                        )}
                      </div>
                    </div>
                  </>
                )
              })()}
            </section>
          </div>
        </div>
      </div>
    </div>
  )
}
