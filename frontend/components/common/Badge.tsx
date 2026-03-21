import { type ReactNode } from "react";

type BadgeVariant = "elite" | "strong" | "caution" | "danger" | "live" | "format";

interface BadgeProps {
  variant: BadgeVariant;
  children: ReactNode;
  className?: string;
}

export function Badge({ variant, children, className = "" }: BadgeProps) {
  if (variant === "live") {
    return (
      <span className={`badge badge-live ${className}`.trim()}>
        <span className="badge-live-dot animate-pulse-dot" />
        {children}
      </span>
    );
  }

  return (
    <span className={`badge badge-${variant} ${className}`.trim()}>
      {children}
    </span>
  );
}
