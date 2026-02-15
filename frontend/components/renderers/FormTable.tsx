/**
 * FormTable.tsx — Recent Form Display with Emoji Results
 * 
 * Used by: team_form (output_type: "form_table")
 * 
 * Data shape: List of { Date, Opponent, Venue, Result, TeamScore, OppScore, RawResult }
 * Result is one of: WIN, LOSS, TIE, NR
 * 
 * Features:
 *   - Result emoji indicator (✅ ❌ 🤝 ➖)
 *   - Color-coded result badges
 *   - Form streak summary bar
 *   - Match-by-match detail cards
 */
"use client";

import { Calendar, MapPin, Swords } from "lucide-react";

interface FormTableProps {
    data: Record<string, unknown>[];
}

export default function FormTable({ data }: FormTableProps) {
    if (!data || data.length === 0) {
        return (
            <div style={{ padding: "20px", textAlign: "center", color: "var(--text-muted)" }}>
                No recent form data available.
            </div>
        );
    }

    // Calculate form summary
    const wins = data.filter((r) => String(r["Result"]).toUpperCase() === "WIN").length;
    const losses = data.filter((r) => String(r["Result"]).toUpperCase() === "LOSS").length;
    const ties = data.length - wins - losses;

    return (
        <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
            {/* ── Form Streak Summary ──────────────────────────────────────── */}
            <div
                className="glass-card"
                style={{
                    padding: "16px 20px",
                    display: "flex",
                    alignItems: "center",
                    gap: "20px",
                    flexWrap: "wrap",
                }}
            >
                {/* Form dots */}
                <div style={{ display: "flex", gap: "6px", alignItems: "center" }}>
                    {data.map((row, i) => {
                        const res = String(row["Result"]).toUpperCase();
                        return (
                            <div
                                key={i}
                                title={`${row["Opponent"]} — ${res}`}
                                style={{
                                    width: 28,
                                    height: 28,
                                    borderRadius: "50%",
                                    display: "flex",
                                    alignItems: "center",
                                    justifyContent: "center",
                                    fontSize: "0.75rem",
                                    fontWeight: 800,
                                    background: getResultBg(res),
                                    color: getResultColor(res),
                                    border: `2px solid ${getResultColor(res)}30`,
                                    transition: "transform var(--transition-fast)",
                                    cursor: "default",
                                }}
                            >
                                {getResultLetter(res)}
                            </div>
                        );
                    })}
                </div>

                {/* Summary stats */}
                <div style={{ display: "flex", gap: "16px", fontSize: "0.85rem" }}>
                    <span style={{ fontWeight: 700, color: "var(--tier-elite)" }}>{wins}W</span>
                    <span style={{ fontWeight: 700, color: "var(--tier-danger)" }}>{losses}L</span>
                    {ties > 0 && (
                        <span style={{ fontWeight: 700, color: "var(--text-muted)" }}>{ties}NR</span>
                    )}
                </div>
            </div>

            {/* ── Match Cards ──────────────────────────────────────────────── */}
            {data.map((row, i) => {
                const result = String(row["Result"]).toUpperCase();
                return (
                    <div
                        key={i}
                        style={{
                            display: "flex",
                            alignItems: "center",
                            gap: "16px",
                            padding: "14px 18px",
                            background: "var(--bg-elevated)",
                            borderRadius: "var(--radius-md)",
                            border: "1px solid var(--border-subtle)",
                            borderLeft: `4px solid ${getResultColor(result)}`,
                            transition: "background var(--transition-fast), border-color var(--transition-fast)",
                        }}
                        onMouseEnter={(e) => {
                            (e.currentTarget).style.background = "var(--bg-hover)";
                        }}
                        onMouseLeave={(e) => {
                            (e.currentTarget).style.background = "var(--bg-elevated)";
                        }}
                    >
                        {/* Result emoji */}
                        <div
                            style={{
                                width: 36,
                                height: 36,
                                borderRadius: "var(--radius-md)",
                                background: getResultBg(result),
                                display: "flex",
                                alignItems: "center",
                                justifyContent: "center",
                                fontSize: "1.1rem",
                                flexShrink: 0,
                            }}
                        >
                            {getResultEmoji(result)}
                        </div>

                        {/* Match details */}
                        <div style={{ flex: 1, minWidth: 0 }}>
                            <div style={{
                                display: "flex", alignItems: "center", gap: "8px",
                                marginBottom: "4px", flexWrap: "wrap",
                            }}>
                                <span style={{
                                    fontSize: "0.92rem", fontWeight: 700, color: "var(--text-primary)",
                                }}>
                                    vs {String(row["Opponent"])}
                                </span>
                                <span
                                    className={`badge ${result === "WIN"
                                        ? "badge-elite"
                                        : result === "LOSS"
                                            ? "badge-danger"
                                            : "badge-caution"
                                        }`}
                                    style={{ fontSize: "0.65rem" }}
                                >
                                    {result}
                                </span>
                            </div>
                            <div style={{
                                display: "flex", gap: "12px", fontSize: "0.78rem",
                                color: "var(--text-muted)", flexWrap: "wrap",
                            }}>
                                <span style={{ display: "inline-flex", alignItems: "center", gap: "4px" }}>
                                    <Calendar size={12} />
                                    {String(row["Date"])}
                                </span>
                                <span style={{ display: "inline-flex", alignItems: "center", gap: "4px" }}>
                                    <MapPin size={12} />
                                    {String(row["Venue"])}
                                </span>
                            </div>
                        </div>

                        {/* Scores */}
                        <div style={{ textAlign: "right", flexShrink: 0 }}>
                            <div style={{
                                display: "flex", alignItems: "center", gap: "8px",
                                justifyContent: "flex-end",
                            }}>
                                <span style={{
                                    fontSize: "0.9rem", fontWeight: 700,
                                    color: result === "WIN" ? "var(--tier-elite)" : "var(--text-primary)",
                                    fontVariantNumeric: "tabular-nums",
                                }}>
                                    {String(row["TeamScore"])}
                                </span>
                                <Swords size={12} style={{ color: "var(--text-disabled)" }} />
                                <span style={{
                                    fontSize: "0.9rem", fontWeight: 500,
                                    color: "var(--text-secondary)",
                                    fontVariantNumeric: "tabular-nums",
                                }}>
                                    {String(row["OppScore"])}
                                </span>
                            </div>
                        </div>
                    </div>
                );
            })}
        </div>
    );
}

// ── Helpers ──────────────────────────────────────────────────────────────

function getResultEmoji(result: string): string {
    switch (result) {
        case "WIN": return "✅";
        case "LOSS": return "❌";
        case "TIE": return "🤝";
        default: return "➖";
    }
}

function getResultLetter(result: string): string {
    switch (result) {
        case "WIN": return "W";
        case "LOSS": return "L";
        case "TIE": return "T";
        default: return "-";
    }
}

function getResultColor(result: string): string {
    switch (result) {
        case "WIN": return "var(--tier-elite)";
        case "LOSS": return "var(--tier-danger)";
        case "TIE": return "var(--tier-caution)";
        default: return "var(--text-disabled)";
    }
}

function getResultBg(result: string): string {
    switch (result) {
        case "WIN": return "rgba(34, 197, 94, 0.12)";
        case "LOSS": return "rgba(239, 68, 68, 0.12)";
        case "TIE": return "rgba(245, 158, 11, 0.12)";
        default: return "rgba(148, 163, 184, 0.08)";
    }
}
