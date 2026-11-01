"use client";

import { motion } from "framer-motion";
import type { ReactNode } from "react";

export function HoverLiftCard({ children, className }: { children: ReactNode; className?: string }) {
  return (
    <motion.div whileHover={{ y: -2 }} transition={{ type: "spring", stiffness: 400, damping: 28 }} className={className}>
      {children}
    </motion.div>
  );
}
