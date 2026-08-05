"use client"

import React, { useState } from "react"
import { FileText, Download, Terminal, Play, Copy, PanelRightClose } from "lucide-react"
import { Button } from "@/components/ui/button"

interface EvidencePanelProps {
  onClose?: () => void
}

export function EvidencePanel({ onClose }: EvidencePanelProps) {
  const [activeTab, setActiveTab] = useState<"evidence" | "code">("evidence")

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
            <div className="rounded-lg border border-white/10 bg-card overflow-hidden">
              <div className="p-3 border-b border-white/10 flex items-start gap-3 bg-white/5">
                <FileText className="w-4 h-4 text-primary shrink-0 mt-0.5" />
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium truncate text-foreground">BCTC_HPG_2023.pdf</p>
                  <p className="text-xs text-muted-foreground mt-0.5">Page 12 • KQKDHN Table</p>
                </div>
              </div>
              <div className="p-3 bg-card text-xs">
                <table className="w-full text-left border-collapse">
                  <thead>
                    <tr className="text-muted-foreground border-b border-white/10">
                      <th className="pb-2 font-medium">Chỉ tiêu</th>
                      <th className="pb-2 font-medium text-right">Năm 2023</th>
                    </tr>
                  </thead>
                  <tbody className="text-foreground">
                    <tr className="border-b border-white/5">
                      <td className="py-2 bg-primary/10 font-medium">1. Doanh thu bán hàng</td>
                      <td className="py-2 text-right bg-primary/10">118,953</td>
                    </tr>
                    <tr>
                      <td className="py-2 text-muted-foreground">5. Lợi nhuận gộp</td>
                      <td className="py-2 text-right text-muted-foreground">12,450</td>
                    </tr>
                    <tr className="border-t border-white/5">
                      <td className="py-2 bg-primary/10 font-medium">11. LN sau thuế</td>
                      <td className="py-2 text-right bg-primary/10">6,800</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {activeTab === "code" && (
          <div className="flex flex-col h-full">
            <div className="flex-1 bg-[#09090B] p-4 overflow-auto text-xs font-mono leading-relaxed text-[#d4d4d4]">
              <div className="text-blue-400">import <span className="text-[#d4d4d4]">pandas</span> as <span className="text-[#d4d4d4]">pd</span></div>
              <div className="text-blue-400">import <span className="text-[#d4d4d4]">duckdb</span></div>
              <br/>
              <div className="text-green-600"># Connect to hybrid database</div>
              <div>con = duckdb.connect(<span className="text-orange-300">'finagent.db'</span>)</div>
              <br/>
              <div className="text-green-600"># Fetch data for HPG 2023</div>
              <div>df = con.execute(<span className="text-orange-300">"""</span></div>
              <div className="text-orange-300">  SELECT * FROM kqkndhn_2023 </div>
              <div className="text-orange-300">  WHERE company = 'HPG'</div>
              <div><span className="text-orange-300">"""</span>).df()</div>
            </div>
            
            <div className="h-40 border-t border-white/10 bg-card p-4 overflow-auto font-mono text-xs">
              <div className="text-muted-foreground mb-2 flex items-center justify-between">
                <span>Execution Result:</span>
                <span className="text-emerald-500">Success (14ms)</span>
              </div>
              <div className="text-foreground">
                Revenue: 118,953<br/>
                Net Profit: 6,800
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
