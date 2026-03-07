"use client";

import { Shield, Target, TrendingUp } from "lucide-react";
import CountUp from "@/components/animations/CountUp";
import EmptyState from "@/components/common/EmptyState";
import { getPercentBreakdown } from "@/lib/types";

interface ReportCardProps {
    data: Record<string, unknown>;
}

const HIDDEN_KEYS = new Set([
    "MATCH_IDS",
    "raw_matches",
    "match_ids",
    "match_audit",
    "percent_breakdown",
    "verdict_tone",
    "highlight_flags",
    "derived_badges",
]);

function formatLabel(key: string): string {
    return key
        .replace(/_/g, " ")
        .replace(/\b\w/g, (c) => c.toUpperCase());
}

export default function ReportCard({ data }: ReportCardProps) {
    if (!data || typeof data !== "object") {
        return <EmptyState message="No report data available." />;
    }

    const verdict = String(data["bias_verdict"] ?? data["verdict"] ?? "");
    const venueId = String(data["venue_id"] ?? data["venue"] ?? "Unknown");
    const breakdown = getPercentBreakdown(data["percent_breakdown"]);
    const bat1Pct = Number(breakdown["bat_first"] ?? data["bat1_win_pct"] ?? data["bat1_pct"] ?? 0);
    const chasePct = Number(breakdown["chase"] ?? data["chase_win_pct"] ?? data["chase_pct"] ?? 0);
    const tieNrPct = Number(breakdown["tie_nr"] ?? 0);
    const verdictTone = String(data["verdict_tone"] ?? "muted");

    const heroKeys = new Set([
        "bias_verdict",
        "verdict",
        "verdict_tone",
        "percent_breakdown",
        "venue_id",
        "venue",
        "bat1_win_pct",
        "bat1_pct",
        "chase_win_pct",
        "chase_pct",
    ]);
    const statEntries = Object.entries(data).filter(([key]) => !HIDDEN_KEYS.has(key) && !heroKeys.has(key));

    return (
        <div className="[display:flex] [flex-direction:column] [gap:24px]">
            <div className="[display:flex] [align-items:center] [justify-content:space-between] [flex-wrap:wrap] [gap:16px]">
                <div>
                    <div className="[font-size:0.72rem] [letter-spacing:0.06em] [color:var(--text-disabled)] [font-weight:600] [margin-bottom:4px] [text-transform:uppercase]">
                        Venue
                    </div>
                    <div className="[font-size:1.2rem] [font-weight:700] [color:var(--text-primary)]">{venueId}</div>
                </div>
                <VerdictBadge verdict={verdict} tone={verdictTone} />
            </div>

            <div className="[background:var(--bg-elevated)] [border-radius:var(--radius-lg)] [padding:18px_22px] [border:1px_solid_var(--border-subtle)] [box-shadow:var(--shadow-md)]">
                <div className="[display:flex] [justify-content:space-between] [margin-bottom:10px] [font-size:0.8rem] [font-weight:600]">
                    <span className="[color:var(--accent-primary)]">
                        <Shield size={14} className="[vertical-align:middle] [margin-right:4px]" />
                        Bat First: <span className="font-numeric">{bat1Pct}%</span>
                    </span>
                    <span className="[color:var(--text-secondary)]">
                        Tie/NR: <span className="font-numeric">{tieNrPct}%</span>
                    </span>
                    <span className="[color:var(--accent-secondary)]">
                        Chase: <span className="font-numeric">{chasePct}%</span>
                        <Target size={14} className="[vertical-align:middle] [margin-left:4px]" />
                    </span>
                </div>

                <div className="[display:flex] [height:12px] [border-radius:6px] [overflow:hidden] [background:var(--bg-active)]">
                    <div
                        className="[background:linear-gradient(90deg,_var(--accent-primary),_var(--accent-tertiary))] [transition:width_0.5s_ease-out]"
                        style={{ width: `${bat1Pct}%` }}
                    />
                    <div
                        className="[background:var(--text-disabled)] [opacity:0.45] [transition:width_0.5s_ease-out]"
                        style={{ width: `${tieNrPct}%` }}
                    />
                    <div
                        className="[background:linear-gradient(90deg,_var(--accent-secondary),_var(--accent-primary))] [transition:width_0.5s_ease-out]"
                        style={{ width: `${chasePct}%` }}
                    />
                </div>
            </div>

            <div className="[display:grid] [grid-template-columns:repeat(auto-fill,_minmax(190px,_1fr))] [gap:12px]">
                {statEntries.map(([key, val]) => (
                    <div
                        key={key}
                        className="[padding:16px_18px] [background:var(--bg-elevated)] [border-radius:var(--radius-md)] [border:1px_solid_var(--border-subtle)] [transition:border-color_var(--transition-fast),_transform_var(--transition-fast)] [box-shadow:var(--shadow-sm)] hover:[border-color:var(--border-strong)] hover:[transform:translateY(-1px)]"
                    >
                        <div className="[font-size:0.72rem] [letter-spacing:0.02em] [color:var(--text-disabled)] [font-weight:600] [margin-bottom:6px]">
                            {formatLabel(key)}
                        </div>
                        <div className="[font-size:1.2rem] [font-weight:800] [color:var(--text-primary)] [font-family:var(--font-numeric)] font-numeric">
                            {typeof val === "number" ? (
                                <CountUp end={val} decimals={Number.isInteger(val) ? 0 : 2} duration={1.2} />
                            ) : val === null || val === undefined ? (
                                "-"
                            ) : (
                                String(val)
                            )}
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}

function VerdictBadge({ verdict, tone }: { verdict: string; tone: string }) {
    if (tone === "primary") {
        return (
            <div className="[display:inline-flex] [align-items:center] [gap:8px] [padding:8px_16px] [border-radius:var(--radius-lg)] [background:var(--accent-glow)] [border:1px_solid_var(--border-accent)] [color:var(--accent-primary)] [font-weight:700] [font-size:0.85rem] [letter-spacing:0.04em]">
                <Shield size={16} />
                {verdict || "UNKNOWN"}
            </div>
        );
    }

    if (tone === "secondary") {
        return (
            <div className="[display:inline-flex] [align-items:center] [gap:8px] [padding:8px_16px] [border-radius:var(--radius-lg)] [background:var(--bg-active)] [border:1px_solid_var(--accent-secondary)] [color:var(--accent-secondary)] [font-weight:700] [font-size:0.85rem] [letter-spacing:0.04em]">
                <Target size={16} />
                {verdict || "UNKNOWN"}
            </div>
        );
    }

    return (
        <div className="[display:inline-flex] [align-items:center] [gap:8px] [padding:8px_16px] [border-radius:var(--radius-lg)] [background:var(--glass-bg)] [border:1px_solid_var(--glass-border)] [color:var(--text-secondary)] [font-weight:700] [font-size:0.85rem] [letter-spacing:0.04em]">
            <TrendingUp size={16} />
            {verdict || "UNKNOWN"}
        </div>
    );
}
