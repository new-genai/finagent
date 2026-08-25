"use client"

import React, { useState } from "react"
import { Send, Paperclip, Loader2 } from "lucide-react"
import { Button } from "@/components/ui/button"
import { useChatStore } from "@/store/useChatStore"
import { useChatMutation } from "@/hooks/useQueries"
import { useRouter } from "next/navigation"

export function ChatInput() {
  const [prompt, setPrompt] = useState("")
  const { addMessage, setLoading, isLoading } = useChatStore()
  const sessionMessages = useChatStore(state => state.sessions.find(s => s.id === state.currentSessionId)?.messages)
  const messages = sessionMessages || []
  const { mutateAsync: sendChat } = useChatMutation()
  const router = useRouter()

  const handleSend = async () => {
    if (!prompt.trim() || isLoading) return;
    
    // Check if we are not on chat page, then navigate
    if (window.location.pathname !== '/chat') {
      router.push('/chat');
      // Adding a small delay for navigation before sending message (optional, but good for UX)
    }

    const text = prompt.trim();
    setPrompt("");
    
    const history = messages.map(m => ({ role: m.role, content: m.content }));
    
    addMessage({ id: Date.now().toString(), role: "user", content: text });
    setLoading(true);

    try {
      const response = await sendChat({ question: text, history });
      addMessage({
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: response.answer,
        thought_process: response.thought_process,
        tables_used: response.tables_used,
      });
    } catch (error: unknown) {
      const message = error instanceof Error ? error.message : 'Unknown error';
      addMessage({
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: `Error: ${message}`,
      });
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="relative flex items-center w-full max-w-4xl mx-auto bg-card border-2 border-border focus-within:border-primary transition-colors p-1">
      <Button variant="ghost" size="icon" className="shrink-0 text-muted-foreground hover:text-foreground rounded-none">
        <Paperclip className="w-5 h-5" />
      </Button>
      <input
        type="text"
        value={prompt}
        onChange={(e) => setPrompt(e.target.value)}
        onKeyDown={(e) => e.key === 'Enter' && handleSend()}
        placeholder="Query financial data..."
        className="flex-1 bg-transparent border-none outline-none ring-0 px-4 py-3 font-mono text-sm placeholder:text-muted-foreground text-foreground"
      />
      <Button 
        size="icon" 
        onClick={handleSend}
        className={`shrink-0 rounded-none transition-colors border border-transparent ${prompt ? 'bg-primary text-primary-foreground hover:bg-primary/90' : 'bg-muted text-muted-foreground'}`}
        disabled={!prompt || isLoading}
      >
        {isLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
      </Button>
    </div>
  )
}
