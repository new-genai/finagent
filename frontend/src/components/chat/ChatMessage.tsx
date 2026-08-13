'use client';

import { ChatMessage as IChatMessage } from '@/store/useChatStore';
import { Card } from '@/components/ui/card';
import { Bot, User } from 'lucide-react';
import Typewriter from './Typewriter';

export default function ChatMessage({ message, isLast }: { message: IChatMessage; isLast: boolean }) {
  const isUser = message.role === 'user';

  return (
    <div className={`flex w-full ${isUser ? 'justify-end' : 'justify-start'} mb-6`}>
      <div className={`flex max-w-[85%] ${isUser ? 'flex-row-reverse' : 'flex-row'} items-start gap-4`}>
        <div className={`flex h-8 w-8 shrink-0 select-none items-center justify-center rounded-md shadow-sm ${isUser ? 'bg-primary text-primary-foreground' : 'bg-background border'}`}>
          {isUser ? <User size={16} /> : <Bot size={16} />}
        </div>
        
        <div className="flex flex-col gap-2 w-full min-w-0">
          <Card className={`p-4 shadow-sm ${isUser ? 'bg-primary text-primary-foreground border-transparent' : 'bg-card'}`}>
            <div className="text-sm break-words overflow-x-hidden">
              {!isUser && isLast ? (
                <Typewriter text={message.content} />
              ) : (
                <span className="whitespace-pre-wrap">{message.content}</span>
              )}
            </div>
          </Card>

          {message.thought_process && (
            <details className="w-full">
              <summary className="cursor-pointer py-1 text-xs text-muted-foreground">View Generated Pandas Code</summary>
              <pre className="p-4 rounded-lg bg-zinc-950 text-zinc-50 overflow-x-auto text-xs mt-1 border">
                <code>{message.thought_process}</code>
              </pre>
            </details>
          )}

          {message.tables_used && message.tables_used.length > 0 && (
            <div className="flex flex-wrap gap-2 mt-1">
              {message.tables_used.map((t) => (
                <span key={t} className="px-2 py-1 bg-secondary text-secondary-foreground text-[10px] rounded-md font-mono border">
                  {t}
                </span>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
