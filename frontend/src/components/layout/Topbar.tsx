"use client"

import React from "react"
import Link from "next/link"
import { usePathname } from "next/navigation"
import { useTheme } from "next-themes"
import { Bell, Menu, Moon, Search, Sun } from "lucide-react"

const pageLabels: Record<string, string> = {
  "/": "Dashboard",
  "/chat": "Chat",
  "/dataset": "Dataset",
  "/parser": "Parser",
  "/retrieval": "Retrieval",
  "/evaluation": "Evaluation",
  "/submission": "Submission",
  "/settings": "Settings",
}

export function Topbar() {
  const pathname = usePathname()
  const { resolvedTheme, setTheme } = useTheme()
  const isDark = resolvedTheme === "dark"
  const formattedPageName = pageLabels[pathname] ?? "Workspace"

  return (
    <header className="h-14 shrink-0 border-b border-border bg-background/95 px-4 backdrop-blur md:px-6">
      <div className="flex h-full items-center justify-between gap-4">
        <div className="flex min-w-0 items-center gap-3">
          <Link
            href="/"
            className="flex h-9 w-9 items-center justify-center border border-border bg-card text-muted-foreground transition-colors hover:text-foreground lg:hidden"
            title="Dashboard"
          >
            <Menu className="h-4 w-4" />
          </Link>
          <div className="min-w-0">
            <h2 className="truncate text-sm font-semibold tracking-tight text-foreground">{formattedPageName}</h2>
            <p className="hidden text-xs text-muted-foreground sm:block">Live financial data workspace</p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button className="hidden min-w-[240px] items-center gap-2 border border-border bg-card px-3 py-2 text-left text-sm text-muted-foreground transition-colors hover:text-foreground md:flex">
            <Search className="h-4 w-4" />
            <span className="flex-1">Search tables, reports...</span>
          </button>
          <button
            onClick={() => setTheme(isDark ? "light" : "dark")}
            className="flex h-9 w-9 items-center justify-center border border-border bg-card text-muted-foreground transition-colors hover:text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
            title={isDark ? "Switch to light" : "Switch to dark"}
          >
            {isDark ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
          </button>
          <button className="relative flex h-9 w-9 items-center justify-center border border-border bg-card text-muted-foreground transition-colors hover:text-foreground">
            <Bell className="h-4 w-4" />
            <span className="absolute right-2 top-2 h-1.5 w-1.5 bg-primary" />
          </button>
          <div className="flex h-9 w-9 items-center justify-center border border-border bg-secondary text-xs font-bold">
            H
          </div>
        </div>
      </div>
    </header>
  )
}
