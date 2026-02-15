/**
 * PredictionCard.tsx — Score Projection Display
 * 
 * Used by: predict_score (output_type: "prediction_card")
 * 
 * Data shape from PredictorEngine: {
 *   Venue_Par, Predicted_Total, Range_Low, Range_High,
 *   Batting_Strength, Bowling_Threat, Venue_Adjusted_Par,
 *   batting_team, bowling_team, venue, Adjustment_Notes: [...]
 * }
 * 
 * Features:
 *   - Large predicted score with range
 *   - Score dial visualization
 *   - Breakdown cards: Venue Par, Batting Power, Bowling Threat
 *   - Adjustment notes list
 */
"use client";

import { Target, TrendingUp, TrendingDown, Gauge, Info } from "lucide-react";

interface PredictionCardProps {
    data: Record<string, unknown>;
}

export default function PredictionCard({ data }: PredictionCardProps) {
    if (!data || typeof data !== "object") {
        return (
            <div style={{ padding: "20px", textAlign: "center", color: "var(--text-muted)" }}>
                No prediction data available.
            </div>
        );
    }

    const predicted = Number(data["Predicted_Total"] ?? data["predicted_total"] ?? 0);
    const rangeLow = Number(data["Range_Low"] ?? data["range_low"] ?? predicted - 15);
    const rangeHigh = Number(data["Range_High"] ?? data["range_high"] ?? predicted + 15);
    const venuePar = Number(data["Venue_Par"] ?? data["venue_par"] ?? 0);
    const venueAdjusted = Number(data["Venue_Adjusted_Par"] ?? data["venue_adjusted_par"] ?? venuePar);
    const batStrength = data["Batting_Strength"] ?? data["batting_strength"] ?? "—";
    const bowlThreat = data["Bowling_Threat"] ?? data["bowling_threat"] ?? "—";
    const batTeam = String(data["batting_team"] ?? "Batting Team");
    const bowlTeam = String(data["bowling_team"] ?? "Bowling Team");
    const venue = String(data["venue"] ?? "");
    const notes = (data["Adjustment_Notes"] ?? data["adjustment_notes"] ?? []) as string[];

    // Score quality indicator
    const diff = predicted - venuePar;
    const aboveParText = diff > 0 ? `+${diff} above par` : diff < 0 ? `${diff} below par` : "At par";

    return (
        <div style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
            {/* ── Hero: Predicted Score ─────────────────────────────────────── */}
            <div
                className="glass-card"
                style={{
                    padding: "28px 24px",
                    textAlign: "center",
                    border: "1px solid var(--border-accent)",
                    position: "relative",
                    overflow: "hidden",
                }}
            >
                {/* Subtle gradient glow behind */}
                <div style={{
                    position: "absolute", top: "-50%", left: "50%", transform: "translateX(-50%)",
                    width: 300, height: 300, borderRadius: "50%",
                    background: "radial-gradient(circle, var(--accent-glow) 0%, transparent 70%)",
                    pointerEvents: "none", opacity: 0.6,
                }} />

                <div style={{ position: "relative" }}>
                    <div style={{
                        fontSize: "0.7rem", textTransform: "uppercase", letterSpacing: "0.08em",
                        color: "var(--text-disabled)", fontWeight: 600, marginBottom: "8px",
                    }}>
                        Predicted 1st Innings Total
                    </div>
                    <div style={{
                        fontSize: "3.2rem", fontWeight: 900,
                        background: "linear-gradient(135deg, var(--accent-primary), var(--accent-secondary))",
                        WebkitBackgroundClip: "text",
                        WebkitTextFillColor: "transparent",
                        lineHeight: 1,
                        marginBottom: "8px",
                        fontVariantNumeric: "tabular-nums",
                    }}>
                        {predicted}
                    </div>
                    <div style={{
                        fontSize: "0.9rem", color: "var(--text-muted)", fontWeight: 500,
                    }}>
                        Range: <span style={{ fontWeight: 700, color: "var(--text-primary)" }}>{rangeLow}</span>
                        {" — "}
                        <span style={{ fontWeight: 700, color: "var(--text-primary)" }}>{rangeHigh}</span>
                    </div>

                    {/* Teams & Venue */}
                    <div style={{
                        marginTop: "12px", fontSize: "0.8rem", color: "var(--text-muted)",
                        display: "flex", justifyContent: "center", gap: "16px", flexWrap: "wrap",
                    }}>
                        <span><strong style={{ color: "var(--text-primary)" }}>{batTeam}</strong> batting</span>
                        <span>vs <strong style={{ color: "var(--text-primary)" }}>{bowlTeam}</strong></span>
                        {venue && <span>at <strong>{venue}</strong></span>}
                    </div>
                </div>
            </div>

            {/* ── Score Gauge Bar ───────────────────────────────────────────── */}
            <div style={{
                background: "var(--bg-elevated)", borderRadius: "var(--radius-lg)",
                padding: "16px 20px", border: "1px solid var(--border-subtle)",
            }}>
                <div style={{
                    display: "flex", justifyContent: "space-between", marginBottom: "8px",
                    fontSize: "0.75rem", color: "var(--text-muted)", fontWeight: 500,
                }}>
                    <span>150</span>
                    <span style={{ color: diff >= 0 ? "var(--tier-elite)" : "var(--tier-caution)", fontWeight: 700 }}>
                        {aboveParText}
                    </span>
                    <span>350</span>
                </div>
                {/* Gauge track */}
                <div style={{
                    position: "relative", height: 10, borderRadius: 5,
                    background: "var(--bg-active)",
                }}>
                    {/* Par marker */}
                    <div style={{
                        position: "absolute",
                        left: `${Math.min(100, Math.max(0, ((venuePar - 150) / 200) * 100))}%`,
                        top: -4, width: 2, height: 18, background: "var(--text-disabled)",
                        borderRadius: 1,
                    }} />
                    {/* Predicted range */}
                    <div style={{
                        position: "absolute",
                        left: `${Math.max(0, ((rangeLow - 150) / 200) * 100)}%`,
                        width: `${Math.min(100 - ((rangeLow - 150) / 200) * 100, ((rangeHigh - rangeLow) / 200) * 100)}%`,
                        height: "100%",
                        background: "linear-gradient(90deg, var(--accent-primary), var(--accent-secondary))",
                        borderRadius: 5, opacity: 0.6,
                    }} />
                    {/* Predicted dot */}
                    <div style={{
                        position: "absolute",
                        left: `${Math.min(100, Math.max(0, ((predicted - 150) / 200) * 100))}%`,
                        top: -3, width: 16, height: 16, borderRadius: "50%",
                        background: "var(--accent-primary)",
                        border: "3px solid var(--bg-base)",
                        transform: "translateX(-50%)",
                        boxShadow: "0 0 8px var(--accent-primary)",
                    }} />
                </div>
                <div style={{
                    display: "flex", justifyContent: "space-between", marginTop: "6px",
                    fontSize: "0.68rem", color: "var(--text-disabled)",
                }}>
                    <span>Low Scoring</span>
                    <span>▲ Venue Par: {venuePar}</span>
                    <span>High Scoring</span>
                </div>
            </div>

            {/* ── Breakdown Cards ───────────────────────────────────────────── */}
            <div style={{
                display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(200px, 1fr))",
                gap: "12px",
            }}>
                <BreakdownCard
                    icon={<Gauge size={18} />}
                    label="Venue Par"
                    value={String(venuePar)}
                    subLabel={`Adjusted: ${venueAdjusted}`}
                    color="var(--accent-tertiary)"
                />
                <BreakdownCard
                    icon={<TrendingUp size={18} />}
                    label="Batting Strength"
                    value={String(batStrength)}
                    subLabel={batTeam}
                    color="var(--tier-elite)"
                />
                <BreakdownCard
                    icon={<TrendingDown size={18} />}
                    label="Bowling Threat"
                    value={String(bowlThreat)}
                    subLabel={bowlTeam}
                    color="var(--tier-danger)"
                />
            </div>

            {/* ── Adjustment Notes ──────────────────────────────────────────── */}
            {Array.isArray(notes) && notes.length > 0 && (
                <div style={{
                    background: "var(--bg-elevated)", borderRadius: "var(--radius-md)",
                    padding: "14px 18px", border: "1px solid var(--border-subtle)",
                }}>
                    <div style={{
                        display: "flex", alignItems: "center", gap: "6px", marginBottom: "10px",
                        fontSize: "0.78rem", fontWeight: 600, color: "var(--text-secondary)",
                    }}>
                        <Info size={14} />
                        Adjustment Notes
                    </div>
                    <ul style={{ margin: 0, paddingLeft: "18px" }}>
                        {notes.map((note, i) => (
                            <li key={i} style={{
                                fontSize: "0.8rem", color: "var(--text-muted)", lineHeight: 1.6,
                            }}>
                                {note}
                            </li>
                        ))}
                    </ul>
                </div>
            )}
        </div>
    );
}

// ── Breakdown Card Sub-Component ────────────────────────────────────────

function BreakdownCard({
    icon,
    label,
    value,
    subLabel,
    color,
}: {
    icon: React.ReactNode;
    label: string;
    value: string;
    subLabel: string;
    color: string;
}) {
    return (
        <div style={{
            padding: "16px", background: "var(--bg-elevated)",
            borderRadius: "var(--radius-md)", border: "1px solid var(--border-subtle)",
        }}>
            <div style={{
                display: "flex", alignItems: "center", gap: "8px", marginBottom: "8px",
            }}>
                <div style={{
                    width: 32, height: 32, borderRadius: "var(--radius-sm)",
                    background: `${color}15`, display: "flex",
                    alignItems: "center", justifyContent: "center", color,
                }}>
                    {icon}
                </div>
                <span style={{
                    fontSize: "0.75rem", fontWeight: 600, color: "var(--text-muted)",
                    textTransform: "uppercase", letterSpacing: "0.04em",
                }}>
                    {label}
                </span>
            </div>
            <div style={{
                fontSize: "1.3rem", fontWeight: 800, color: "var(--text-primary)",
                fontVariantNumeric: "tabular-nums",
            }}>
                {value}
            </div>
            <div style={{ fontSize: "0.72rem", color: "var(--text-disabled)", marginTop: "2px" }}>
                {subLabel}
            </div>
        </div>
    );
}
