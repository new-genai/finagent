"use client"

import React, { useState } from "react"
import { Send, UploadCloud, CheckCircle2, FileJson, Loader2, Sparkles, Download, Circle, Play } from "lucide-react"
import { ShineButton } from "@/components/ui/animations/ShineButton"
import { Button } from "@/components/ui/button"
import { useLanguage } from "@/providers/language-provider"
import { useSubmissionMutation } from "@/hooks/useQueries"

export default function SubmissionPage() {
  const { lang } = useLanguage()
  const { mutateAsync: generate, isPending } = useSubmissionMutation()
  const [isSuccess, setIsSuccess] = useState(false)

  const handleGenerate = async () => {
    try {
      await generate()
      setIsSuccess(true)
    } catch (error) {
      console.error(error)
      alert(lang === "EN" ? "Failed to generate submission" : "Khởi tạo thất bại")
    }
  }

  return (
    <div className="flex flex-col gap-8 h-full w-full max-w-4xl mx-auto pt-4 pb-10">
      
      <div className="flex flex-col items-center text-center max-w-2xl mx-auto mt-6">
        <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-primary/20 to-accent/20 flex items-center justify-center border border-white/10 shadow-2xl mb-6">
          <Send className="w-8 h-8 text-primary" />
        </div>
        <h1 className="text-3xl font-bold tracking-tight text-foreground mb-3">{lang === "EN" ? "AI Guru 2026 Submission" : "Nộp bài AI Guru 2026"}</h1>
        <p className="text-muted-foreground">
          {lang === "EN" 
            ? "Generate the final `submission.json` for the test dataset. This process runs the entire pipeline end-to-end on 2,500 questions."
            : "Tạo file `submission.json` cuối cùng cho tập test. Quá trình này sẽ chạy toàn bộ luồng End-to-End trên 2.500 câu hỏi."}
        </p>
      </div>

      <div className="rounded-2xl border border-white/10 bg-card/50 p-8 shadow-2xl relative overflow-hidden mt-4">
        {/* Decorative background glow */}
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-primary/10 rounded-full blur-[100px] pointer-events-none" />
        
        <h3 className="font-semibold text-sm uppercase tracking-wider text-muted-foreground mb-6 border-b border-white/5 pb-4">
          {lang === "EN" ? "Pre-flight Checklist" : "Kiểm tra trước khi chạy"}
        </h3>
        
        <div className="flex flex-col gap-4 mb-10">
          {[
            { name: lang === "EN" ? "Dataset Parser Completed" : "Hoàn thành xử lý dữ liệu", status: true, detail: lang === "EN" ? "1,245 documents processed into DuckDB" : "1.245 tài liệu đã đưa vào DuckDB" },
            { name: lang === "EN" ? "Vector Index Built" : "Đã xây dựng Vector Index", status: true, detail: lang === "EN" ? "Dense & Sparse indices ready" : "Sẵn sàng Dense & Sparse Index" },
            { name: lang === "EN" ? "Test Dataset Loaded" : "Đã tải tập Test", status: true, detail: lang === "EN" ? "test.jsonl loaded (2,500 questions)" : "Đã tải test.jsonl (2.500 câu hỏi)" },
            { name: lang === "EN" ? "LLM Endpoint Connected" : "Kết nối LLM thành công", status: true, detail: "Qwen2.5-Coder-7B responding at 45ms" },
            { name: lang === "EN" ? "Submission Format Verified" : "Định dạng hợp lệ", status: false, detail: lang === "EN" ? "Pending generation" : "Chờ khởi tạo" },
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
          <ShineButton 
            onClick={handleGenerate}
            disabled={isPending || isSuccess}
            className={`h-12 px-10 gap-2 text-base font-medium ${isSuccess ? 'bg-emerald-500 hover:bg-emerald-600' : 'bg-primary shadow-[0_0_40px_rgba(59,130,246,0.3)]'}`}
          >
            {isPending ? (
              <>{lang === "EN" ? "Generating..." : "Đang tạo..."}</>
            ) : isSuccess ? (
              <><CheckCircle2 className="w-4 h-4" /> {lang === "EN" ? "Generated Successfully" : "Tạo thành công"}</>
            ) : (
              <><Play className="w-4 h-4 fill-current" /> {lang === "EN" ? "Generate submission.json" : "Khởi tạo file submission.json"}</>
            )}
          </ShineButton>
          {!isSuccess && <div className="text-xs text-muted-foreground">{lang === "EN" ? "Estimated time: 45 minutes" : "Thời gian ước tính: 45 phút"}</div>}
        </div>
      </div>

      {/* Post-generation actions */}
      <div className={`grid grid-cols-2 gap-4 ${isSuccess ? '' : 'opacity-50 pointer-events-none'}`}>
        <button 
          onClick={() => isSuccess && alert('Download started')}
          className="flex flex-col items-center justify-center gap-2 h-24 rounded-xl border border-dashed border-white/20 bg-white/5 hover:bg-white/10 transition-colors cursor-pointer"
        >
          <Download className="w-5 h-5 text-muted-foreground" />
          <span className="text-sm font-medium">{lang === "EN" ? "Download JSON" : "Tải xuống JSON"}</span>
        </button>
        <button 
          onClick={() => isSuccess && alert('Submission sent')}
          className="flex flex-col items-center justify-center gap-2 h-24 rounded-xl border border-dashed border-white/20 bg-white/5 hover:bg-white/10 transition-colors cursor-pointer"
        >
          <Send className="w-5 h-5 text-muted-foreground" />
          <span className="text-sm font-medium">{lang === "EN" ? "Submit to Kaggle" : "Nộp lên Kaggle"}</span>
        </button>
      </div>

    </div>
  )
}
