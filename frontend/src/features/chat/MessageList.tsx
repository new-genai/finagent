"use client"

import React from "react"
import { Sparkles, User, FileText, Database, Code2 } from "lucide-react"

export function MessageList() {
  return (
    <div className="flex-1 overflow-y-auto w-full flex flex-col gap-6 py-6 scroll-smooth">
      
      {/* User Message */}
      <div className="flex gap-4 max-w-4xl mx-auto w-full px-4">
        <div className="w-8 h-8 rounded-full bg-secondary flex items-center justify-center shrink-0 border border-border">
          <User className="w-4 h-4 text-secondary-foreground" />
        </div>
        <div className="flex-1 space-y-2">
          <h4 className="font-semibold text-sm text-foreground">You</h4>
          <p className="text-foreground text-[15px] leading-relaxed">
            Doanh thu và lợi nhuận sau thuế của HPG (Hòa Phát) trong năm 2023 là bao nhiêu?
          </p>
        </div>
      </div>

      {/* AI Message */}
      <div className="flex gap-4 max-w-4xl mx-auto w-full px-4">
        <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-primary to-accent flex items-center justify-center shrink-0 shadow-sm border border-border">
          <Sparkles className="w-4 h-4 text-primary-foreground" />
        </div>
        <div className="flex-1 space-y-4">
          <h4 className="font-semibold text-sm text-foreground">NewGenAI</h4>
          
          {/* Status indicators */}
          <div className="flex flex-wrap gap-2 text-xs font-medium">
            <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-muted/50 border border-border text-muted-foreground">
              <Database className="w-3.5 h-3.5" />
              Searched 1,245 reports
            </span>
            <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-muted/50 border border-border text-muted-foreground">
              <FileText className="w-3.5 h-3.5" />
              Found 2 tables in HPG 2023
            </span>
            <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-primary/10 border border-primary/20 text-primary">
              <Code2 className="w-3.5 h-3.5" />
              Executed Pandas Query
            </span>
          </div>

          <p className="text-foreground text-[15px] leading-relaxed">
            Dựa trên báo cáo tài chính hợp nhất kiểm toán năm 2023 của Tập đoàn Hòa Phát (Mã: HPG), kết quả kinh doanh như sau:
          </p>

          <ul className="list-disc pl-5 space-y-2 text-[15px] text-foreground">
            <li><strong>Doanh thu thuần:</strong> 118,953 tỷ VND (giảm 16% so với năm 2022).</li>
            <li><strong>Lợi nhuận sau thuế:</strong> 6,800 tỷ VND (giảm 19% so với năm 2022).</li>
          </ul>

          <p className="text-muted-foreground text-sm leading-relaxed mt-4">
            Dữ liệu được trích xuất từ "Báo cáo kết quả hoạt động kinh doanh hợp nhất", trang 12, báo cáo năm 2023 của HPG.
          </p>
        </div>
      </div>
    </div>
  )
}
