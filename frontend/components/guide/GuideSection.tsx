import type { ReactNode } from "react";
import type React from "react";

export interface CalloutItem {
  number: number;
  title: string;
  description: string;
}

interface SectionShellProps {
  title: string;
  accentColor?: string;
  description: string;
  children: ReactNode;
}

export function SectionShell({ title, accentColor, description, children }: SectionShellProps) {
  const accent = accentColor ?? "var(--accent-ui)";
  const sectionStyle: React.CSSProperties = { borderLeft: `4px solid ${accent}` };
  return (
    <section
      className="py-10 pl-6"
      style={sectionStyle}
    >
      <h2 className="[font-size:20px] font-bold [color:var(--text-primary)] mb-3">{title}</h2>
      {description && (
        <p className="[font-size:14px] [color:var(--text-secondary)] mb-6 [line-height:1.6]">{description}</p>
      )}
      {children}
    </section>
  );
}
