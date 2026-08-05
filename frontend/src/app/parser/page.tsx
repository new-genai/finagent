"use client"

import React from "react"
import { FileText, Table2, Database, Play, Download, TerminalSquare } from "lucide-react"
import { AnimatedBeam } from "@/components/ui/animations/AnimatedBeam"
import { ShineButton } from "@/components/ui/animations/ShineButton"
import { Button } from "@/components/ui/button"

export default function ParserPage() {
  return (
    <div className="flex flex-col gap-8 h-full w-full max-w-5xl mx-auto pt-4 pb-10">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-foreground">Data Pipeline Parser</h1>
          <p className="text-sm text-muted-foreground mt-1">
            Execute the ETL process to transform raw TXT reports into structured DuckDB databases.
          </p>
        </div>
        <ShineButton className="h-10 px-6 gap-2 bg-primary">
          <Play className="w-4 h-4" />
          Run Pipeline
        </ShineButton>
      </div>

      {/* Pipeline Visualization */}
      <div className="rounded-xl border border-white/5 bg-card/30 p-8 flex flex-col gap-8 relative overflow-hidden">
        <h3 className="font-semibold text-sm uppercase tracking-wider text-muted-foreground mb-2">ETL Workflow</h3>
        
        <div className="flex justify-between items-center relative z-10">
          {[
            { name: "Raw TXT", icon: FileText, status: "completed" },
            { name: "Splitter", icon: FileText, status: "completed" },
            { name: "Table Detect", icon: Table2, status: "active" },
            { name: "Normalize", icon: Table2, status: "pending" },
            { name: "DuckDB", icon: Database, status: "pending" },
          ].map((node, i) => (
            <div key={i} className="flex flex-col items-center gap-3 relative z-10 w-24">
              <div className={`w-12 h-12 rounded-xl flex items-center justify-center border-2 transition-all shadow-xl ${
                node.status === 'completed' ? 'bg-emerald-500/10 border-emerald-500/50 text-emerald-500' :
                node.status === 'active' ? 'bg-primary/20 border-primary shadow-[0_0_15px_rgba(59,130,246,0.5)] text-primary animate-pulse' :
                'bg-[#09090B] border-white/10 text-muted-foreground'
              }`}>
                <node.icon className="w-5 h-5" />
              </div>
              <span className={`text-xs font-medium text-center ${node.status === 'active' ? 'text-primary' : 'text-muted-foreground'}`}>
                {node.name}
              </span>
            </div>
          ))}
        </div>
        
        {/* Connection line behind nodes */}
        <div className="absolute top-[108px] left-12 right-12 h-0.5 bg-white/5 -z-0" />
        <AnimatedBeam duration={4} delay={0} className="absolute top-[107px] left-12 w-1/2 h-1 rounded-full z-0" />
      </div>

      {/* Parser Logs & Stats */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 flex-1 min-h-[400px]">
        {/* Terminal Logs */}
        <div className="lg:col-span-2 rounded-xl border border-white/5 bg-[#09090B] flex flex-col overflow-hidden shadow-2xl relative">
          <div className="h-10 border-b border-white/5 flex items-center px-4 bg-white/5 gap-2">
            <TerminalSquare className="w-4 h-4 text-muted-foreground" />
            <span className="text-xs font-mono text-muted-foreground">parser.log</span>
          </div>
          <div className="p-4 font-mono text-[13px] leading-relaxed text-[#d4d4d4] overflow-auto flex-1">
            <div className="text-emerald-400">➜ Starting pipeline execution...</div>
            <div className="text-muted-foreground">[10:42:01] Loading metadata from data/metadata.json</div>
            <div className="text-muted-foreground">[10:42:02] Found 1245 raw TXT files.</div>
            <div className="text-blue-400">[10:42:05] [SPLIT] Processing VNM_2023_HN.txt...</div>
            <div className="text-muted-foreground">[10:42:06]   &gt; Extracted 42 pages.</div>
            <div className="text-blue-400">[10:42:08] [DETECT] Scanning for tables in VNM_2023_HN...</div>
            <div className="text-orange-300">[10:42:15]   &gt; Found 14 potential tables.</div>
            <div className="text-purple-400 animate-pulse mt-2">⠋ Extracting table structures (2/14)...</div>
          </div>
        </div>

        {/* Stats Panel */}
        <div className="rounded-xl border border-white/5 bg-card/30 flex flex-col p-6 gap-6">
          <h3 className="font-semibold text-sm uppercase tracking-wider text-foreground">Execution Stats</h3>
          
          <div className="space-y-4">
            <div>
              <div className="flex justify-between text-xs mb-1">
                <span className="text-muted-foreground">Overall Progress</span>
                <span className="text-primary font-medium">42%</span>
              </div>
              <div className="h-1.5 w-full bg-white/5 rounded-full overflow-hidden">
                <div className="h-full bg-primary w-[42%]" />
              </div>
            </div>
            
            <div className="pt-4 border-t border-white/5 space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-sm text-muted-foreground">Processed Files</span>
                <span className="text-sm font-medium">1 / 1,245</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-muted-foreground">Tables Extracted</span>
                <span className="text-sm font-medium text-emerald-500">14</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-muted-foreground">Elapsed Time</span>
                <span className="text-sm font-mono">00:01:24</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-muted-foreground">Est. Remaining</span>
                <span className="text-sm font-mono">2h 15m</span>
              </div>
            </div>
          </div>
          
          <div className="mt-auto pt-4 flex gap-2">
            <Button variant="outline" className="w-full h-9 text-xs border-white/10 hover:bg-white/5">
              Stop
            </Button>
            <Button variant="outline" className="w-full h-9 text-xs border-white/10 hover:bg-white/5">
              <Download className="w-3.5 h-3.5 mr-1.5" />
              Logs
            </Button>
          </div>
        </div>
      </div>
    </div>
  )
}
