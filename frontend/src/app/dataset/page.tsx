"use client"

import React from "react"
import { Database, Search, Filter } from "lucide-react"

import { useDatasetStats } from "@/hooks/useQueries"
import { useLanguage } from "@/providers/language-provider"

export default function DatasetPage() {
  const { data: stats, isLoading } = useDatasetStats()
  const { lang } = useLanguage()

  // Mảng fallback nếu chưa load xong hoặc có lỗi
  const companies = stats?.companies || []
  const counts = stats?.company_table_counts || {}
  return (
    <div className="flex flex-col gap-6 h-full w-full max-w-7xl mx-auto pb-6 pt-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-foreground flex items-center gap-2">
            <Database className="w-6 h-6 text-primary" />
            {lang === "EN" ? "Dataset Explorer" : "Trình khám phá Dữ liệu"}
          </h1>
          <p className="text-sm text-muted-foreground mt-1">
            {lang === "EN" ? "Browse and filter 100+ Companies, 10 Years of financial reports." : "Duyệt và lọc hơn 100 Công ty, 10 năm báo cáo tài chính."}
          </p>
        </div>
        <div className="flex gap-2">
          <div className="relative">
            <Search className="w-4 h-4 absolute left-3 top-2.5 text-muted-foreground" />
            <input 
              type="text" 
              placeholder={lang === "EN" ? "Search companies..." : "Tìm kiếm công ty..."}
              className="bg-card border border-white/10 rounded-lg pl-9 pr-4 py-2 text-sm text-foreground outline-none focus:ring-1 focus:ring-primary/50 w-[250px]"
            />
          </div>
          <button className="flex items-center gap-2 px-3 py-2 bg-card border border-white/10 rounded-lg text-sm text-foreground hover:bg-white/5 transition-colors">
            <Filter className="w-4 h-4" />
            {lang === "EN" ? "Filter" : "Lọc"}
          </button>
        </div>
      </div>

      <div className="flex-1 rounded-xl border border-white/10 bg-card/50 overflow-hidden flex flex-col">
        <div className="overflow-x-auto flex-1">
          <table className="w-full text-left border-collapse text-sm">
            <thead className="bg-[#09090B] border-b border-white/10 sticky top-0 z-10">
              <tr>
                <th className="py-3 px-4 font-medium text-muted-foreground w-12">#</th>
                <th className="py-3 px-4 font-medium text-muted-foreground">{lang === "EN" ? "Company Name" : "Tên công ty"}</th>
                <th className="py-3 px-4 font-medium text-muted-foreground w-24">Ticker</th>
                <th className="py-3 px-4 font-medium text-muted-foreground w-32">{lang === "EN" ? "Exchange" : "Sàn"}</th>
                <th className="py-3 px-4 font-medium text-muted-foreground w-32 text-right">{lang === "EN" ? "Reports" : "Báo cáo"}</th>
                <th className="py-3 px-4 font-medium text-muted-foreground w-32 text-right">{lang === "EN" ? "Tables" : "Số bảng"}</th>
                <th className="py-3 px-4 font-medium text-muted-foreground w-32">{lang === "EN" ? "Status" : "Trạng thái"}</th>
              </tr>
            </thead>
            <tbody>
              {isLoading ? (
                <tr><td colSpan={7} className="py-8 text-center text-muted-foreground">Loading dataset statistics...</td></tr>
              ) : companies.length === 0 ? (
                <tr><td colSpan={7} className="py-8 text-center text-muted-foreground">No companies found in DuckDB.</td></tr>
              ) : (
                companies.map((company, i) => (
                  <tr key={i} className="border-b border-white/5 hover:bg-white/5 transition-colors">
                    <td className="py-3 px-4 text-muted-foreground">{i + 1}</td>
                    <td className="py-3 px-4 font-medium text-foreground">{company}</td>
                    <td className="py-3 px-4 text-accent font-medium">{company}</td>
                    <td className="py-3 px-4 text-muted-foreground">UNKNOWN</td>
                    <td className="py-3 px-4 text-right">{counts[company] ? Math.ceil(counts[company] / 4) : 0}</td>
                    <td className="py-3 px-4 text-right text-muted-foreground">{counts[company] || 0}</td>
                    <td className="py-3 px-4">
                      <span className="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-medium bg-emerald-500/10 text-emerald-500 border border-emerald-500/20">
                        Indexed
                      </span>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
        
        {/* Pagination */}
        <div className="h-12 border-t border-white/10 bg-[#09090B] flex items-center justify-between px-4 shrink-0">
          <span className="text-xs text-muted-foreground">
            {lang === "EN" ? `Showing ${companies.length} companies` : `Đang hiển thị ${companies.length} công ty`}
          </span>
          <div className="flex gap-1">
            <button className="px-3 py-1 rounded border border-white/10 text-xs text-muted-foreground hover:bg-white/5 disabled:opacity-50" disabled>
              {lang === "EN" ? "Previous" : "Trước"}
            </button>
            <button className="px-3 py-1 rounded border border-white/10 text-xs text-foreground bg-white/5">1</button>
            <button className="px-3 py-1 rounded border border-white/10 text-xs text-muted-foreground hover:bg-white/5 disabled:opacity-50" disabled>
              {lang === "EN" ? "Next" : "Sau"}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
