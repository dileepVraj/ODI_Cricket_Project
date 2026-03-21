import { type ReactNode } from "react";

type CardVariant = "base" | "active" | "signal";

interface CardProps {
  variant?: CardVariant;
  children: ReactNode;
  className?: string;
  onClick?: () => void;
}

export function Card({ variant = "base", children, className = "", onClick }: CardProps) {
  return (
    <div
      className={`card-${variant} ${className}`.trim()}
      onClick={onClick}
      style={onClick ? { cursor: "pointer" } : undefined}
    >
      {children}
    </div>
  );
}
