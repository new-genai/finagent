"use client"

import React from "react"
import Link from "next/link"
import { usePathname } from "next/navigation"
import { motion, AnimatePresence } from "framer-motion"
import { useAppStore } from "@/store/useAppStore"
import { 
  LayoutDashboard, 
  MessageSquare, 
  Database, 
  FileText, 
  Search, 
  BarChart2, 
  Send, 
  Settings,
  GitBranch,
  PanelLeftClose,
  PanelLeftOpen
} from "lucide-react"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"

const menuItems = [
  { name: "Dashboard", href: "/", icon: LayoutDashboard },
  { name: "Chat", href: "/chat", icon: MessageSquare },
  { name: "Dataset", href: "/dataset", icon: Database },
  { name: "Parser", href: "/parser", icon: FileText },
  { name: "Retrieval", href: "/retrieval", icon: Search },
  { name: "Evaluation", href: "/evaluation", icon: BarChart2 },
  { name: "Submission", href: "/submission", icon: Send },
]

export function Sidebar() {
  const { isSidebarOpen, toggleSidebar } = useAppStore()
  const pathname = usePathname()

  return (
    <AnimatePresence initial={false}>
      {isSidebarOpen ? (
        <motion.aside 
          initial={{ width: 0, opacity: 0 }}
          animate={{ width: 260, opacity: 1 }}
          exit={{ width: 0, opacity: 0 }}
          transition={{ duration: 0.3, ease: "easeInOut" }}
          className="flex-shrink-0 h-full border-r border-white/5 bg-[#09090B] flex flex-col overflow-hidden"
        >
          <div className="h-14 flex items-center justify-between px-4">
            <Link href="/" className="flex items-center gap-2 font-bold text-sm text-foreground tracking-tight whitespace-nowrap">
              <div className="w-6 h-6 rounded bg-primary flex items-center justify-center">
                <span className="text-primary-foreground text-xs">N</span>
              </div>
              NewGenAI
            </Link>
            <Button variant="ghost" size="icon" className="h-8 w-8 text-muted-foreground hover:text-foreground" onClick={toggleSidebar}>
              <PanelLeftClose className="w-4 h-4" />
            </Button>
          </div>

          <div className="flex-1 overflow-y-auto py-2 px-3 flex flex-col gap-0.5 mt-2">
            {menuItems.map((item) => {
              const Icon = item.icon
              const isActive = pathname === item.href
              return (
                <Link key={item.href} href={item.href}>
                  <motion.div 
                    whileHover={{ scale: 1.01 }}
                    whileTap={{ scale: 0.98 }}
                    className={cn(
                      "flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-colors whitespace-nowrap",
                      isActive 
                        ? "bg-white/10 text-foreground font-medium" 
                        : "text-muted-foreground hover:bg-white/5 hover:text-foreground"
                    )}
                  >
                    <Icon className="w-4 h-4 shrink-0" />
                    {item.name}
                  </motion.div>
                </Link>
              )
            })}
          </div>

          <div className="p-3 border-t border-white/5 flex flex-col gap-1">
            <Link href="/settings">
              <Button variant="ghost" className="w-full justify-start gap-3 h-10 px-3 text-muted-foreground hover:text-foreground hover:bg-white/5 whitespace-nowrap">
                <Settings className="w-4 h-4 shrink-0" />
                <span className="text-sm">Settings</span>
              </Button>
            </Link>
            <Link href="https://github.com/new-genai/finagent" target="_blank">
              <Button variant="ghost" className="w-full justify-start gap-3 h-10 px-3 text-muted-foreground hover:text-foreground hover:bg-white/5 whitespace-nowrap">
                <GitBranch className="w-4 h-4 shrink-0" />
                <span className="text-sm">Github</span>
              </Button>
            </Link>
          </div>
        </motion.aside>
      ) : (
        <div className="w-14 flex-shrink-0 h-full border-r border-white/5 bg-[#09090B] flex flex-col items-center py-4">
          <Button variant="ghost" size="icon" className="h-8 w-8 text-muted-foreground hover:text-foreground mb-4" onClick={toggleSidebar}>
            <PanelLeftOpen className="w-4 h-4" />
          </Button>
          
          <div className="flex-1 flex flex-col gap-2">
            {menuItems.map((item) => {
              const Icon = item.icon
              const isActive = pathname === item.href
              return (
                <Link key={item.href} href={item.href} title={item.name}>
                  <div className={cn(
                    "w-10 h-10 flex items-center justify-center rounded-lg transition-colors",
                    isActive ? "bg-white/10 text-foreground" : "text-muted-foreground hover:bg-white/5 hover:text-foreground"
                  )}>
                    <Icon className="w-4 h-4" />
                  </div>
                </Link>
              )
            })}
          </div>
        </div>
      )}
    </AnimatePresence>
  )
}
