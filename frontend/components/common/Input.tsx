"use client";

import { type InputHTMLAttributes, type SelectHTMLAttributes } from "react";

/* ── Shared label / error wrappers ───────────────────────────────────── */

interface FieldWrapperProps {
  label?: string;
  error?: string;
  children: React.ReactNode;
}

function FieldWrapper({ label, error, children }: FieldWrapperProps) {
  return (
    <div>
      {label && <label className="input-label">{label}</label>}
      {children}
      {error && <p className="input-error-text">{error}</p>}
    </div>
  );
}

/* ── Text Input ──────────────────────────────────────────────────────── */

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
}

export function Input({ label, error, className = "", ...rest }: InputProps) {
  const errorClass = error ? "context-input-error" : "";
  return (
    <FieldWrapper label={label} error={error}>
      <input
        className={`context-input ${errorClass} ${className}`.trim()}
        {...rest}
      />
    </FieldWrapper>
  );
}

/* ── Select ──────────────────────────────────────────────────────────── */

interface SelectOption {
  label: string;
  value: string;
}

interface SelectProps extends SelectHTMLAttributes<HTMLSelectElement> {
  label?: string;
  error?: string;
  options: SelectOption[];
  placeholder?: string;
}

export function Select({
  label,
  error,
  options,
  placeholder,
  className = "",
  ...rest
}: SelectProps) {
  const errorClass = error ? "context-input-error" : "";
  return (
    <FieldWrapper label={label} error={error}>
      <select className={`context-input ${errorClass} ${className}`.trim()} {...rest}>
        {placeholder && (
          <option value="" disabled>
            {placeholder}
          </option>
        )}
        {options.map((opt) => (
          <option key={opt.value} value={opt.value}>
            {opt.label}
          </option>
        ))}
      </select>
    </FieldWrapper>
  );
}

/* ── Slider ──────────────────────────────────────────────────────────── */

interface SliderProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
}

export function Slider({ label, error, className = "", ...rest }: SliderProps) {
  return (
    <FieldWrapper label={label} error={error}>
      <input
        type="range"
        className={`context-input ${className}`.trim()}
        {...rest}
      />
    </FieldWrapper>
  );
}
