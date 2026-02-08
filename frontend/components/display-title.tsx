"use client"

/**
 * Renders text with a Sagittaire Display-style un-unified pattern:
 * alternating letter sizes, baseline shifts, and mixed italic for a playful serif look.
 */
export function DisplayTitle({ children, className = "" }: { children: string; className?: string }) {
  const chars = children.split("")
  let i = 0

  return (
    <span className={`inline-block font-serif font-bold ${className}`}>
      {chars.map((char, idx) => {
        if (char === " ") {
          return <span key={idx} className="inline-block w-[0.25em]" aria-hidden />
        }
        const pos = i++
        const sizeVariant = pos % 2 === 0 ? "big" : "small"
        const baselineVariant = pos % 3
        const useItalic = pos % 3 === 1

        const fontSize = sizeVariant === "big" ? "1.05em" : "0.82em"
        const verticalAlign =
          baselineVariant === 0 ? "0" : baselineVariant === 1 ? "-0.12em" : "0.08em"

        return (
          <span
            key={idx}
            className="inline-block"
            style={{
              fontSize,
              verticalAlign,
              fontStyle: useItalic ? "italic" : "normal",
              lineHeight: 1,
            }}
          >
            {char}
          </span>
        )
      })}
    </span>
  )
}
