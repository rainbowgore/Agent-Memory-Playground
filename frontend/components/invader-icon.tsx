"use client"

/**
 * Space Invaders crab alien pixel art (9x8).
 * Optional pixel cowboy hat on top for Agent B.
 */
const PIXEL_MAP = [
  [0, 1, 1, 1, 0, 1, 1, 1, 0], // .XXX.XXX.
  [1, 1, 1, 1, 1, 1, 1, 1, 1], // XXXXXXXXX
  [1, 1, 1, 1, 1, 1, 1, 1, 1],
  [1, 0, 1, 1, 1, 1, 1, 0, 1], // X.XXXXX.X (eyes)
  [1, 1, 1, 1, 1, 1, 1, 1, 1],
  [1, 0, 1, 0, 1, 0, 1, 0, 1], // X.X.X.X.X
  [0, 1, 1, 0, 0, 0, 1, 1, 0], // .XX...XX.
  [1, 0, 0, 0, 1, 0, 0, 0, 1], // X...X...X
]

/** Pixel cowboy hat (11 wide): wide brim, tapered crown. */
const HAT_MAP = [
  [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], // wide brim
  [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0], // brim underside
  [0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0], // crown base
  [0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0], // crown
  [0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0], // crown top / crease
]

const HAT_WIDTH = 11
const HAT_HEIGHT = 5
const INVADER_WIDTH = 9
const INVADER_BODY_X = (HAT_WIDTH - INVADER_WIDTH) / 2 // 1, so invader centered under hat

interface InvaderIconProps {
  className?: string
  "aria-hidden"?: boolean
  cowboyHat?: boolean
}

export function InvaderIcon({ className, "aria-hidden": ariaHidden, cowboyHat = false }: InvaderIconProps) {
  const width = cowboyHat ? HAT_WIDTH : 9
  const height = cowboyHat ? HAT_HEIGHT + 8 : 8
  const bodyYOffset = cowboyHat ? HAT_HEIGHT : 0
  const bodyXOffset = cowboyHat ? INVADER_BODY_X : 0

  return (
    <svg
      viewBox={`0 0 ${width} ${height}`}
      className={className}
      aria-hidden={ariaHidden}
      fill="currentColor"
      preserveAspectRatio="xMidYMid meet"
    >
      {cowboyHat &&
        HAT_MAP.map((row, y) =>
          row.map((filled, x) =>
            filled ? (
              <rect key={`hat-${y}-${x}`} x={x} y={y} width={1} height={1} />
            ) : null
          )
        )}
      {PIXEL_MAP.map((row, y) =>
        row.map((filled, x) =>
          filled ? (
            <rect
              key={`body-${y}-${x}`}
              x={x + bodyXOffset}
              y={y + bodyYOffset}
              width={1}
              height={1}
            />
          ) : null
        )
      )}
    </svg>
  )
}
