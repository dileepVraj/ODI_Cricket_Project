"use client";

import { type ReactNode, type ButtonHTMLAttributes } from "react";

type ButtonVariant = "primary" | "ghost" | "danger";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  children: ReactNode;
}

export function Button({
  variant = "primary",
  children,
  className = "",
  "aria-label": ariaLabel,
  ...rest
}: ButtonProps) {
  return (
    <button
      className={`btn-${variant} ${className}`.trim()}
      aria-label={ariaLabel}
      {...rest}
    >
      {children}
    </button>
  );
}
