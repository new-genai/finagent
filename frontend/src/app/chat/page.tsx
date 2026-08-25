"use client"

import React, { useState } from "react"
import { ChatInput } from "@/features/chat/ChatInput"
import { MessageList } from "@/features/chat/MessageList"
import { EvidencePanel } from "@/features/chat/EvidencePanel"
import { ChatHistoryPanel } from "@/features/chat/ChatHistoryPanel"
import { Button } from "@/components/ui/button"

export default function ChatPage() {
  const [leftOpen, setLeftOpen] = useState(true)
  const [rightOpen, setRightOpen] = useState(true)

  return (
    <div suppressHydrationWarning className="flex w-full h-[calc(100vh-3rem)] -m-4 md:-m-6 lg:-m-8 bg-background overflow-hidden relative">
      
      {/* Left Panel: Conversation History */}
      {leftOpen && (
        <div className="w-[260px] h-full border-r border-border bg-background shrink-0 flex flex-col">
          <ChatHistoryPanel onClose={() => setLeftOpen(false)} />
        </div>
      )}

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col h-full relative min-w-0">
        <div className="h-12 border-b border-border flex items-center justify-between px-4 shrink-0 bg-background">
          {!leftOpen ? (
            <button className="text-muted-foreground hover:text-foreground text-xs font-mono border border-border px-2 py-1" onClick={() => setLeftOpen(true)}>
              [History]
            </button>
          ) : <div />}
          
          <div className="text-xs font-mono font-bold text-muted-foreground flex items-center gap-2 uppercase tracking-wider">
            <span>Model: <span className="text-foreground">Qwen2.5-Coder</span></span>
          </div>

          {!rightOpen ? (
            <button className="text-muted-foreground hover:text-foreground text-xs font-mono border border-border px-2 py-1" onClick={() => setRightOpen(true)}>
              [Evidence]
            </button>
          ) : <div />}
        </div>

        <div className="flex-1 overflow-hidden flex flex-col relative">
          <MessageList />
        </div>
        
        {/* Chat Input Container */}
        <div className="p-4 bg-background border-t border-border shrink-0 w-full z-10">
          <ChatInput />
          <div className="text-center mt-3">
            <span className="text-[10px] uppercase tracking-wider font-mono text-muted-foreground">
              Note: Verify tables in the Evidence Panel before acting.
            </span>
          </div>
        </div>
      </div>
      
      {/* Right Panel: Evidence & Code */}
      {rightOpen && (
        <div className="w-[380px] h-full border-l border-border bg-background shrink-0 flex flex-col">
          <EvidencePanel onClose={() => setRightOpen(false)} />
        </div>
      )}
      
    </div>
  )
}
