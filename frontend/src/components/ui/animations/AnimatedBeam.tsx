"use client";

import { motion } from "framer-motion";
import React from "react";
import { cn } from "@/lib/utils";

interface AnimatedBeamProps extends React.HTMLAttributes<HTMLDivElement> {
  children?: React.ReactNode;
  duration?: number;
  delay?: number;
  className?: string;
  from?: string;
  to?: string;
}

export function AnimatedBeam({
  children,
  duration = 2,
  delay = 0,
  className,
  from = "var(--color-primary)",
  to = "var(--color-accent)",
  ...props
}: AnimatedBeamProps) {
  return (
    <div
      suppressHydrationWarning
      className={cn("relative overflow-hidden flex items-center", className)}
      {...props}
    >
      <div className="absolute inset-0 bg-muted/20" suppressHydrationWarning />
      <motion.div
        className="absolute h-[2px] top-1/2 -translate-y-1/2 w-1/3 bg-gradient-to-r from-transparent via-primary to-transparent opacity-70"
        initial={{ left: "-100%" }}
        animate={{ left: "200%" }}
        transition={{
          repeat: Infinity,
          duration: duration,
          ease: "linear",
          delay: delay,
        }}
        style={{
          background: `linear-gradient(to right, transparent, ${from}, ${to}, transparent)`,
        }}
      />
      <div className="relative z-10 w-full h-full">{children}</div>
    </div>
  );
}
