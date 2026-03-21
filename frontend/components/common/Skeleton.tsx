interface SkeletonBarProps {
  width?: string;
  height?: string;
  className?: string;
}

interface SkeletonRowProps {
  cols?: number;
  className?: string;
}

export function SkeletonBar({ width = "100%", height = "16px", className = "" }: SkeletonBarProps) {
  return (
    <div
      className={`skeleton ${className}`.trim()}
      style={{ width, height }}
    />
  );
}

export function SkeletonBlock({ width = "100%", height = "80px", className = "" }: SkeletonBarProps) {
  return (
    <div
      className={`skeleton ${className}`.trim()}
      style={{ width, height, borderRadius: "var(--radius-md)" }}
    />
  );
}

export function SkeletonRow({ cols = 4, className = "" }: SkeletonRowProps) {
  return (
    <div className={`flex gap-3 ${className}`.trim()}>
      {Array.from({ length: cols }).map((_, i) => (
        <SkeletonBar key={i} height="12px" />
      ))}
    </div>
  );
}
