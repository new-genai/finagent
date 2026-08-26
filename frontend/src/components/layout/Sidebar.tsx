"use client"

import React from "react"
import Link from "next/link"
import { usePathname } from "next/navigation"
import {
  BarChart2,
  Database,
  FileText,
  GitBranch,
  LayoutDashboard,
  MessageSquare,
  Search,
  Send,
  Settings,
} from "lucide-react"

import { cn } from "@/lib/utils"
import { useLanguage } from "@/providers/language-provider"

const workspaceItemsEN = [
  { name: "Dashboard", href: "/", icon: LayoutDashboard, desc: "Live metrics" },
  { name: "Chat", href: "/chat", icon: MessageSquare, desc: "Ask data" },
  { name: "Dataset", href: "/dataset", icon: Database, desc: "Tables" },
  { name: "Parser", href: "/parser", icon: FileText, desc: "Extract" },
]

const analysisItemsEN = [
  { name: "Retrieval", href: "/retrieval", icon: Search, desc: "Search test" },
  { name: "Evaluation", href: "/evaluation", icon: BarChart2, desc: "Scores" },
  { name: "Submission", href: "/submission", icon: Send, desc: "Export" },
]

const workspaceItemsVI = [
  { name: "Tổng quan", href: "/", icon: LayoutDashboard, desc: "Số liệu trực tiếp" },
  { name: "Trò chuyện", href: "/chat", icon: MessageSquare, desc: "Hỏi đáp dữ liệu" },
  { name: "Dữ liệu", href: "/dataset", icon: Database, desc: "Các bảng DuckDB" },
  { name: "Trích xuất", href: "/parser", icon: FileText, desc: "Đọc báo cáo PDF" },
]

const analysisItemsVI = [
  { name: "Truy hồi", href: "/retrieval", icon: Search, desc: "Test tìm kiếm" },
  { name: "Đánh giá", href: "/evaluation", icon: BarChart2, desc: "Chấm điểm mô hình" },
  { name: "Nộp bài", href: "/submission", icon: Send, desc: "Xuất file CSV" },
]

export function Sidebar() {
  const pathname = usePathname()
  const { lang } = useLanguage()

  const workspaceItems = lang === "EN" ? workspaceItemsEN : workspaceItemsVI
  const analysisItems = lang === "EN" ? analysisItemsEN : analysisItemsVI

  return (
    <aside className="hidden h-full w-[248px] shrink-0 border-r border-border bg-card/70 lg:flex lg:flex-col">
      <div className="border-b border-border p-4">
        <Link href="/" className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center border border-primary/30 bg-primary text-sm font-bold text-primary-foreground">
            NG
          </div>
          <div className="min-w-0">
            <div className="font-semibold leading-tight">NewGenAI</div>
            <div className="text-xs text-muted-foreground">Financial Agent</div>
          </div>
        </Link>
      </div>

      <nav className="flex-1 space-y-5 overflow-y-auto p-3">
        <NavGroup label={lang === "EN" ? "Workspace" : "Không gian làm việc"} items={workspaceItems} pathname={pathname} />
        <NavGroup label={lang === "EN" ? "Analysis" : "Phân tích"} items={analysisItems} pathname={pathname} />
      </nav>

      <div className="space-y-2 border-t border-border p-3">
        <SidebarLink
          name={lang === "EN" ? "Settings" : "Cài đặt"}
          href="/settings"
          icon={Settings}
          desc={lang === "EN" ? "Theme & app" : "Giao diện & ƯD"}
          active={pathname === "/settings"}
        />
        <Link
          href="https://github.com/new-genai/finagent"
          target="_blank"
          className="flex items-center gap-3 border border-transparent px-3 py-2.5 text-sm text-muted-foreground transition-colors hover:border-border hover:bg-secondary hover:text-foreground"
        >
          <GitBranch className="h-4 w-4" />
          <span>GitHub</span>
        </Link>
      </div>
    </aside>
  )
}

function NavGroup({
  label,
  items,
  pathname,
}: {
  label: string
  items: Array<{ name: string; href: string; icon: React.ElementType; desc: string }>
  pathname: string
}) {
  return (
    <div className="space-y-2">
      <div className="px-3 text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">
        {label}
      </div>
      <div className="space-y-1">
        {items.map((item) => (
          <SidebarLink
            key={item.href}
            name={item.name}
            href={item.href}
            icon={item.icon}
            desc={item.desc}
            active={pathname === item.href}
          />
        ))}
      </div>
    </div>
  )
}

function SidebarLink({
  name,
  href,
  icon: Icon,
  desc,
  active,
}: {
  name: string
  href: string
  icon: React.ElementType
  desc: string
  active: boolean
}) {
  return (
    <Link
      href={href}
      className={cn(
        "group flex items-center gap-3 border px-3 py-2.5 text-sm transition-colors",
        active
          ? "border-primary/30 bg-primary/10 text-foreground"
          : "border-transparent text-muted-foreground hover:border-border hover:bg-secondary hover:text-foreground",
      )}
    >
      <div
        className={cn(
          "flex h-8 w-8 items-center justify-center border",
          active ? "border-primary/30 bg-primary text-primary-foreground" : "border-border bg-background",
        )}
      >
        <Icon className="h-4 w-4" />
      </div>
      <div className="min-w-0">
        <div className="font-medium leading-tight">{name}</div>
        <div className="text-xs text-muted-foreground">{desc}</div>
      </div>
    </Link>
  )
}
