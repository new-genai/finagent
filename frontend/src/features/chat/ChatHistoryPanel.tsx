"use client"

import React from "react"
import { PanelLeftClose, Plus, MessageSquare } from "lucide-react"
import { Button } from "@/components/ui/button"
import { useChatStore } from "@/store/useChatStore"

interface ChatHistoryPanelProps {
  onClose: () => void
}

export function ChatHistoryPanel({ onClose }: ChatHistoryPanelProps) {
  const { sessions, currentSessionId, loadSession, createNewSession } = useChatStore()
  
  const getSessionDateLabel = (timestamp: number) => {
    const date = new Date(timestamp);
    const today = new Date();
    const yesterday = new Date(today);
    yesterday.setDate(yesterday.getDate() - 1);
    
    if (date.toDateString() === today.toDateString()) return "Today";
    if (date.toDateString() === yesterday.toDateString()) return "Yesterday";
    if (date.getTime() > today.getTime() - 7 * 24 * 60 * 60 * 1000) return "Previous 7 Days";
    return "Older";
  }

  return (
    <div className="flex flex-col h-full w-[260px]">
      <div className="h-12 flex items-center justify-between px-2 shrink-0 border-b border-white/5">
        <Button variant="ghost" size="icon" className="h-8 w-8 text-muted-foreground" onClick={onClose}>
          <PanelLeftClose className="w-4 h-4" />
        </Button>
        <Button variant="ghost" size="sm" className="h-8 gap-1.5 text-foreground hover:bg-white/5" onClick={createNewSession}>
          <Plus className="w-4 h-4" />
          New Chat
        </Button>
      </div>

      <div className="flex-1 overflow-y-auto p-2">
        <div className="flex flex-col gap-1">
          {sessions.map((session, i) => {
            const dateLabel = getSessionDateLabel(session.updatedAt);
            const prevDateLabel = i > 0 ? getSessionDateLabel(sessions[i - 1].updatedAt) : null;
            
            return (
              <div key={session.id} className="group flex flex-col gap-1">
                {i === 0 || dateLabel !== prevDateLabel ? (
                  <span className="text-xs font-medium text-muted-foreground px-2 pt-4 pb-1">
                    {dateLabel}
                  </span>
                ) : null}
                <Button 
                  variant="ghost" 
                  onClick={() => loadSession(session.id)}
                  className={`w-full justify-start h-9 px-2 text-sm font-normal hover:text-foreground hover:bg-white/5 ${currentSessionId === session.id ? 'bg-white/5 text-foreground' : 'text-muted-foreground'}`}
                >
                  <MessageSquare className="w-3.5 h-3.5 mr-2 shrink-0" />
                  <span className="truncate">{session.title}</span>
                </Button>
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}
