"use client";

import { type ReactNode, type ButtonHTMLAttributes } from "react";

type ButtonVariant = "primary" | "ghost" | "danger";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  children: ReactNode;
  isLoading?: boolean;
  loadingLabel?: string;
}

function Spinner() {
  return (
    <svg
      className="animate-spin"
      width={14}
      height={14}
      viewBox="0 0 14 14"
      fill="none"
      aria-hidden="true"
    >
      <circle
        cx={7}
        cy={7}
        r={5}
        stroke="currentColor"
        strokeOpacity={0.3}
        strokeWidth={2}
      />
      <path
        d="M12 7a5 5 0 0 0-5-5"
        stroke="currentColor"
        strokeWidth={2}
        strokeLinecap="round"
      />
    </svg>
  );
}

export function Button({
  variant = "primary",
  children,
  className = "",
  isLoading = false,
  loadingLabel = "Analysing...",
  disabled,
  "aria-label": ariaLabel,
  ...rest
}: ButtonProps) {
  return (
    <button
      className={`btn-${variant} ${className}`.trim()}
      aria-label={ariaLabel}
      disabled={disabled || isLoading}
      {...rest}
    >
      {isLoading ? (
        <>
          <Spinner />
          {loadingLabel}
        </>
      ) : (
        children
      )}
    </button>
  );
}
