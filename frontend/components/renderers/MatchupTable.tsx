/**
 * MatchupTable.tsx — Batter vs Bowler Grid
 * 
 * Used by: matchups (output_type: "matchup_table")
 * 
 * Data shape: List of matchup records with batter, bowler, balls, runs, dismissals, etc.
 * 
 * Features:
 *   - Batter vs Bowler matchup rows
 *   - "Bunny Alert" highlighting (high dismissal rate)
 *   - Color-coded threat level
 *   - SR calculation displayed
 */
"use client";

import { Crosshair, AlertTriangle } from "lucide-react";

interface MatchupTableProps {
    data: Record<string, unknown>[];
}

const HIDDEN_COLS = new Set(["MATCH_IDS", "match_ids"]);

export default function MatchupTable({ data }: MatchupTableProps) {
    if (!data || data.length === 0) {
        return (
            <div style={{ padding: "20px", textAlign: "center", color: "var(--text-muted)" }}>
                No matchup data available.
            </div>
        );
    }

    const columns = Object.keys(data[0]).filter((c) => !HIDDEN_COLS.has(c));

    return (
        <div>
            {/* Header */}
            <div style={{
                display: "flex", alignItems: "center", gap: "8px", marginBottom: "12px",
            }}>
                <Crosshair size={16} style={{ color: "var(--accent-primary)" }} />
                <span style={{
                    fontSize: "0.8rem", fontWeight: 600, color: "var(--text-secondary)",
                    textTransform: "uppercase", letterSpacing: "0.04em",
                }}>
                    Player Matchups ({data.length} records)
                </span>
            </div>

            <div style={{ overflowX: "auto" }}>
                <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "0.825rem" }}>
                    <thead>
                        <tr>
                            {columns.map((col) => (
                                <th
                                    key={col}
                                    style={{
                                        textAlign: isTextCol(col) ? "left" : "right",
                                        padding: "10px 12px",
                                        borderBottom: "2px solid var(--border-default)",
                                        color: "var(--text-muted)",
                                        fontWeight: 600,
                                        textTransform: "uppercase",
                                        fontSize: "0.7rem",
                                        letterSpacing: "0.05em",
                                        whiteSpace: "nowrap",
                                    }}
                                >
                                    {col}
                                </th>
                            ))}
                        </tr>
                    </thead>
                    <tbody>
                        {data.map((row, i) => {
                            const isBunny = isBunnyAlert(row);
                            return (
                                <tr
                                    key={i}
                                    style={{
                                        borderBottom: "1px solid var(--border-subtle)",
                                        background: isBunny ? "rgba(239, 68, 68, 0.06)" : "transparent",
                                        transition: "background var(--transition-fast)",
                                    }}
                                    onMouseEnter={(e) => {
                                        (e.currentTarget).style.background = isBunny
                                            ? "rgba(239, 68, 68, 0.10)"
                                            : "var(--bg-hover)";
                                    }}
                                    onMouseLeave={(e) => {
                                        (e.currentTarget).style.background = isBunny
                                            ? "rgba(239, 68, 68, 0.06)"
                                            : "transparent";
                                    }}
                                >
                                    {columns.map((col) => {
                                        const val = row[col];
                                        return (
                                            <td
                                                key={col}
                                                style={{
                                                    padding: "10px 12px",
                                                    textAlign: isTextCol(col) ? "left" : "right",
                                                    whiteSpace: "nowrap",
                                                    fontVariantNumeric: !isTextCol(col) ? "tabular-nums" : undefined,
                                                    fontWeight: isTextCol(col) ? 600 : 400,
                                                    color: getDismissalColor(col, val),
                                                }}
                                            >
                                                <span style={{ display: "inline-flex", alignItems: "center", gap: "4px" }}>
                                                    {val === null || val === undefined ? "—" : String(val)}
                                                    {col.toLowerCase().includes("dismissal") && isBunny && i === 0 && (
                                                        <AlertTriangle size={12} style={{ color: "var(--tier-danger)" }} />
                                                    )}
                                                </span>
                                            </td>
                                        );
                                    })}
                                </tr>
                            );
                        })}
                    </tbody>
                </table>
            </div>

            {/* Bunny Alert Legend */}
            {data.some(isBunnyAlert) && (
                <div style={{
                    display: "flex", alignItems: "center", gap: "6px", marginTop: "10px",
                    fontSize: "0.75rem", color: "var(--tier-danger)",
                }}>
                    <AlertTriangle size={12} />
                    <span>Bunny Alert: High dismissal rate detected</span>
                </div>
            )}
        </div>
    );
}

// ── Helpers ──────────────────────────────────────────────────────────────

function isTextCol(col: string): boolean {
    const lc = col.toLowerCase();
    return lc.includes("batter") || lc.includes("bowler") || lc.includes("player") ||
        lc.includes("name") || lc.includes("type");
}

function isBunnyAlert(row: Record<string, unknown>): boolean {
    const dismissals = Number(row["Dismissals"] ?? row["dismissals"] ?? row["Outs"] ?? 0);
    const balls = Number(row["Balls"] ?? row["balls"] ?? 0);
    // If dismissed 3+ times, or once per 15 balls or fewer
    return dismissals >= 3 || (dismissals >= 2 && balls > 0 && balls / dismissals <= 15);
}

function getDismissalColor(col: string, val: unknown): string {
    const lc = col.toLowerCase();
    if (lc.includes("dismissal") || lc.includes("outs")) {
        const n = Number(val);
        if (n >= 3) return "var(--tier-danger)";
        if (n >= 2) return "var(--tier-caution)";
    }
    if (val === null || val === undefined) return "var(--text-disabled)";
    return "var(--text-primary)";
}
