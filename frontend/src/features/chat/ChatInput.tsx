"use client"

import React, { useState } from "react"
import { Send, Paperclip } from "lucide-react"
import { Button } from "@/components/ui/button"

export function ChatInput() {
  const [prompt, setPrompt] = useState("")

  return (
    <div className="relative flex items-center w-full max-w-4xl mx-auto bg-card border border-border shadow-md rounded-2xl p-2 px-4 focus-within:ring-2 focus-within:ring-primary/50 transition-all">
      <Button variant="ghost" size="icon" className="shrink-0 text-muted-foreground hover:text-foreground">
        <Paperclip className="w-5 h-5" />
      </Button>
      <input
        type="text"
        value={prompt}
        onChange={(e) => setPrompt(e.target.value)}
        placeholder="Ask anything about financial data (e.g. Doanh thu của VNM năm 2023 là bao nhiêu?)"
        className="flex-1 bg-transparent border-none outline-none ring-0 px-4 py-3 text-sm placeholder:text-muted-foreground text-foreground"
      />
      <Button 
        size="icon" 
        className={`shrink-0 rounded-xl transition-all ${prompt ? 'bg-primary text-primary-foreground' : 'bg-muted text-muted-foreground'}`}
        disabled={!prompt}
      >
        <Send className="w-4 h-4" />
      </Button>
    </div>
  )
}
