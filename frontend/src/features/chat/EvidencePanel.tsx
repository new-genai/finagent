"use client"

import React, { useState } from "react"
import { FileText, Download, Terminal, Play, Copy, PanelRightClose } from "lucide-react"
import { Button } from "@/components/ui/button"
import { useChatStore } from "@/store/useChatStore"

interface EvidencePanelProps {
  onClose?: () => void
}

export function EvidencePanel({ onClose }: EvidencePanelProps) {
  const [activeTab, setActiveTab] = useState<"evidence" | "code">("code")
  // Force Turbopack rebuild to clear cached TypeError
  const sessionMessages = useChatStore(state => state.sessions.find(s => s.id === state.currentSessionId)?.messages)
  const messages = sessionMessages || []

  const lastAssistantMsg = [...messages].reverse().find(m => m.role === 'assistant')
  const code = lastAssistantMsg?.thought_process || "No query has been executed yet."
  const tables = lastAssistantMsg?.tables_used || []

  return (
    <div className="w-full h-full flex flex-col">
      <div className="h-12 border-b border-white/5 flex items-center px-2 shrink-0">
        <div className="flex bg-white/5 rounded-md p-0.5">
          <button 
            className={`px-3 py-1 text-xs font-medium rounded-sm transition-colors ${activeTab === 'evidence' ? 'bg-white/10 text-foreground' : 'text-muted-foreground hover:text-foreground'}`}
            onClick={() => setActiveTab('evidence')}
          >
            Evidence
          </button>
          <button 
            className={`px-3 py-1 text-xs font-medium rounded-sm transition-colors ${activeTab === 'code' ? 'bg-white/10 text-foreground' : 'text-muted-foreground hover:text-foreground'}`}
            onClick={() => setActiveTab('code')}
          >
            Pandas Code
          </button>
        </div>
        <div className="flex-1" />
        {onClose && (
          <Button variant="ghost" size="icon" className="h-8 w-8 text-muted-foreground" onClick={onClose}>
            <PanelRightClose className="w-4 h-4" />
          </Button>
        )}
      </div>
      
      <div className="flex-1 overflow-y-auto">
        {activeTab === "evidence" && (
          <div className="p-4 flex flex-col gap-4">
            {tables.length === 0 ? (
              <div className="text-muted-foreground text-sm text-center mt-10">No tables retrieved.</div>
            ) : (
              tables.map((t, idx) => {
                const parts = t.split('.csv');
                const title = parts[0] ? parts[0] + '.csv' : t;
                return (
                  <div key={idx} className="rounded-lg border border-white/10 bg-card overflow-hidden">
                    <div className="p-3 border-b border-white/10 flex items-start gap-3 bg-white/5">
                      <FileText className="w-4 h-4 text-primary shrink-0 mt-0.5" />
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium truncate text-foreground" title={title}>{title}</p>
                        <p className="text-xs text-muted-foreground mt-0.5">Hybrid Search Result</p>
                      </div>
                    </div>
                  </div>
                )
              })
            )}
          </div>
        )}

        {activeTab === "code" && (
          <div className="flex flex-col h-full">
            <div className="flex-1 bg-[#09090B] p-4 overflow-auto text-[13px] font-mono leading-relaxed text-[#d4d4d4]">
              <pre><code>{code}</code></pre>
            </div>
            
            <div className="border-t border-white/10 bg-card p-4 overflow-auto font-mono text-xs">
              <div className="text-muted-foreground mb-2 flex items-center justify-between">
                <span>Execution Status:</span>
                <span className={code !== "No query has been executed yet." ? "text-emerald-500" : "text-muted-foreground"}>
                  {code !== "No query has been executed yet." ? "Auto-Executed" : "Idle"}
                </span>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
