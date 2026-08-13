'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { SendHorizontal, Loader2 } from 'lucide-react';

export default function ChatInput({ onSend, isLoading }: { onSend: (text: string) => void; isLoading: boolean }) {
  const [text, setText] = useState('');

  const handleSend = () => {
    if (text.trim() && !isLoading) {
      onSend(text.trim());
      setText('');
    }
  };

  return (
    <div className="relative flex items-center w-full max-w-4xl mx-auto bg-background rounded-2xl shadow-sm border p-2 focus-within:ring-1 focus-within:ring-primary transition-all">
      <Textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="Ask anything about the financial data..."
        className="min-h-[44px] max-h-[200px] w-full resize-none border-0 focus-visible:ring-0 shadow-none py-3 px-4 bg-transparent"
        onKeyDown={(e) => {
          if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSend();
          }
        }}
      />
      <div className="absolute right-4 bottom-3">
        <Button 
          size="icon"
          className="h-10 w-10 rounded-full shrink-0"
          disabled={isLoading || !text.trim()}
          onClick={handleSend}
        >
          {isLoading ? <Loader2 className="h-5 w-5 animate-spin" /> : <SendHorizontal className="h-5 w-5 ml-0.5" />}
        </Button>
      </div>
    </div>
  );
}
