"use client"

import React, { useState } from "react"
import { Search, BrainCircuit, AlignLeft, BarChart, Loader2 } from "lucide-react"
import { Button } from "@/components/ui/button"
import { useRetrieveMutation } from "@/hooks/useQueries"
import { useLanguage } from "@/providers/language-provider"

export default function RetrievalPage() {
  const { lang } = useLanguage()
  const [query, setQuery] = useState("Doanh thu bán hàng và cung cấp dịch vụ của FPT năm 2023")
  const retrieveMutation = useRetrieveMutation()

  const handleSearch = () => {
    if (!query.trim()) return;
    retrieveMutation.mutate({ question: query })
  }
  return (
    <div className="flex flex-col gap-6 h-full w-full max-w-5xl mx-auto pt-4 pb-10">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-foreground">{lang === "EN" ? "Hybrid Retrieval Testing" : "Kiểm thử Truy hồi Kết hợp"}</h1>
          <p className="text-sm text-muted-foreground mt-1">
            {lang === "EN" ? "Test Vector Similarity and BM25 Search across the DuckDB structured indices." : "Thử nghiệm tìm kiếm Vector và Keyword BM25 trên dữ liệu bảng DuckDB."}
          </p>
        </div>
      </div>

      <div className="rounded-xl border border-white/5 bg-card/30 p-6 flex gap-4 items-start shadow-sm">
        <div className="flex-1">
          <div className="relative">
            <Search className="w-5 h-5 absolute left-3 top-3 text-muted-foreground" />
            <input 
              type="text" 
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
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
        <Button 
          className="h-12 px-8 bg-primary text-primary-foreground" 
          onClick={handleSearch}
          disabled={retrieveMutation.isPending}
        >
          {retrieveMutation.isPending ? <Loader2 className="w-5 h-5 animate-spin" /> : (lang === "EN" ? "Search" : "Tìm kiếm")}
        </Button>
      </div>

      <div className="flex-1 flex flex-col gap-4">
        <h3 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground px-1">{lang === "EN" ? "Top Ranked Results" : "Kết quả Hàng đầu"}</h3>
        
        <div className="space-y-4">
          {!retrieveMutation.data && !retrieveMutation.isPending && (
            <div className="text-center py-10 text-sm text-muted-foreground border border-dashed border-white/10 rounded-xl">
              {lang === "EN" ? "Type a query and press Search to see retrieved tables." : "Nhập câu hỏi và bấm Tìm kiếm để xem các bảng được truy hồi."}
            </div>
          )}
          {retrieveMutation.data?.tables.map((result, i) => (
            <div key={i} className="rounded-xl border border-white/5 bg-card/50 p-5 flex gap-6 hover:bg-card/80 transition-colors">
              <div className="w-20 shrink-0 flex flex-col items-center justify-center gap-1 border-r border-white/5 pr-4">
                <div className="text-2xl font-bold text-emerald-500">{result.score.toFixed(3)}</div>
                <div className="text-[10px] text-muted-foreground uppercase tracking-widest">Score</div>
              </div>
              
              <div className="flex-1 min-w-0 flex flex-col justify-center">
                <div className="flex items-center gap-3 mb-2">
                  <div className="flex items-center gap-1.5 px-2 py-1 rounded bg-white/5 text-xs font-medium text-foreground">
                    <BarChart className="w-3.5 h-3.5 text-primary" />
                    Table
                  </div>
                  <span className="text-sm font-semibold text-foreground">{result.table_id}</span>
                  <span className="text-xs text-muted-foreground">{result.company} - {result.year}</span>
                </div>
                <p className="text-sm text-muted-foreground truncate opacity-80 font-mono text-xs mt-1">
                  {result.preview && result.preview.length > 0 
                    ? result.preview[0].join(" | ")
                    : (lang === "EN" ? "No preview available" : "Không có dữ liệu xem trước")}
                </p>
              </div>
              
              <div className="shrink-0 flex items-center">
                <Button variant="ghost" className="text-xs h-8 border border-white/10 hover:bg-white/5">{lang === "EN" ? "View Details" : "Chi tiết"}</Button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
