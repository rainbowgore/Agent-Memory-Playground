"use client"

import { useEffect, useCallback } from "react"
import { Keyboard, X } from "lucide-react"

// --------------------------------------------------------------------------------------
// Key cap styling for shortcut display
// --------------------------------------------------------------------------------------

function KeyCap({ children }: { children: React.ReactNode }) {
  return (
    <kbd className="keycap-custom inline-flex h-6 min-w-[1.5rem] items-center justify-center rounded border px-1.5 py-0.5 font-mono text-xs text-slate-200 shadow-sm">
      {children}
    </kbd>
  )
}

const SHORTCUTS = [
  { keys: ["Ctrl", "Enter"], label: "Send message" },
  { keys: ["Ctrl", "Shift", "Enter"], label: "Send to both agents" },
  { keys: ["Ctrl", "K"], label: "Clear agent memory" },
  { keys: ["Ctrl", "/"], label: "Focus message input" },
] as const

export function ShortcutsModal({
  open,
  onClose,
}: {
  open: boolean
  onClose: () => void
}) {
  const handleEscape = useCallback(
    (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose()
    },
    [onClose]
  )

  useEffect(() => {
    if (!open) return
    window.addEventListener("keydown", handleEscape)
    return () => window.removeEventListener("keydown", handleEscape)
  }, [open, handleEscape])

  if (!open) return null

  return (
    <>
      <button
        type="button"
        onClick={onClose}
        className="fixed inset-0 z-40 bg-black/60 backdrop-blur-[2px]"
        aria-label="Close shortcuts"
      />
      <div
        className="shortcuts-modal-custom fixed left-1/2 top-1/2 z-50 w-full max-w-sm -translate-x-1/2 -translate-y-1/2 rounded-xl border bg-[#1a1a1a]/95 px-5 py-4 shadow-xl"
        role="dialog"
        aria-modal="true"
        aria-labelledby="shortcuts-title"
      >
        <div className="mb-3 flex items-center justify-between">
          <h2
            id="shortcuts-title"
            className="flex items-center gap-2 text-sm font-semibold text-slate-100"
          >
            <Keyboard className="h-4 w-4 text-white" />
            Shortcuts
          </h2>
          <button
            type="button"
            onClick={onClose}
            className="rounded p-1 text-slate-400 transition hover:bg-slate-700 hover:text-slate-100"
            aria-label="Close"
          >
            <X className="h-4 w-4" />
          </button>
        </div>
        <ul className="space-y-2.5 text-sm">
          {SHORTCUTS.map(({ keys, label }) => (
            <li
              key={label}
              className="flex flex-wrap items-center gap-2 text-slate-300"
            >
              <span className="flex items-center gap-1">
                {keys.map((k, i) => (
                  <span key={`${label}-${i}`} className="flex items-center gap-1">
                    {i > 0 && <span className="text-white">+</span>}
                    <KeyCap>{k}</KeyCap>
                  </span>
                ))}
              </span>
              <span className="text-slate-400">-</span>
              <span className="text-white">{label}</span>
            </li>
          ))}
        </ul>
        <p className="mt-3 text-xs text-white">
          Use Cmd on Mac instead of Ctrl.
        </p>
      </div>
    </>
  )
}

export function ShortcutsTrigger({ onClick }: { onClick: () => void }) {
  return (
    <button
      type="button"
      onClick={onClick}
      className="rounded-lg p-2 text-white transition hover:bg-window hover:text-slate-100"
      aria-label="Show keyboard shortcuts"
      title="Keyboard shortcuts"
    >
      <Keyboard className="h-4 w-4" />
    </button>
  )
}
