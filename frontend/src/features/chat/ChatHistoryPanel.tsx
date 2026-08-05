"use client"

import React from "react"
import { PanelLeftClose, Plus, MessageSquare } from "lucide-react"
import { Button } from "@/components/ui/button"

interface ChatHistoryPanelProps {
  onClose: () => void
}

export function ChatHistoryPanel({ onClose }: ChatHistoryPanelProps) {
  const history = [
    { title: "Doanh thu HPG 2023", date: "Today" },
    { title: "So sánh biên lợi nhuận VNM", date: "Yesterday" },
    { title: "Tài sản cố định FPT", date: "Previous 7 Days" },
    { title: "Chi phí lãi vay MWG", date: "Previous 7 Days" },
  ]

  return (
    <div className="flex flex-col h-full w-[260px]">
      <div className="h-12 flex items-center justify-between px-2 shrink-0 border-b border-white/5">
        <Button variant="ghost" size="icon" className="h-8 w-8 text-muted-foreground" onClick={onClose}>
          <PanelLeftClose className="w-4 h-4" />
        </Button>
        <Button variant="ghost" size="sm" className="h-8 gap-1.5 text-foreground hover:bg-white/5">
          <Plus className="w-4 h-4" />
          New Chat
        </Button>
      </div>

      <div className="flex-1 overflow-y-auto p-2">
        <div className="flex flex-col gap-1">
          {history.map((item, i) => (
            <div key={i} className="group flex flex-col gap-1">
              {i === 0 || history[i - 1].date !== item.date ? (
                <span className="text-xs font-medium text-muted-foreground px-2 pt-4 pb-1">
                  {item.date}
                </span>
              ) : null}
              <Button 
                variant="ghost" 
                className="w-full justify-start h-9 px-2 text-sm font-normal text-muted-foreground hover:text-foreground hover:bg-white/5"
              >
                <MessageSquare className="w-3.5 h-3.5 mr-2 shrink-0" />
                <span className="truncate">{item.title}</span>
              </Button>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
