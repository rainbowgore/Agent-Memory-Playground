interface StrategyBadgeProps {
  strategyType: string
  color?: string
  category?: string
  icon?: string
}

export function StrategyBadge({ 
  strategyType, 
  color = "#a78bfa", 
  category = "Basic",
  icon
}: StrategyBadgeProps) {
  return (
    <div className="flex items-center gap-2">
      <div
        className="h-2 w-2 rounded-full"
        style={{ backgroundColor: color }}
        aria-hidden
      />
      <span className="text-xs text-slate-400 font-medium">
        {strategyType}
      </span>
      {category && (
        <span className="rounded bg-window px-1.5 py-0.5 text-xs text-slate-500">
          {category}
        </span>
      )}
    </div>
  )
}
