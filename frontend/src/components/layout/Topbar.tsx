"use client"

import React from "react"
import Link from "next/link"
import { usePathname } from "next/navigation"
import { useTheme } from "next-themes"
import { Bell, Menu, Moon, Search, Sun, Globe } from "lucide-react"
import { useLanguage } from "@/providers/language-provider"

const pageLabelsEN: Record<string, string> = {
  "/": "Dashboard",
  "/chat": "Chat",
  "/dataset": "Dataset",
  "/parser": "Parser",
  "/retrieval": "Retrieval",
  "/evaluation": "Evaluation",
  "/submission": "Submission",
  "/settings": "Settings",
}

const pageLabelsVI: Record<string, string> = {
  "/": "Tổng quan",
  "/chat": "Trò chuyện",
  "/dataset": "Dữ liệu",
  "/parser": "Trích xuất",
  "/retrieval": "Truy hồi",
  "/evaluation": "Đánh giá",
  "/submission": "Nộp bài",
  "/settings": "Cài đặt",
}

export function Topbar() {
  const pathname = usePathname()
  const { resolvedTheme, setTheme } = useTheme()
  const { lang, toggleLang } = useLanguage()
  const [mounted, setMounted] = React.useState(false)

  React.useEffect(() => {
    setMounted(true)
  }, [])

  const isDark = mounted && resolvedTheme === "dark"
  const pageLabels = lang === "EN" ? pageLabelsEN : pageLabelsVI
  const formattedPageName = pageLabels[pathname] ?? (lang === "EN" ? "Workspace" : "Không gian làm việc")

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
            <p className="hidden text-xs text-muted-foreground sm:block">
              {lang === "EN" ? "Live financial data workspace" : "Không gian dữ liệu tài chính trực tiếp"}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button className="hidden min-w-[240px] items-center gap-2 border border-border bg-card px-3 py-2 text-left text-sm text-muted-foreground transition-colors hover:text-foreground md:flex">
            <Search className="h-4 w-4" />
            <span className="flex-1">{lang === "EN" ? "Search tables, reports..." : "Tìm kiếm bảng, báo cáo..."}</span>
          </button>
          
          {/* Language Toggle */}
          <button
            onClick={toggleLang}
            className="flex h-9 w-9 items-center justify-center border border-border bg-card text-muted-foreground transition-colors hover:text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring relative"
            title={lang === "EN" ? "Switch to Vietnamese" : "Chuyển sang tiếng Anh"}
          >
            <Globe className="h-4 w-4" />
            <span className="absolute -bottom-1 -right-1 text-[8px] font-bold bg-primary text-primary-foreground px-1 rounded-sm">{lang}</span>
          </button>

          {/* Theme Toggle */}
          <button
            onClick={() => setTheme(resolvedTheme === "dark" ? "light" : "dark")}
            className="flex h-9 w-9 items-center justify-center border border-border bg-card text-muted-foreground transition-colors hover:text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
            title={mounted ? (isDark ? (lang === "EN" ? "Switch to light" : "Giao diện sáng") : (lang === "EN" ? "Switch to dark" : "Giao diện tối")) : "..."}
          >
            {mounted ? (isDark ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />) : <div className="h-4 w-4" />}
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
