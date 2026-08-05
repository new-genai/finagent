"use client"

import React, { useState } from "react"
import { GridPattern } from "@/components/ui/backgrounds/GridPattern"
import { BorderBeam } from "@/components/ui/animations/BorderBeam"
import { AnimatedBeam } from "@/components/ui/animations/AnimatedBeam"
import { Search, MessageSquare, Database, FileText, BarChart2, ArrowRight } from "lucide-react"

export default function DashboardPage() {
  const [searchQuery, setSearchQuery] = useState("")

  return (
    <div className="flex flex-col gap-12 w-full max-w-5xl mx-auto pb-10" suppressHydrationWarning>
      
      {/* Hero Section */}
      <div className="relative rounded-3xl border border-white/10 bg-card/50 overflow-hidden mt-6 p-12 text-center flex flex-col items-center justify-center shadow-2xl" suppressHydrationWarning>
        <GridPattern
          width={40}
          height={40}
          x={-1}
          y={-1}
          className="absolute inset-0 h-full w-full opacity-30 [mask-image:linear-gradient(to_bottom_right,white,transparent,transparent)]"
        />
        <BorderBeam duration={12} delay={9} />
        
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 border border-primary/20 text-primary text-xs font-medium mb-6 relative z-10" suppressHydrationWarning>
          <span className="flex h-2 w-2 rounded-full bg-primary animate-pulse" />
          AI Guru 2026 Ready
        </div>

        <h1 className="text-4xl md:text-5xl font-bold tracking-tight text-foreground mb-4 relative z-10">
          NewGenAI <span className="text-gradient">Financial Agent</span>
        </h1>
        <p className="text-muted-foreground text-sm md:text-base max-w-2xl mb-10 relative z-10">
          AI-powered Financial Table Retrieval & Text-to-Pandas platform designed for deep research and robust data execution.
        </p>

        {/* Giant Search Box */}
        <div className="relative w-full max-w-2xl z-10" suppressHydrationWarning>
          <div className="absolute inset-0 bg-primary/20 blur-xl rounded-2xl" suppressHydrationWarning />
          <div className="relative flex items-center bg-[#09090B] border border-white/10 rounded-2xl p-2 px-4 shadow-2xl focus-within:ring-2 focus-within:ring-primary/50 transition-all" suppressHydrationWarning>
            <Search className="w-5 h-5 text-muted-foreground mr-3" />
            <input
              suppressHydrationWarning
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Hỏi bất kỳ câu hỏi tài chính nào... (VD: Doanh thu VNM năm 2023?)"
              className="flex-1 bg-transparent border-none outline-none ring-0 py-4 text-base placeholder:text-muted-foreground text-foreground"
            />
            <div className="flex items-center gap-2 absolute right-4 opacity-50 text-xs text-muted-foreground pointer-events-none hidden md:flex" suppressHydrationWarning>
              <kbd className="border border-white/20 rounded px-1.5 py-0.5 bg-white/5">Ctrl</kbd>
              <kbd className="border border-white/20 rounded px-1.5 py-0.5 bg-white/5">K</kbd>
            </div>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div suppressHydrationWarning>
        <h3 className="text-sm font-semibold text-muted-foreground uppercase tracking-wider mb-4">Quick Actions</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4" suppressHydrationWarning>
          {[
            { name: "Chat AI", icon: MessageSquare, color: "from-blue-500/20 to-transparent", border: "group-hover:border-blue-500/50" },
            { name: "Browse Dataset", icon: Database, color: "from-emerald-500/20 to-transparent", border: "group-hover:border-emerald-500/50" },
            { name: "Run Parser", icon: FileText, color: "from-orange-500/20 to-transparent", border: "group-hover:border-orange-500/50" },
            { name: "Evaluate Model", icon: BarChart2, color: "from-purple-500/20 to-transparent", border: "group-hover:border-purple-500/50" },
          ].map((action, i) => (
            <div key={i} className={`group cursor-pointer rounded-xl border border-white/5 bg-card/50 p-5 transition-all hover:bg-card ${action.border} relative overflow-hidden`} suppressHydrationWarning>
              <div className={`absolute inset-0 bg-gradient-to-br ${action.color} opacity-0 group-hover:opacity-100 transition-opacity`} suppressHydrationWarning />
              <action.icon className="w-5 h-5 text-foreground mb-3 relative z-10" />
              <div className="font-medium text-sm text-foreground relative z-10" suppressHydrationWarning>{action.name}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Pipeline Visualization */}
      <div>
        <h3 className="text-sm font-semibold text-muted-foreground uppercase tracking-wider mb-4">Execution Pipeline</h3>
        <div className="rounded-xl border border-white/5 bg-card/30 p-8 flex flex-col gap-6 overflow-hidden relative">
          
          <div className="flex flex-wrap items-center justify-between gap-4 relative z-10">
            {[
              "Question",
              "Hybrid Retrieval",
              "Relevant Tables",
              "LLM",
              "Pandas Query",
              "Execution",
              "Answer"
            ].map((step, i, arr) => (
              <React.Fragment key={step}>
                <div className="px-4 py-2 rounded-lg bg-[#09090B] border border-white/10 text-xs font-medium text-foreground whitespace-nowrap shadow-md">
                  {step}
                </div>
                {i < arr.length - 1 && (
                  <ArrowRight className="w-4 h-4 text-muted-foreground shrink-0 hidden md:block" />
                )}
              </React.Fragment>
            ))}
          </div>

          <AnimatedBeam duration={3} className="h-12 w-full rounded-full" />
          
        </div>
      </div>

    </div>
  )
}
