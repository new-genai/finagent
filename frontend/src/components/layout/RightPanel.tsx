"use client"

import React from "react"
import { Activity, Server, Database, BrainCircuit, Search, FileCog, Layers } from "lucide-react"

export function RightPanel() {
  const services = [
    { name: "FastAPI Core", icon: Server, latency: "12ms", status: "Operational", color: "text-blue-500" },
    { name: "DuckDB", icon: Database, latency: "4ms", status: "Operational", color: "text-emerald-500" },
    { name: "Vector Store", icon: Layers, latency: "18ms", status: "Operational", color: "text-indigo-500" },
    { name: "LLM (Qwen 7B)", icon: BrainCircuit, latency: "450ms", status: "Operational", color: "text-purple-500" },
    { name: "Embedding Model", icon: BrainCircuit, latency: "85ms", status: "Operational", color: "text-pink-500" },
    { name: "Retriever", icon: Search, latency: "24ms", status: "Operational", color: "text-orange-500" },
    { name: "Indexer", icon: FileCog, latency: "-", status: "Idle", color: "text-muted-foreground" },
  ]

  return (
    <aside className="w-full h-full border border-white/5 rounded-xl bg-card/30 p-4 flex flex-col gap-4">
      <div className="flex items-center justify-between pb-3 border-b border-white/5">
        <div className="flex items-center gap-2">
          <Activity className="w-4 h-4 text-primary" />
          <h3 className="font-medium text-xs text-foreground uppercase tracking-wider">System Status</h3>
        </div>
        <span className="flex h-2 w-2 rounded-full bg-emerald-500 animate-pulse" />
      </div>
      
      <div className="flex flex-col gap-2 flex-1 overflow-y-auto pr-1">
        {services.map((service, i) => (
          <div key={i} className="bg-[#09090B]/50 p-3 rounded-lg border border-white/5 flex flex-col gap-1.5 hover:bg-white/5 transition-colors">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 text-xs font-medium text-foreground">
                <service.icon className={`w-3.5 h-3.5 ${service.color}`} />
                {service.name}
              </div>
              <span className={`w-1.5 h-1.5 rounded-full ${service.status === 'Operational' ? 'bg-emerald-500' : 'bg-muted-foreground'}`} />
            </div>
            <div className="flex justify-between items-center text-[11px] text-muted-foreground">
              <span>{service.status}</span>
              <span className="font-mono">{service.latency}</span>
            </div>
          </div>
        ))}
      </div>
    </aside>
  )
}
