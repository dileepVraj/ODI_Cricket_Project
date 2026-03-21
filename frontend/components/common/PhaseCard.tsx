import { Badge } from "./Badge";
import { StatPill } from "./StatPill";

type TierVariant = "elite" | "strong" | "caution" | "danger";

export interface PhaseStatItem {
    label: string;
    value: string;
}

interface PhaseCardProps {
    label: string;
    stats: PhaseStatItem[];
    badgeVariant?: TierVariant;
    badgeText?: string;
    barValue?: number;   // 0–100, percentage of relative bar to fill
    barTone?: TierVariant;
}

const BAR_COLOR: Record<TierVariant, string> = {
    elite:   "var(--tier-elite)",
    strong:  "var(--tier-strong)",
    caution: "var(--tier-caution)",
    danger:  "var(--tier-danger)",
};

export function PhaseCard({
    label,
    stats,
    badgeVariant,
    badgeText,
    barValue,
    barTone = "strong",
}: PhaseCardProps) {
    const barStyle = barValue !== undefined
        ? { width: `${Math.min(100, Math.max(0, barValue))}%`, background: BAR_COLOR[barTone] }
        : undefined;

    return (
        <div className="phase-card">
            <div className="phase-card-header">
                <span className="phase-card-label">{label}</span>
                {badgeVariant && badgeText && (
                    <Badge variant={badgeVariant}>{badgeText}</Badge>
                )}
            </div>
            <div className="phase-card-stats">
                {stats.map((s) => (
                    <StatPill key={s.label} label={s.label} value={s.value} />
                ))}
            </div>
            {barStyle && (
                <div className="phase-card-bar-track">
                    <div className="phase-card-bar-fill" style={barStyle} />
                </div>
            )}
        </div>
    );
}
