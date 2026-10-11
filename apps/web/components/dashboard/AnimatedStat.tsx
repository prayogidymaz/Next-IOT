"use client";

import { useEffect, useRef, useState } from "react";

type AnimatedStatProps = {
  value: number;
  suffix?: string;
  className?: string;
};

export function AnimatedStat({ value, suffix = "", className = "" }: AnimatedStatProps) {
  const [display, setDisplay] = useState(value);
  const fromRef = useRef(value);

  useEffect(() => {
    const start = fromRef.current;
    fromRef.current = value;
    const delta = value - start;
    if (delta === 0) {
      setDisplay(value);
      return;
    }
    const steps = 20;
    let step = 0;
    const id = window.setInterval(() => {
      step += 1;
      if (step >= steps) {
        setDisplay(value);
        window.clearInterval(id);
        return;
      }
      setDisplay(Math.round(start + (delta * step) / steps));
    }, 16);
    return () => window.clearInterval(id);
  }, [value]);

  return (
    <span className={`font-mono tabular-nums ${className}`}>
      {display.toLocaleString()}
      {suffix}
    </span>
  );
}
