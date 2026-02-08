"use client"

export function CircuitBackground() {
  return (
    <div
      className="fixed inset-0 -z-10 bg-black"
      aria-hidden
    >
      <svg
        className="h-full w-full"
        viewBox="0 0 800 600"
        preserveAspectRatio="xMidYMid slice"
      >
        <defs>
          <linearGradient
            id="bg-vertical"
            x1="0"
            y1="0"
            x2="0"
            y2="1"
          >
            <stop offset="0%" stopColor="#000000" />
            <stop offset="38%" stopColor="#000000" />
            <stop offset="50%" stopColor="#0a1614" />
            <stop offset="70%" stopColor="#0f2d2a" />
            <stop offset="85%" stopColor="#134e4a" />
            <stop offset="100%" stopColor="#0d9488" />
          </linearGradient>
          <pattern
            id="bg-grid"
            width="5"
            height="5"
            patternUnits="userSpaceOnUse"
          >
            <rect x="0" y="0" width="4" height="4" fill="white" />
          </pattern>
          <mask id="bg-mask">
            <rect width="100%" height="100%" fill="url(#bg-grid)" />
          </mask>
        </defs>
        <rect width="100%" height="100%" fill="#000000" />
        <rect
          width="100%"
          height="100%"
          fill="url(#bg-vertical)"
          mask="url(#bg-mask)"
        />
      </svg>
    </div>
  )
}
