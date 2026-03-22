"use client";

import { type ReactNode, useState } from "react";

interface TooltipProps {
  content: string;
  children: ReactNode;
  className?: string;
  placement?: "top" | "right";
}

export function Tooltip({ content, children, className = "", placement = "top" }: TooltipProps) {
  const [visible, setVisible] = useState(false);

  return (
    <span
      className={`relative inline-flex ${className}`.trim()}
      onMouseEnter={() => setVisible(true)}
      onMouseLeave={() => setVisible(false)}
      onFocus={() => setVisible(true)}
      onBlur={() => setVisible(false)}
    >
      {children}
      {visible && (
        <span
          role="tooltip"
          className={placement === "right" ? "tooltip-popup-right" : "tooltip-popup"}
        >
          {content}
        </span>
      )}
    </span>
  );
}
