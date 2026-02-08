"use client"

import { useState, useRef, useEffect } from "react"
import { GlassPanel } from "@/components/glass-panel"
import { Send, RotateCcw } from "lucide-react"
import type { AgentConfig, Message } from "@/lib/types"

const HEADER_ICON_SIZE = 40
const EMPTY_STATE_ICON_SIZE = 168

interface AgentWindowProps {
  agentId: "A" | "B"
  config: AgentConfig
  messages: Message[]
  onSendMessage: (message: string) => void
  onClearMessages: () => void
  onInputChange?: (value: string) => void
  onInputFocus?: () => void
  onSendToBoth?: (message: string) => void
  metrics?: {
    retrievalTime?: number
    generationTime?: number
    promptTokens?: number
  }
}

export function AgentWindow({
  agentId,
  config,
  messages,
  onSendMessage,
  onClearMessages,
  onInputChange,
  onInputFocus,
  onSendToBoth,
  metrics,
}: AgentWindowProps) {
  const [input, setInput] = useState("")
  const endRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages])

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Cmd/Ctrl + K to restart
      if ((e.metaKey || e.ctrlKey) && e.key === "k") {
        e.preventDefault()
        onClearMessages()
      }
      // Cmd/Ctrl + / to focus input
      if ((e.metaKey || e.ctrlKey) && e.key === "/") {
        e.preventDefault()
        inputRef.current?.focus()
      }
    }

    window.addEventListener("keydown", handleKeyDown)
    return () => window.removeEventListener("keydown", handleKeyDown)
  }, [onClearMessages])

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!input.trim()) return
    onSendMessage(input.trim())
    setInput("")
  }

  return (
    <GlassPanel className="flex h-[min(70vh,720px)] min-h-[320px] flex-col">
      <div className="flex shrink-0 items-center justify-between gap-3 border-b border-windowBorder bg-window/90 backdrop-blur-sm px-4 py-3">
        <div className="flex min-w-0 items-center gap-3">
          <div
            className="flex shrink-0 items-center justify-center overflow-hidden rounded-lg text-violet-400"
            style={{ width: HEADER_ICON_SIZE, height: HEADER_ICON_SIZE }}
          >
            {agentId === "A" ? (
              <img
                src="/agent-a-icon.png"
                alt=""
                className="object-contain"
                width={HEADER_ICON_SIZE}
                height={HEADER_ICON_SIZE}
                style={{ width: HEADER_ICON_SIZE, height: HEADER_ICON_SIZE }}
                aria-hidden
              />
            ) : (
              <img
                src="/agent-b-icon.png"
                alt=""
                className="object-contain"
                width={HEADER_ICON_SIZE}
                height={HEADER_ICON_SIZE}
                style={{ width: HEADER_ICON_SIZE, height: HEADER_ICON_SIZE }}
                aria-hidden
              />
            )}
          </div>
          <div className="min-w-0 flex-1">
            <h2 className="font-semibold text-slate-100">Agent {agentId}</h2>
            <p className="font-mono text-xs text-white truncate">
              {config.memoryType} · {config.model}
            </p>
          </div>
        </div>
        <button
          type="button"
          onClick={onClearMessages}
          className="rounded-lg p-2 text-white/70 transition hover:bg-windowBorder hover:text-white/90"
          aria-label="Restart conversation (Cmd+K)"
          title="Restart conversation (Cmd+K)"
        >
          <RotateCcw className="h-4 w-4" />
        </button>
      </div>

      <div className="scrollbar-thin min-h-0 flex-1 overflow-y-auto px-4 py-3">
        {messages.length === 0 ? (
          <div className="flex min-h-[200px] flex-col items-center justify-center gap-2 text-center">
            {agentId === "A" ? (
            <img
              src="/sloth-icon.png"
              alt=""
              className="object-contain"
              width={EMPTY_STATE_ICON_SIZE}
              height={EMPTY_STATE_ICON_SIZE}
              style={{ width: EMPTY_STATE_ICON_SIZE, height: EMPTY_STATE_ICON_SIZE }}
              aria-hidden
            />
          ) : (
            <img
              src="/oct.png"
              alt=""
              className="object-contain"
              width={EMPTY_STATE_ICON_SIZE}
              height={EMPTY_STATE_ICON_SIZE}
              style={{ width: EMPTY_STATE_ICON_SIZE, height: EMPTY_STATE_ICON_SIZE }}
              aria-hidden
            />
          )}
            <p className="text-sm text-white">Send a message to start</p>
            <p className="text-xs text-slate-200">Cmd+/ to focus input</p>
          </div>
        ) : (
          <div className="flex flex-col gap-3">
            {messages.map((msg) => (
              <div
                key={msg.id}
                className={msg.role === "user" ? "flex justify-end" : "flex justify-start"}
              >
                <div
                  className={
                    msg.role === "user"
                      ? "max-w-[85%] rounded-lg bg-violet-600 px-3 py-2 text-sm text-white shadow-sm"
                      : "max-w-[85%] rounded-lg border border-windowBorder bg-window/80 px-3 py-2 text-sm text-white shadow-sm backdrop-blur-sm"
                  }
                >
                  {msg.content}
                </div>
              </div>
            ))}
            <div ref={endRef} />
          </div>
        )}
      </div>

      <form onSubmit={handleSubmit} className="shrink-0 border-t border-windowBorder bg-window/90 backdrop-blur-sm p-3">
        <div className="flex gap-2">
          <input
            ref={inputRef}
            type="text"
            value={input}
            onChange={(e) => {
              setInput(e.target.value)
              onInputChange?.(e.target.value)
            }}
            onFocus={() => onInputFocus?.()}
            placeholder="Type a message"
            className="min-w-0 flex-1 rounded-lg border border-windowBorder bg-window/20 px-3 py-2 text-sm text-white placeholder-white/70 focus:border-violet-500 focus:outline-none focus:ring-1 focus:ring-violet-500 transition"
            aria-label="Message input"
            onKeyDown={(e) => {
              if ((e.metaKey || e.ctrlKey) && e.shiftKey && e.key === "Enter") {
                e.preventDefault()
                if (input.trim() && onSendToBoth) {
                  onSendToBoth(input.trim())
                  setInput("")
                }
              } else if ((e.metaKey || e.ctrlKey) && e.key === "Enter") {
                e.preventDefault()
                handleSubmit(e)
              }
            }}
          />
          <button
            type="submit"
            disabled={!input.trim()}
            className="shrink-0 rounded-lg bg-violet-600 px-3 py-2 text-white transition hover:bg-violet-700 disabled:opacity-50 disabled:cursor-not-allowed active:scale-95"
            aria-label="Send (Cmd+Enter)"
            title="Send (Cmd+Enter)"
          >
            <Send className="h-4 w-4" />
          </button>
        </div>
      </form>
    </GlassPanel>
  )
}

