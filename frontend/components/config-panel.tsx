"use client"

import React, { useState } from "react"
import { GlassPanel } from "@/components/glass-panel"
import { Settings2, ChevronDown, ChevronRight, Sliders, X } from "lucide-react"
import type {
  AgentConfig,
  MasterConfig,
  MemoryType,
  ModelType,
} from "@/lib/types"
import { MEMORY_TYPES, MODEL_TYPES } from "@/lib/types"

function ConfigSelect<T extends string>({
  value,
  onChange,
  options,
}: {
  value: T
  onChange: (v: T) => void
  options: { value: T; label: string }[]
}) {
  return (
    <select
      value={value}
      onChange={(e) => onChange(e.target.value as T)}
      className="w-full rounded-lg border border-windowBorder bg-window px-3 py-2 text-sm text-white focus:border-violet-500 focus:outline-none focus:ring-1 focus:ring-violet-500"
    >
      {options.map((o) => (
        <option key={o.value} value={o.value}>
          {o.label}
        </option>
      ))}
    </select>
  )
}

function ConfigSlider({
  label,
  value,
  min,
  max,
  step,
  onChange,
  display,
}: {
  label: string
  value: number
  min: number
  max: number
  step: number
  onChange: (v: number) => void
  display?: string
}) {
  return (
    <div className="flex flex-col gap-1">
      <div className="flex items-center justify-between">
        <span className="text-xs text-white">{label}</span>
        <span className="font-mono text-xs text-white">{display ?? value}</span>
      </div>
      <input
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={(e) => onChange(Number(e.target.value))}
        className="h-1.5 w-full cursor-pointer appearance-none rounded-full bg-windowBorder accent-violet-600 [&::-webkit-slider-thumb]:h-3 [&::-webkit-slider-thumb]:w-3 [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:bg-violet-500"
      />
    </div>
  )
}

function ConfigToggle({
  label,
  checked,
  onChange,
}: {
  label: string
  checked: boolean
  onChange: (v: boolean) => void
}) {
  return (
    <label className="flex cursor-pointer items-center justify-between">
      <span className="text-xs text-white">{label}</span>
      <button
        type="button"
        role="switch"
        aria-checked={checked}
        onClick={() => onChange(!checked)}
        className={`relative h-5 w-9 rounded-full transition focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-violet-500 ${checked ? "bg-violet-600" : "bg-windowBorder"
          }`}
      >
        <span
          className={`absolute top-0.5 h-4 w-4 rounded-full bg-white shadow transition-transform ${checked ? "left-4" : "left-0.5"
            }`}
        />
      </button>
    </label>
  )
}

function Section({
  title,
  defaultOpen = true,
  children,
}: {
  title: string
  defaultOpen?: boolean
  children: React.ReactNode
}) {
  const [open, setOpen] = useState(defaultOpen)
  return (
    <div className="border-b border-windowBorder last:border-b-0">
      <button
        type="button"
        onClick={() => setOpen(!open)}
        className="flex w-full items-center justify-between bg-transparent px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-white hover:text-slate-100"
      >
        {title}
        {open ? <ChevronDown className="h-3.5 w-3.5" /> : <ChevronRight className="h-3.5 w-3.5" />}
      </button>
      {open && <div className="flex flex-col gap-3 px-4 pb-4 pt-0">{children}</div>}
    </div>
  )
}

function AgentConfigSection({
  agentId,
  config,
  onUpdate,
  defaultOpen = true,
}: {
  agentId: "A" | "B"
  config: AgentConfig
  onUpdate: (cfg: AgentConfig) => void
  defaultOpen?: boolean
}) {
  return (
    <Section title={`Agent ${agentId}`} defaultOpen={defaultOpen}>
      <div className="flex flex-col gap-3">
        <div>
          <label className="mb-1 block text-xs text-white">Memory</label>
          <ConfigSelect<MemoryType>
            value={config.memoryType}
            onChange={(v) => onUpdate({ ...config, memoryType: v })}
            options={MEMORY_TYPES}
          />
        </div>
        <div>
          <label className="mb-1 block text-xs text-white">Model</label>
          <ConfigSelect<ModelType>
            value={config.model}
            onChange={(v) => onUpdate({ ...config, model: v })}
            options={MODEL_TYPES}
          />
        </div>
        <ConfigSlider
          label="Temperature"
          value={config.temperature}
          min={0}
          max={2}
          step={0.1}
          onChange={(v) => onUpdate({ ...config, temperature: v })}
        />
        <ConfigSlider
          label="Max tokens"
          value={config.maxTokens}
          min={256}
          max={8192}
          step={256}
          onChange={(v) => onUpdate({ ...config, maxTokens: v })}
          display={config.maxTokens.toLocaleString()}
        />
        <ConfigSlider
          label="Memory window"
          value={config.memoryWindow}
          min={1}
          max={50}
          step={1}
          onChange={(v) => onUpdate({ ...config, memoryWindow: v })}
        />
        <div>
          <label className="mb-1 block text-xs text-white">System prompt</label>
          <textarea
            value={config.systemPrompt}
            onChange={(e) => onUpdate({ ...config, systemPrompt: e.target.value })}
            rows={3}
            className="scrollbar-thin w-full resize-y rounded-lg border border-windowBorder bg-window px-3 py-2 text-sm text-white placeholder-slate-300 focus:border-violet-500 focus:outline-none focus:ring-1 focus:ring-violet-500"
            placeholder="e.g. You are a helpful assistant."
          />
        </div>
      </div>
    </Section>
  )
}

interface ConfigPanelProps {
  agentAConfig: AgentConfig
  agentBConfig: AgentConfig
  masterConfig: MasterConfig
  onUpdateAgentA: (cfg: AgentConfig) => void
  onUpdateAgentB: (cfg: AgentConfig) => void
  onUpdateMaster: (cfg: MasterConfig) => void
  onClose?: () => void
}

export function ConfigPanel({
  agentAConfig,
  agentBConfig,
  masterConfig,
  onUpdateAgentA,
  onUpdateAgentB,
  onUpdateMaster,
  onClose,
}: ConfigPanelProps) {
  return (
    <GlassPanel className="flex h-full min-h-0 flex-col overflow-hidden">
      <div className="flex shrink-0 items-center justify-between gap-3 border-b border-windowBorder bg-window px-4 py-3">
        <div className="flex min-w-0 items-center gap-3">
          <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg text-violet-400">
            <Settings2 className="h-4 w-4" />
          </div>
          <div className="min-w-0">
            <h3 className="text-sm font-semibold text-white">Configuration</h3>
            <p className="text-xs text-white">Playground settings</p>
          </div>
        </div>
        {onClose && (
          <button
            type="button"
            onClick={onClose}
            className="shrink-0 rounded-lg p-2 text-white transition hover:bg-windowBorder hover:text-slate-100"
            aria-label="Close configuration panel"
          >
            <X className="h-4 w-4" />
          </button>
        )}
      </div>
      <div className="scrollbar-thin min-h-0 flex-1 overflow-y-auto">
        <Section title="Master" defaultOpen={false}>
          <div className="flex items-center gap-2 pb-2">
            <Sliders className="h-3 w-3 text-white" />
            <span className="text-xs font-medium text-white">Global</span>
          </div>
          <ConfigToggle
            label="Sync messages"
            checked={masterConfig.syncMessages}
            onChange={(v) => onUpdateMaster({ ...masterConfig, syncMessages: v })}
          />
          <ConfigToggle
            label="Stream responses"
            checked={masterConfig.streamResponses}
            onChange={(v) => onUpdateMaster({ ...masterConfig, streamResponses: v })}
          />
          <ConfigToggle
            label="Show token count"
            checked={masterConfig.showTokenCount}
            onChange={(v) => onUpdateMaster({ ...masterConfig, showTokenCount: v })}
          />
        </Section>
        <AgentConfigSection agentId="A" config={agentAConfig} onUpdate={onUpdateAgentA} defaultOpen />
        <AgentConfigSection agentId="B" config={agentBConfig} onUpdate={onUpdateAgentB} defaultOpen={false} />
      </div>
    </GlassPanel>
  )
}
