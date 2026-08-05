"use client"

import React from "react"
import { Search, BrainCircuit, AlignLeft, BarChart } from "lucide-react"
import { Button } from "@/components/ui/button"

export default function RetrievalPage() {
  return (
    <div className="flex flex-col gap-6 h-full w-full max-w-5xl mx-auto pt-4 pb-10">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-foreground">Hybrid Retrieval Testing</h1>
          <p className="text-sm text-muted-foreground mt-1">
            Test Vector Similarity and BM25 Search across the DuckDB structured indices.
          </p>
        </div>
      </div>

      <div className="rounded-xl border border-white/5 bg-card/30 p-6 flex gap-4 items-start shadow-sm">
        <div className="flex-1">
          <div className="relative">
            <Search className="w-5 h-5 absolute left-3 top-3 text-muted-foreground" />
            <input 
              type="text" 
              defaultValue="Báo cáo doanh thu và lợi nhuận gộp của Vinamilk năm 2023"
              className="w-full bg-[#09090B] border border-white/10 rounded-lg pl-10 pr-4 py-3 text-sm text-foreground outline-none focus:ring-1 focus:ring-primary/50 shadow-inner"
            />
          </div>
          <div className="flex gap-6 mt-4 px-1">
            <label className="flex items-center gap-2 text-sm text-muted-foreground cursor-pointer">
              <input type="checkbox" defaultChecked className="rounded border-white/20 bg-[#09090B] text-primary focus:ring-primary" />
              Dense Vector (Embedding)
            </label>
            <label className="flex items-center gap-2 text-sm text-muted-foreground cursor-pointer">
              <input type="checkbox" defaultChecked className="rounded border-white/20 bg-[#09090B] text-primary focus:ring-primary" />
              Sparse BM25 (Keyword)
            </label>
            <label className="flex items-center gap-2 text-sm text-muted-foreground cursor-pointer">
              <span className="text-xs">Top K:</span>
              <input type="number" defaultValue={5} className="w-16 bg-[#09090B] border border-white/10 rounded px-2 py-1 text-xs" />
            </label>
          </div>
        </div>
        <Button className="h-12 px-8 bg-primary text-primary-foreground">Search</Button>
      </div>

      <div className="flex-1 flex flex-col gap-4">
        <h3 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground px-1">Top Ranked Results</h3>
        
        <div className="space-y-4">
          {[
            { doc: "VNM_2023_HN.pdf", type: "Table", page: 12, score: 0.965, match: "Doanh thu bán hàng, Lợi nhuận gộp, LN sau thuế..." },
            { doc: "VNM_2023_HN.pdf", type: "Text", page: 4, score: 0.842, match: "...tổng doanh thu thuần hợp nhất năm 2023 đạt 60.368 tỷ đồng..." },
            { doc: "VNM_2022_HN.pdf", type: "Table", page: 12, score: 0.715, match: "Doanh thu bán hàng, Lợi nhuận gộp, LN sau thuế..." },
          ].map((result, i) => (
            <div key={i} className="rounded-xl border border-white/5 bg-card/50 p-5 flex gap-6 hover:bg-card/80 transition-colors">
              <div className="w-20 shrink-0 flex flex-col items-center justify-center gap-1 border-r border-white/5 pr-4">
                <div className="text-2xl font-bold text-emerald-500">{result.score.toFixed(3)}</div>
                <div className="text-[10px] text-muted-foreground uppercase tracking-widest">Score</div>
              </div>
              
              <div className="flex-1 min-w-0 flex flex-col justify-center">
                <div className="flex items-center gap-3 mb-2">
                  <div className="flex items-center gap-1.5 px-2 py-1 rounded bg-white/5 text-xs font-medium text-foreground">
                    {result.type === 'Table' ? <BarChart className="w-3.5 h-3.5 text-primary" /> : <AlignLeft className="w-3.5 h-3.5 text-orange-400" />}
                    {result.type}
                  </div>
                  <span className="text-sm font-semibold text-foreground">{result.doc}</span>
                  <span className="text-xs text-muted-foreground">Page {result.page}</span>
                </div>
                <p className="text-sm text-muted-foreground truncate">{result.match}</p>
              </div>
              
              <div className="shrink-0 flex items-center">
                <Button variant="ghost" className="text-xs h-8 border border-white/10 hover:bg-white/5">View Details</Button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
