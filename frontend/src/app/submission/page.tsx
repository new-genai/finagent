"use client"

import React from "react"
import { Send, CheckCircle2, Circle, Play, Download } from "lucide-react"
import { ShineButton } from "@/components/ui/animations/ShineButton"
import { AnimatedBeam } from "@/components/ui/animations/AnimatedBeam"

export default function SubmissionPage() {
  return (
    <div className="flex flex-col gap-8 h-full w-full max-w-4xl mx-auto pt-4 pb-10">
      
      <div className="flex flex-col items-center text-center max-w-2xl mx-auto mt-6">
        <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-primary/20 to-accent/20 flex items-center justify-center border border-white/10 shadow-2xl mb-6">
          <Send className="w-8 h-8 text-primary" />
        </div>
        <h1 className="text-3xl font-bold tracking-tight text-foreground mb-3">AI Guru 2026 Submission</h1>
        <p className="text-muted-foreground">
          Generate the final `submission.json` for the test dataset. This process runs the entire pipeline end-to-end on 2,500 questions.
        </p>
      </div>

      <div className="rounded-2xl border border-white/10 bg-card/50 p-8 shadow-2xl relative overflow-hidden mt-4">
        {/* Decorative background glow */}
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-primary/10 rounded-full blur-[100px] pointer-events-none" />
        
        <h3 className="font-semibold text-sm uppercase tracking-wider text-muted-foreground mb-6 border-b border-white/5 pb-4">Pre-flight Checklist</h3>
        
        <div className="flex flex-col gap-4 mb-10">
          {[
            { name: "Dataset Parser Completed", status: true, detail: "1,245 documents processed into DuckDB" },
            { name: "Vector Index Built", status: true, detail: "Dense & Sparse indices ready" },
            { name: "Test Dataset Loaded", status: true, detail: "test.jsonl loaded (2,500 questions)" },
            { name: "LLM Endpoint Connected", status: true, detail: "Qwen2.5-Coder-7B responding at 45ms" },
            { name: "Submission Format Verified", status: false, detail: "Pending generation" },
          ].map((item, i) => (
            <div key={i} className="flex items-center gap-4">
              {item.status ? (
                <CheckCircle2 className="w-5 h-5 text-emerald-500 shrink-0" />
              ) : (
                <Circle className="w-5 h-5 text-muted-foreground shrink-0" />
              )}
              <div className="flex-1">
                <div className={`text-sm font-medium ${item.status ? 'text-foreground' : 'text-muted-foreground'}`}>{item.name}</div>
                <div className="text-xs text-muted-foreground">{item.detail}</div>
              </div>
            </div>
          ))}
        </div>

        <div className="flex flex-col items-center gap-4 border-t border-white/5 pt-8 relative z-10">
          <ShineButton className="h-12 px-10 gap-2 bg-primary text-base font-medium shadow-[0_0_40px_rgba(59,130,246,0.3)]">
            <Play className="w-4 h-4 fill-current" />
            Generate submission.json
          </ShineButton>
          <div className="text-xs text-muted-foreground">Estimated time: 45 minutes</div>
        </div>
      </div>

      {/* Post-generation actions */}
      <div className="grid grid-cols-2 gap-4 opacity-50 pointer-events-none">
        <button className="flex flex-col items-center justify-center gap-2 h-24 rounded-xl border border-dashed border-white/20 bg-white/5 hover:bg-white/10 transition-colors">
          <Download className="w-5 h-5 text-muted-foreground" />
          <span className="text-sm font-medium">Download JSON</span>
        </button>
        <button className="flex flex-col items-center justify-center gap-2 h-24 rounded-xl border border-dashed border-white/20 bg-white/5 hover:bg-white/10 transition-colors">
          <Send className="w-5 h-5 text-muted-foreground" />
          <span className="text-sm font-medium">Submit to Kaggle</span>
        </button>
      </div>

    </div>
  )
}
