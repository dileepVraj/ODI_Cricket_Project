/**
 * ReportCard.tsx — Key-Value Stat Cards (Venue Bias)
 * 
 * Used by: venue_bias (output_type: "report")
 * 
 * Data shape: Dict with keys like venue_id, total_matches, bat1_wins,
 *   chase_wins, bat1_win_pct, chase_win_pct, bias_verdict, avg_1st_inn, avg_2nd_inn
 * 
 * Features:
 *   - Hero verdict badge (BAT FIRST / BOWL FIRST / NEUTRAL)
 *   - Stat grid with large numbers
 *   - Win% bar visualization
 *   - Hides internal fields (MATCH_IDS, raw_matches)
 */
"use client";

import { Shield, Target, TrendingUp } from "lucide-react";

interface ReportCardProps {
    data: Record<string, unknown>;
}

const HIDDEN_KEYS = new Set(["MATCH_IDS", "raw_matches", "match_ids"]);

export default function ReportCard({ data }: ReportCardProps) {
    if (!data || typeof data !== "object") {
        return (
            <div style={{ padding: "20px", textAlign: "center", color: "var(--text-muted)" }}>
                No report data available.
            </div>
        );
    }

    const verdict = String(data["bias_verdict"] ?? data["verdict"] ?? "");
    const venueId = String(data["venue_id"] ?? data["venue"] ?? "Unknown");
    const bat1Pct = Number(data["bat1_win_pct"] ?? data["bat1_pct"] ?? 0);
    const chasePct = Number(data["chase_win_pct"] ?? data["chase_pct"] ?? 0);

    // Get display entries (excluding hidden + already displayed fields)
    const heroKeys = new Set(["bias_verdict", "verdict", "venue_id", "venue", "bat1_win_pct", "bat1_pct", "chase_win_pct", "chase_pct"]);
    const statEntries = Object.entries(data).filter(
        ([key]) => !HIDDEN_KEYS.has(key) && !heroKeys.has(key)
    );

    return (
        <div style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
            {/* ── Hero Section: Verdict + Venue ──────────────────────────────── */}
            <div
                style={{
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "space-between",
                    flexWrap: "wrap",
                    gap: "16px",
                }}
            >
                <div>
                    <div style={{
                        fontSize: "0.7rem", textTransform: "uppercase", letterSpacing: "0.06em",
                        color: "var(--text-disabled)", fontWeight: 600, marginBottom: "4px",
                    }}>
                        Venue
                    </div>
                    <div style={{
                        fontSize: "1.15rem", fontWeight: 700, color: "var(--text-primary)",
                    }}>
                        {venueId}
                    </div>
                </div>
                <VerdictBadge verdict={verdict} />
            </div>

            {/* ── Win% Bar ──────────────────────────────────────────────────── */}
            <div
                style={{
                    background: "var(--bg-elevated)",
                    borderRadius: "var(--radius-lg)",
                    padding: "16px 20px",
                    border: "1px solid var(--border-subtle)",
                }}
            >
                <div style={{
                    display: "flex", justifyContent: "space-between", marginBottom: "8px",
                    fontSize: "0.78rem", fontWeight: 600,
                }}>
                    <span style={{ color: "var(--accent-primary)" }}>
                        <Shield size={14} style={{ verticalAlign: "middle", marginRight: 4 }} />
                        Bat First: {bat1Pct}%
                    </span>
                    <span style={{ color: "var(--accent-secondary)" }}>
                        Chase: {chasePct}%
                        <Target size={14} style={{ verticalAlign: "middle", marginLeft: 4 }} />
                    </span>
                </div>
                {/* Visual bar */}
                <div style={{
                    display: "flex", height: 12, borderRadius: 6, overflow: "hidden",
                    background: "var(--bg-active)",
                }}>
                    <div style={{
                        width: `${bat1Pct}%`,
                        background: "linear-gradient(90deg, var(--accent-primary), #60A5FA)",
                        borderRadius: "6px 0 0 6px",
                        transition: "width 0.5s ease-out",
                    }} />
                    <div style={{
                        width: `${chasePct}%`,
                        background: "linear-gradient(90deg, #A78BFA, var(--accent-secondary))",
                        borderRadius: "0 6px 6px 0",
                        transition: "width 0.5s ease-out",
                    }} />
                </div>
            </div>

            {/* ── Stat Cards Grid ───────────────────────────────────────────── */}
            <div style={{
                display: "grid",
                gridTemplateColumns: "repeat(auto-fill, minmax(180px, 1fr))",
                gap: "10px",
            }}>
                {statEntries.map(([key, val]) => (
                    <div
                        key={key}
                        style={{
                            padding: "14px 16px",
                            background: "var(--bg-elevated)",
                            borderRadius: "var(--radius-md)",
                            border: "1px solid var(--border-subtle)",
                            transition: "border-color var(--transition-fast)",
                        }}
                        onMouseEnter={(e) => {
                            (e.currentTarget).style.borderColor = "var(--border-strong)";
                        }}
                        onMouseLeave={(e) => {
                            (e.currentTarget).style.borderColor = "var(--border-subtle)";
                        }}
                    >
                        <div style={{
                            fontSize: "0.68rem", textTransform: "uppercase", letterSpacing: "0.05em",
                            color: "var(--text-disabled)", fontWeight: 600, marginBottom: "4px",
                        }}>
                            {key.replace(/_/g, " ")}
                        </div>
                        <div style={{
                            fontSize: "1.15rem", fontWeight: 700,
                            color: "var(--text-primary)",
                            fontVariantNumeric: "tabular-nums",
                        }}>
                            {val === null || val === undefined ? "—" : String(val)}
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}

// ── Verdict Badge Sub-Component ─────────────────────────────────────────

function VerdictBadge({ verdict }: { verdict: string }) {
    const v = verdict.toUpperCase();
    let bg: string, color: string, icon: React.ReactNode;

    if (v.includes("BAT")) {
        bg = "rgba(59, 130, 246, 0.15)";
        color = "var(--accent-primary)";
        icon = <Shield size={16} />;
    } else if (v.includes("BOWL") || v.includes("CHASE")) {
        bg = "rgba(139, 92, 246, 0.15)";
        color = "var(--accent-secondary)";
        icon = <Target size={16} />;
    } else {
        bg = "rgba(148, 163, 184, 0.10)";
        color = "var(--text-secondary)";
        icon = <TrendingUp size={16} />;
    }

    return (
        <div
            style={{
                display: "inline-flex",
                alignItems: "center",
                gap: "8px",
                padding: "8px 16px",
                borderRadius: "var(--radius-lg)",
                background: bg,
                border: `1px solid ${color}30`,
                color,
                fontWeight: 700,
                fontSize: "0.85rem",
                letterSpacing: "0.04em",
            }}
        >
            {icon}
            {verdict || "UNKNOWN"}
        </div>
    );
}
