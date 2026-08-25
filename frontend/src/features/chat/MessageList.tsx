"use client"

import React, { useEffect, useMemo, useRef } from "react"
import { Sparkles, User, FileText, Database, Code2, Table2 } from "lucide-react"
import { useChatStore } from "@/store/useChatStore"
import Typewriter from "@/components/chat/Typewriter"
import { Badge } from "@/components/ui/badge"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"

type ParsedTableRow = {
  index: string
  tableName: string
  columns: string[]
}

export function MessageList() {
  const isLoading = useChatStore(state => state.isLoading)
  const sessionMessages = useChatStore(state => state.sessions.find(s => s.id === state.currentSessionId)?.messages)
  const messages = useMemo(() => sessionMessages || [], [sessionMessages])
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
                
                <div className="text-foreground text-[15px] leading-relaxed">
                  {isUser ? (
                    <div className="whitespace-pre-wrap">{msg.content}</div>
                  ) : (
                    <AssistantContent content={msg.content} isLast={isLast} />
                  )}
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

function AssistantContent({ content, isLast }: { content: string; isLast: boolean }) {
  const parsedRows = parsePandasTableList(content)

  if (!parsedRows.length) {
    return (
      <div className="whitespace-pre-wrap">
        {isLast ? <Typewriter text={content} /> : content}
      </div>
    )
  }

  return (
    <div className="space-y-3">
      <div className="rounded-none border border-border bg-card">
        <div className="flex flex-col gap-2 border-b border-border p-3 sm:flex-row sm:items-center sm:justify-between">
          <div className="flex items-center gap-2 font-semibold">
            <Table2 className="h-4 w-4 text-primary" />
            Tìm thấy {parsedRows.length} bảng liên quan
          </div>
          <Badge variant="outline" className="w-fit rounded-none">
            Đã chuẩn hóa để đọc
          </Badge>
        </div>

        <Table>
          <TableHeader>
            <TableRow className="hover:bg-transparent">
              <TableHead className="w-14 px-3">STT</TableHead>
              <TableHead className="px-3">Bảng</TableHead>
              <TableHead className="px-3">Các cột chính</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {parsedRows.map((row) => (
              <TableRow key={`${row.index}-${row.tableName}`}>
                <TableCell className="px-3 font-mono text-muted-foreground">{row.index}</TableCell>
                <TableCell className="px-3">
                  <div className="font-mono text-sm" title={row.tableName}>
                    {shortTableId(row.tableName)}
                  </div>
                  <div className="mt-1 text-xs text-muted-foreground">ID bảng đã rút gọn</div>
                </TableCell>
                <TableCell className="px-3">
                  <div className="flex flex-wrap gap-1.5 whitespace-normal">
                    {row.columns.slice(0, 8).map((column) => (
                      <Badge key={`${row.tableName}-${column}`} variant="secondary" className="rounded-none">
                        {column}
                      </Badge>
                    ))}
                    {row.columns.length > 8 && (
                      <Badge variant="outline" className="rounded-none">
                        +{row.columns.length - 8} cột
                      </Badge>
                    )}
                  </div>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>

      <details className="border border-border bg-background p-3 text-xs text-muted-foreground">
        <summary className="cursor-pointer font-medium text-foreground">Xem dữ liệu gốc</summary>
        <pre className="mt-3 max-h-64 overflow-auto whitespace-pre-wrap font-mono">{content}</pre>
      </details>
    </div>
  )
}

function parsePandasTableList(content: string): ParsedTableRow[] {
  if (!content.includes("Table Name") || !content.includes("Columns")) {
    return []
  }

  return content
    .split(/\r?\n/)
    .map((line) => {
      const match = line.match(/^\s*(\d+)\s+([0-9a-fA-F]{8}-[0-9a-fA-F-]{20,})\s+(.+)$/)
      if (!match) return null

      const columnsText = match[3].trim().replace(/^\[/, "").replace(/\]$/, "")
      const columns = columnsText
        .split(",")
        .map((column) => column.trim())
        .filter(Boolean)

      return {
        index: match[1],
        tableName: match[2],
        columns: columns.length ? columns : [match[3].trim()],
      }
    })
    .filter((row): row is ParsedTableRow => Boolean(row))
}

function shortTableId(tableName: string) {
  if (tableName.length <= 18) return tableName
  return `${tableName.slice(0, 8)}...${tableName.slice(-6)}`
}
