"use client";

import { motion } from "framer-motion";
import type { ReactNode } from "react";

export function SpringDropdownPanel({ children, className }: { children: ReactNode; className?: string }) {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.96, y: -4 }}
      animate={{ opacity: 1, scale: 1, y: 0 }}
      exit={{ opacity: 0, scale: 0.98, y: -2 }}
      transition={{ type: "spring", stiffness: 420, damping: 30 }}
      className={className}
    >
      {children}
    </motion.div>
  );
}
