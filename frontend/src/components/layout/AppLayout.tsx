"use client"

import React from "react"
import { Sidebar } from "./Sidebar"
import { Topbar } from "./Topbar"
import { RightPanel } from "./RightPanel"
import { useAppStore } from "@/store/useAppStore"
import { usePathname } from "next/navigation"

interface AppLayoutProps {
  children: React.ReactNode
}

export function AppLayout({ children }: AppLayoutProps) {
  const { isSidebarOpen } = useAppStore()
  const pathname = usePathname()
  
  const showRightPanel = pathname === "/" || pathname === "/chat"

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-background">
      <Sidebar />
      <div className="flex flex-1 flex-col overflow-hidden relative">
        <Topbar />
        <main className="flex-1 overflow-auto">
          <div className="min-h-full w-full mx-auto p-4 md:p-6 lg:p-8 flex">
            <div className="flex-1 flex flex-col min-w-0">
              {children}
            </div>
            {showRightPanel && (
              <div className="hidden xl:block w-[300px] ml-6 shrink-0 h-full">
                <RightPanel />
              </div>
            )}
          </div>
        </main>
      </div>
    </div>
  )
}
