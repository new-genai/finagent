"use client"

import React from "react"
import { Database, Search, Filter } from "lucide-react"

const tableCounts = [356, 418, 297, 521, 463, 382, 444, 319, 508, 276, 397, 489, 332, 455, 371]

export default function DatasetPage() {
  return (
    <div className="flex flex-col gap-6 h-full w-full max-w-7xl mx-auto pb-6 pt-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-foreground flex items-center gap-2">
            <Database className="w-6 h-6 text-primary" />
            Dataset Explorer
          </h1>
          <p className="text-sm text-muted-foreground mt-1">
            Browse and filter 100+ Companies, 10 Years of financial reports.
          </p>
        </div>
        <div className="flex gap-2">
          <div className="relative">
            <Search className="w-4 h-4 absolute left-3 top-2.5 text-muted-foreground" />
            <input 
              type="text" 
              placeholder="Search companies..." 
              className="bg-card border border-white/10 rounded-lg pl-9 pr-4 py-2 text-sm text-foreground outline-none focus:ring-1 focus:ring-primary/50 w-[250px]"
            />
          </div>
          <button className="flex items-center gap-2 px-3 py-2 bg-card border border-white/10 rounded-lg text-sm text-foreground hover:bg-white/5 transition-colors">
            <Filter className="w-4 h-4" />
            Filter
          </button>
        </div>
      </div>

      <div className="flex-1 rounded-xl border border-white/10 bg-card/50 overflow-hidden flex flex-col">
        <div className="overflow-x-auto flex-1">
          <table className="w-full text-left border-collapse text-sm">
            <thead className="bg-[#09090B] border-b border-white/10 sticky top-0 z-10">
              <tr>
                <th className="py-3 px-4 font-medium text-muted-foreground w-12">#</th>
                <th className="py-3 px-4 font-medium text-muted-foreground">Company Name</th>
                <th className="py-3 px-4 font-medium text-muted-foreground w-24">Ticker</th>
                <th className="py-3 px-4 font-medium text-muted-foreground w-32">Exchange</th>
                <th className="py-3 px-4 font-medium text-muted-foreground w-32 text-right">Reports</th>
                <th className="py-3 px-4 font-medium text-muted-foreground w-32 text-right">Tables</th>
                <th className="py-3 px-4 font-medium text-muted-foreground w-32">Status</th>
              </tr>
            </thead>
            <tbody>
              {Array.from({ length: 15 }).map((_, i) => (
                <tr key={i} className="border-b border-white/5 hover:bg-white/5 transition-colors">
                  <td className="py-3 px-4 text-muted-foreground">{i + 1}</td>
                  <td className="py-3 px-4 font-medium text-foreground">{['Vinamilk', 'Hòa Phát Group', 'FPT Corporation', 'Mobile World', 'Vietcombank'][i % 5]}</td>
                  <td className="py-3 px-4 text-accent font-medium">{['VNM', 'HPG', 'FPT', 'MWG', 'VCB'][i % 5]}</td>
                  <td className="py-3 px-4 text-muted-foreground">HOSE</td>
                  <td className="py-3 px-4 text-right">10</td>
                  <td className="py-3 px-4 text-right text-muted-foreground">{tableCounts[i]}</td>
                  <td className="py-3 px-4">
                    <span className="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-medium bg-emerald-500/10 text-emerald-500 border border-emerald-500/20">
                      Indexed
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        
        {/* Pagination */}
        <div className="h-12 border-t border-white/10 bg-[#09090B] flex items-center justify-between px-4 shrink-0">
          <span className="text-xs text-muted-foreground">Showing 1-15 of 100 companies</span>
          <div className="flex gap-1">
            <button className="px-3 py-1 rounded border border-white/10 text-xs text-muted-foreground hover:bg-white/5 disabled:opacity-50" disabled>Previous</button>
            <button className="px-3 py-1 rounded border border-white/10 text-xs text-foreground bg-white/5">1</button>
            <button className="px-3 py-1 rounded border border-white/10 text-xs text-muted-foreground hover:bg-white/5">2</button>
            <button className="px-3 py-1 rounded border border-white/10 text-xs text-muted-foreground hover:bg-white/5">3</button>
            <span className="px-2 py-1 text-xs text-muted-foreground">...</span>
            <button className="px-3 py-1 rounded border border-white/10 text-xs text-muted-foreground hover:bg-white/5">Next</button>
          </div>
        </div>
      </div>
    </div>
  )
}
