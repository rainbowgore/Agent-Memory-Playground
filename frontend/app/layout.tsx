import React from "react"
import type { Metadata, Viewport } from "next"
import { Bricolage_Grotesque, IBM_Plex_Mono, Instrument_Serif } from "next/font/google"
import { CircuitBackground } from "@/components/circuit-background"
import "./globals.css"

const bricolage = Bricolage_Grotesque({
  subsets: ["latin"],
  variable: "--font-sans",
  display: "swap",
})

const ibmPlexMono = IBM_Plex_Mono({
  weight: ["400", "500"],
  subsets: ["latin"],
  variable: "--font-mono",
  display: "swap",
})

const instrumentSerif = Instrument_Serif({
  weight: "400",
  style: ["normal", "italic"],
  subsets: ["latin"],
  variable: "--font-serif",
  display: "swap",
})

export const metadata: Metadata = {
  title: "Agent Memory Playground",
  description: "Test and compare agent memory techniques side by side",
  icons: {
    icon: "/ferris-wheel.png",
  },
}

export const viewport: Viewport = {
  themeColor: "#0f172a",
}

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html
      lang="en"
      className={`${bricolage.variable} ${ibmPlexMono.variable} ${instrumentSerif.variable}`}
      suppressHydrationWarning
    >
      <body className="min-h-screen bg-black text-slate-50 antialiased">
        <CircuitBackground />
        <div className="relative z-10">{children}</div>
      </body>
    </html>
  )
}
