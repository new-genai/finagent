"use client"

import React from "react"
import { BarChart2, Target, CheckCircle2, AlertTriangle, ChevronRight } from "lucide-react"

export default function EvaluationPage() {
  return (
    <div className="flex flex-col gap-6 h-full w-full max-w-6xl mx-auto pt-4 pb-10">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-foreground flex items-center gap-2">
            <BarChart2 className="w-6 h-6 text-primary" />
            Model Evaluation
          </h1>
          <p className="text-sm text-muted-foreground mt-1">
            Analyze retrieval performance and answer accuracy on the AI Guru 2026 validation set.
          </p>
        </div>
        <button className="flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-lg text-sm font-medium hover:bg-primary/90 transition-colors">
          Run Evaluation
        </button>
      </div>

      {/* High level Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {[
          { label: "Overall Score", value: "92.4", sub: "Top 5% in Leaderboard", color: "text-emerald-500" },
          { label: "Table Retrieval (Recall@5)", value: "98.1%", sub: "+2.1% from last run", color: "text-blue-500" },
          { label: "Text-to-Pandas Acc", value: "87.3%", sub: "-0.5% regression", color: "text-orange-500" },
          { label: "End-to-End F2", value: "90.8", sub: "Stable", color: "text-purple-500" },
        ].map((metric, i) => (
          <div key={i} className="rounded-xl border border-white/5 bg-card/50 p-5 flex flex-col gap-2 relative overflow-hidden">
            <div className={`absolute top-0 right-0 w-24 h-24 bg-gradient-to-br from-white/5 to-transparent rounded-bl-full -mr-4 -mt-4 pointer-events-none`} />
            <span className="text-sm font-medium text-muted-foreground">{metric.label}</span>
            <div className={`text-3xl font-bold tracking-tight ${metric.color}`}>{metric.value}</div>
            <span className="text-xs text-muted-foreground">{metric.sub}</span>
          </div>
        ))}
      </div>

      {/* Detailed Analysis */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 flex-1 min-h-[400px]">
        
        {/* Error Analysis */}
        <div className="lg:col-span-2 rounded-xl border border-white/5 bg-[#09090B] flex flex-col overflow-hidden shadow-xl">
          <div className="p-4 border-b border-white/5 flex items-center justify-between bg-white/5">
            <h3 className="font-semibold text-sm text-foreground flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-orange-500" />
              Error Analysis & Failure Cases
            </h3>
          </div>
          <div className="p-4 flex-1 overflow-auto flex flex-col gap-3">
            {[
              { q: "Tổng tài sản VCB năm 2023?", err: "Pandas Execution Error", desc: "Column 'Tong_Tai_San' not found in table bcdkt_2023" },
              { q: "Tỷ suất lợi nhuận gộp HPG 2022?", err: "Calculation Error", desc: "Generated code used division by zero logic" },
              { q: "Lợi nhuận gộp VNM 2021?", err: "Retrieval Miss", desc: "Retrieved table kqkndhn_2022 instead of kqkndhn_2021" },
            ].map((err, i) => (
              <div key={i} className="p-4 rounded-lg border border-orange-500/20 bg-orange-500/5 flex flex-col gap-2">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium text-foreground">Q: {err.q}</span>
                  <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded bg-orange-500/20 text-orange-500">{err.err}</span>
                </div>
                <div className="text-xs font-mono text-muted-foreground">{err.desc}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Evaluation Configuration */}
        <div className="rounded-xl border border-white/5 bg-card/30 p-6 flex flex-col gap-6">
          <h3 className="font-semibold text-sm uppercase tracking-wider text-muted-foreground">Configuration</h3>
          
          <div className="space-y-4">
            <div className="flex flex-col gap-1.5">
              <label className="text-xs font-medium text-muted-foreground">Dataset Split</label>
              <select className="w-full bg-[#09090B] border border-white/10 rounded-lg px-3 py-2 text-sm text-foreground outline-none">
                <option>Validation Set (1,000 Q&A)</option>
                <option>Test Set (2,500 Q&A)</option>
              </select>
            </div>
            
            <div className="flex flex-col gap-1.5">
              <label className="text-xs font-medium text-muted-foreground">LLM Model</label>
              <select className="w-full bg-[#09090B] border border-white/10 rounded-lg px-3 py-2 text-sm text-foreground outline-none">
                <option>Qwen2.5-Coder-7B-Instruct</option>
                <option>Llama-3.1-8B-Instruct</option>
              </select>
            </div>

            <div className="flex flex-col gap-1.5">
              <label className="text-xs font-medium text-muted-foreground">Top K Retrieval</label>
              <input type="number" defaultValue={5} className="w-full bg-[#09090B] border border-white/10 rounded-lg px-3 py-2 text-sm text-foreground outline-none" />
            </div>
          </div>
          
          <div className="mt-auto pt-4 border-t border-white/5">
            <button className="w-full flex items-center justify-between px-4 py-2 bg-white/5 hover:bg-white/10 rounded-lg text-sm text-foreground transition-colors">
              <span>View Full Report</span>
              <ChevronRight className="w-4 h-4 text-muted-foreground" />
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
