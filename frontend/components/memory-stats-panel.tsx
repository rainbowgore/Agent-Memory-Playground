import { GlassPanel } from "@/components/glass-panel"
import { Activity, Clock, Cpu, Database } from "lucide-react"
import { formatTime, formatNumber } from "@/lib/utils"
import type { MemoryStats } from "@/lib/types"

interface MemoryStatsPanelProps {
  stats: MemoryStats | null
  retrievalTime?: number
  generationTime?: number
  promptTokens?: number
}

export function MemoryStatsPanel({
  stats,
  retrievalTime,
  generationTime,
  promptTokens,
}: MemoryStatsPanelProps) {
  if (!stats && !retrievalTime && !generationTime && !promptTokens) {
    return null
  }

  return (
    <GlassPanel className="p-3">
      <div className="flex items-center gap-2 mb-3">
        <Activity className="h-3.5 w-3.5 text-violet-400" />
        <h4 className="text-xs font-semibold text-slate-300 uppercase tracking-wide">
          Performance Metrics
        </h4>
      </div>

      <div className="grid grid-cols-2 gap-2">
        {retrievalTime !== undefined && (
          <div className="flex items-start gap-2 rounded-lg bg-window p-2">
            <Database className="h-3.5 w-3.5 text-slate-400 mt-0.5" />
            <div className="min-w-0 flex-1">
              <div className="text-xs text-slate-500">Retrieval</div>
              <div className="font-mono text-sm font-semibold text-slate-200">
                {formatTime(retrievalTime)}
              </div>
            </div>
          </div>
        )}

        {generationTime !== undefined && (
          <div className="flex items-start gap-2 rounded-lg bg-window p-2">
            <Cpu className="h-3.5 w-3.5 text-slate-400 mt-0.5" />
            <div className="min-w-0 flex-1">
              <div className="text-xs text-slate-500">Generation</div>
              <div className="font-mono text-sm font-semibold text-slate-200">
                {formatTime(generationTime)}
              </div>
            </div>
          </div>
        )}

        {promptTokens !== undefined && (
          <div className="flex items-start gap-2 rounded-lg bg-window p-2">
            <Clock className="h-3.5 w-3.5 text-slate-400 mt-0.5" />
            <div className="min-w-0 flex-1">
              <div className="text-xs text-slate-500">Tokens</div>
              <div className="font-mono text-sm font-semibold text-slate-200">
                {formatNumber(promptTokens)}
              </div>
            </div>
          </div>
        )}
      </div>

      {stats && (
        <div className="mt-3 space-y-1 border-t border-windowBorder pt-2">
          <div className="flex items-center justify-between text-xs">
            <span className="text-slate-500">Strategy</span>
            <span className="font-mono text-slate-300">{stats.strategy_type}</span>
          </div>
          {stats.memory_size && (
            <div className="flex items-center justify-between text-xs">
              <span className="text-slate-500">Memory</span>
              <span className="font-mono text-slate-300">{stats.memory_size}</span>
            </div>
          )}
        </div>
      )}
    </GlassPanel>
  )
}
