"use client"

import React from "react"
import { usePathname } from "next/navigation"
import { Bell, Search } from "lucide-react"
import { Button } from "@/components/ui/button"

export function Topbar() {
  const pathname = usePathname()

  // Find current page name for header
  const pageName = pathname === "/" 
    ? "Dashboard" 
    : pathname.split("/").filter(Boolean)[0] || ""
  
  const formattedPageName = pageName.charAt(0).toUpperCase() + pageName.slice(1)

  return (
    <header className="h-12 border-b border-white/5 bg-background flex items-center justify-between px-4 shrink-0">
      <div className="flex items-center gap-4 flex-1">
        <h2 className="text-sm font-medium text-foreground">{formattedPageName}</h2>
      </div>
      
      <div className="flex items-center gap-2">
        <Button variant="ghost" size="icon" className="h-8 w-8 text-muted-foreground hover:text-foreground">
          <Search className="w-4 h-4" />
        </Button>
        <Button variant="ghost" size="icon" className="relative h-8 w-8 text-muted-foreground hover:text-foreground">
          <Bell className="w-4 h-4" />
          <span className="absolute top-1.5 right-1.5 w-1.5 h-1.5 bg-primary rounded-full" />
        </Button>
        <div className="w-7 h-7 rounded-full bg-gradient-to-tr from-primary to-accent border border-white/10 ml-2" />
      </div>
    </header>
  )
}
