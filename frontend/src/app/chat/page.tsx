"use client"

import React, { useState } from "react"
import { ChatInput } from "@/features/chat/ChatInput"
import { MessageList } from "@/features/chat/MessageList"
import { EvidencePanel } from "@/features/chat/EvidencePanel"
import { ChatHistoryPanel } from "@/features/chat/ChatHistoryPanel"
import { Button } from "@/components/ui/button"
import { Panel, Group as PanelGroup, Separator as PanelResizeHandle } from "react-resizable-panels"

export default function ChatPage() {
  const [leftOpen, setLeftOpen] = useState(true)
  const [rightOpen, setRightOpen] = useState(true)

  return (
    <div suppressHydrationWarning className="flex w-full h-[calc(100vh-3rem)] -m-4 md:-m-6 lg:-m-8 bg-background overflow-hidden relative">
      <PanelGroup orientation="horizontal">
        {/* Left Panel: Conversation History */}
        {leftOpen && (
          <Panel defaultSize="20" minSize="15" maxSize="40" className="border-r border-border bg-background flex flex-col">
            <ChatHistoryPanel onClose={() => setLeftOpen(false)} />
          </Panel>
        )}
        {leftOpen && (
          <PanelResizeHandle className="w-1 bg-border hover:bg-primary/50 transition-colors cursor-col-resize" />
        )}

        {/* Main Chat Area */}
        <Panel className="flex flex-col h-full relative min-w-0">
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
        </Panel>
        
        {/* Right Panel: Evidence & Code */}
        {rightOpen && (
          <PanelResizeHandle className="w-1 bg-border hover:bg-primary/50 transition-colors cursor-col-resize" />
        )}
        {rightOpen && (
          <Panel defaultSize="30" minSize="20" maxSize="50" className="border-l border-border bg-background flex flex-col">
            <EvidencePanel onClose={() => setRightOpen(false)} />
          </Panel>
        )}
      </PanelGroup>
    </div>
  )
}
