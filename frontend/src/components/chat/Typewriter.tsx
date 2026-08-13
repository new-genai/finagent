'use client';

import { useState, useEffect } from 'react';

export default function Typewriter({ text, speed = 15 }: { text: string; speed?: number }) {
  const [displayedText, setDisplayedText] = useState('');

  useEffect(() => {
    let i = 1;
    const interval = setInterval(() => {
      setDisplayedText(text.slice(0, i));
      i++;
      if (i >= text.length) clearInterval(interval);
    }, speed);

    return () => clearInterval(interval);
  }, [text, speed]);

  return <span className="whitespace-pre-wrap">{displayedText}</span>;
}
