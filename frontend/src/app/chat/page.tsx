"use client"

import React, { useState } from "react"
import { ChatInput } from "@/features/chat/ChatInput"
import { MessageList } from "@/features/chat/MessageList"
import { EvidencePanel } from "@/features/chat/EvidencePanel"
import { ChatHistoryPanel } from "@/features/chat/ChatHistoryPanel"
import { PanelLeftOpen, PanelRightOpen } from "lucide-react"
import { Button } from "@/components/ui/button"
import { motion, AnimatePresence } from "framer-motion"

export default function ChatPage() {
  const [leftOpen, setLeftOpen] = useState(true)
  const [rightOpen, setRightOpen] = useState(true)

  return (
    <div suppressHydrationWarning className="flex w-full h-[calc(100vh-3rem)] -m-4 md:-m-6 lg:-m-8 bg-background overflow-hidden relative">
      
      {/* Left Panel: Conversation History */}
      <AnimatePresence initial={false}>
        {leftOpen && (
          <motion.div
            initial={{ width: 0, opacity: 0 }}
            animate={{ width: 260, opacity: 1 }}
            exit={{ width: 0, opacity: 0 }}
            className="h-full border-r border-white/5 bg-[#09090B] shrink-0 overflow-hidden"
          >
            <ChatHistoryPanel onClose={() => setLeftOpen(false)} />
          </motion.div>
        )}
      </AnimatePresence>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col h-full relative min-w-0">
        <div className="h-12 border-b border-white/5 flex items-center justify-between px-2 shrink-0">
          {!leftOpen ? (
            <Button variant="ghost" size="icon" className="h-8 w-8 text-muted-foreground" onClick={() => setLeftOpen(true)}>
              <PanelLeftOpen className="w-4 h-4" />
            </Button>
          ) : <div />}
          
          <div className="text-xs font-medium text-muted-foreground flex items-center gap-2">
            <span>Model: <span className="text-foreground">Qwen2.5-Coder-7B</span></span>
          </div>

          {!rightOpen ? (
            <Button variant="ghost" size="icon" className="h-8 w-8 text-muted-foreground" onClick={() => setRightOpen(true)}>
              <PanelRightOpen className="w-4 h-4" />
            </Button>
          ) : <div />}
        </div>

        <div className="flex-1 overflow-hidden flex flex-col relative">
          <MessageList />
        </div>
        
        {/* Chat Input Container */}
        <div className="p-4 bg-gradient-to-t from-background via-background to-transparent pb-6 shrink-0 w-full z-10">
          <ChatInput />
          <div className="text-center mt-2">
            <span className="text-[11px] text-muted-foreground">
              AI Guru 2026 can make mistakes. Verify tables in the Evidence Panel.
            </span>
          </div>
        </div>
      </div>
      
      {/* Right Panel: Evidence & Code */}
      <AnimatePresence initial={false}>
        {rightOpen && (
          <motion.div
            initial={{ width: 0, opacity: 0 }}
            animate={{ width: 380, opacity: 1 }}
            exit={{ width: 0, opacity: 0 }}
            className="h-full border-l border-white/5 bg-[#09090B] shrink-0 flex flex-col overflow-hidden"
          >
            <EvidencePanel onClose={() => setRightOpen(false)} />
          </motion.div>
        )}
      </AnimatePresence>
      
    </div>
  )
}
