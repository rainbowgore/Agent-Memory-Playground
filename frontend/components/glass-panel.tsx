"use client"

import { cn } from "@/lib/utils"
import type { ReactNode } from "react"

interface GlassPanelProps {
  children: ReactNode
  className?: string
}

export function GlassPanel({ children, className }: GlassPanelProps) {
  return (
    <div
      className={cn(
        "flex flex-col overflow-hidden rounded-xl border border-windowBorder bg-window/90 backdrop-blur-sm shadow-xl shadow-black/20",
        className
      )}
    >
      {children}
    </div>
  )
}
