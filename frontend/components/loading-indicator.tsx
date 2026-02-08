interface LoadingIndicatorProps {
  size?: "sm" | "md" | "lg"
  label?: string
}

export function LoadingIndicator({ size = "md", label }: LoadingIndicatorProps) {
  const sizeClasses = {
    sm: "h-4 w-4 border-2",
    md: "h-6 w-6 border-2",
    lg: "h-8 w-8 border-3",
  }

  return (
    <div className="flex items-center justify-center gap-2">
      <div
        className={`${sizeClasses[size]} animate-spin rounded-full border-violet-500 border-t-transparent`}
        role="status"
        aria-label="Loading"
      />
      {label && <span className="text-sm text-slate-400">{label}</span>}
    </div>
  )
}
