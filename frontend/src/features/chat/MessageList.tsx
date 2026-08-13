"use client"

import React, { useEffect, useRef } from "react"
import { Sparkles, User, FileText, Database, Code2 } from "lucide-react"
import { useChatStore } from "@/store/useChatStore"
import Typewriter from "@/components/chat/Typewriter"

export function MessageList() {
  const isLoading = useChatStore(state => state.isLoading)
  const sessionMessages = useChatStore(state => state.sessions.find(s => s.id === state.currentSessionId)?.messages)
  const messages = sessionMessages || []
  const scrollRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollIntoView({ behavior: "smooth" })
    }
  }, [messages, isLoading])

  return (
    <div className="flex-1 overflow-y-auto w-full flex flex-col gap-6 py-6 scroll-smooth">
      
      {messages.length === 0 ? (
        <div className="flex-1 flex flex-col items-center justify-center text-muted-foreground opacity-50 space-y-4">
          <Sparkles className="w-8 h-8" />
          <p>Ask a financial question to start the investigation.</p>
        </div>
      ) : (
        messages.map((msg, idx) => {
          const isUser = msg.role === "user";
          const isLast = idx === messages.length - 1;
          
          return (
            <div key={msg.id} className="flex gap-4 max-w-4xl mx-auto w-full px-4">
              <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 border border-border ${isUser ? 'bg-secondary' : 'bg-gradient-to-tr from-primary to-accent shadow-sm'}`}>
                {isUser ? <User className="w-4 h-4 text-secondary-foreground" /> : <Sparkles className="w-4 h-4 text-primary-foreground" />}
              </div>
              <div className="flex-1 space-y-4">
                <h4 className="font-semibold text-sm text-foreground">{isUser ? "You" : "NewGenAI"}</h4>
                
                {!isUser && msg.tables_used && msg.tables_used.length > 0 && (
                  <div className="flex flex-wrap gap-2 text-xs font-medium">
                    <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-muted/50 border border-border text-muted-foreground">
                      <Database className="w-3.5 h-3.5" />
                      Hybrid Search DB
                    </span>
                    <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-muted/50 border border-border text-muted-foreground">
                      <FileText className="w-3.5 h-3.5" />
                      Found {msg.tables_used.length} tables
                    </span>
                    <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-primary/10 border border-primary/20 text-primary">
                      <Code2 className="w-3.5 h-3.5" />
                      Executed Pandas
                    </span>
                  </div>
                )}
                
                <div className="text-foreground text-[15px] leading-relaxed whitespace-pre-wrap">
                  {!isUser && isLast ? <Typewriter text={msg.content} /> : msg.content}
                </div>
              </div>
            </div>
          )
        })
      )}

      {isLoading && (
        <div className="flex gap-4 max-w-4xl mx-auto w-full px-4 animate-pulse mt-4">
          <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-primary to-accent flex items-center justify-center shrink-0 shadow-sm border border-border">
            <Sparkles className="w-4 h-4 text-primary-foreground" />
          </div>
          <div className="flex-1 space-y-4">
            <h4 className="font-semibold text-sm text-foreground">NewGenAI</h4>
            <div className="h-4 bg-muted/50 rounded w-1/4"></div>
            <div className="h-4 bg-muted/50 rounded w-1/2"></div>
          </div>
        </div>
      )}
      
      <div ref={scrollRef} className="h-4" />
    </div>
  )
}
