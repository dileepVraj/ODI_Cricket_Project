interface StatPillProps {
  label: string;
  value: string | number;
  valueColor?: string;
  className?: string;
}

export function StatPill({ label, value, valueColor, className = "" }: StatPillProps) {
  return (
    <div className={`stat-pill ${className}`.trim()}>
      <span className="stat-pill-label">{label}</span>
      <span
        className="stat-pill-value"
        style={valueColor ? { color: `var(${valueColor})` } : undefined}
        data-numeric="true"
      >
        {value}
      </span>
    </div>
  );
}
