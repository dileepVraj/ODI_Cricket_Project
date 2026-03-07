/**
 * MatchupTable.tsx - Batter vs Bowler Grid
 *
 * Used by: matchups (output_type: "matchup_table")
 */
"use client";

import { Crosshair, AlertTriangle } from "lucide-react";
import EmptyState from "@/components/common/EmptyState";
import { MatchupRow, toMatchupRows } from "@/lib/types";

interface MatchupTableProps {
    data: Record<string, unknown>[];
}

const HIDDEN_COLS = new Set([
    "MATCH_IDS",
    "match_ids",
    "highlight_flags",
    "cell_tones",
    "derived_badges",
    "DismissalTone",
]);

export default function MatchupTable({ data }: MatchupTableProps) {
    if (!data || data.length === 0) {
        return <EmptyState message="No matchup data available." />;
    }

    const rows = toMatchupRows(data);
    const columns = Object.keys(rows[0]).filter((c) => !HIDDEN_COLS.has(c));
    const hasBunnyAlert = rows.some(rowHasBunnyAlert);

    return (
        <div>
            <div className="[display:flex] [align-items:center] [gap:8px] [margin-bottom:12px]">
                <Crosshair size={16} className="[color:var(--accent-primary)]" />
                <span className="[font-size:0.8rem] [font-weight:600] [color:var(--text-secondary)] [text-transform:uppercase] [letter-spacing:0.04em]">
                    Player Matchups ({rows.length} records)
                </span>
            </div>

            <div className="[overflow-x:auto]">
                <table className="[width:100%] [border-collapse:collapse] [font-size:0.825rem]">
                    <thead>
                        <tr>
                            {columns.map((col) => (
                                <th
                                    key={col}
                                    className={`[padding:10px_12px] [border-bottom:2px_solid_var(--border-default)] [color:var(--text-muted)] [font-weight:600] [text-transform:uppercase] [font-size:0.7rem] [letter-spacing:0.05em] [white-space:nowrap] ${isTextCol(col) ? "[text-align:left]" : "[text-align:right]"}`}
                                >
                                    {col}
                                </th>
                            ))}
                        </tr>
                    </thead>
                    <tbody>
                        {rows.map((row, i) => {
                            const isBunny = rowHasBunnyAlert(row);
                            return (
                                <tr
                                    key={i}
                                    className={`[border-bottom:1px_solid_var(--border-subtle)] [transition:background_var(--transition-fast)] ${isBunny ? "[background:var(--bg-elevated)] [box-shadow:inset_3px_0_0_var(--tier-danger)]" : "[background:transparent]"}`}
                                    onMouseEnter={(e) => {
                                        e.currentTarget.style.background = isBunny
                                            ? "var(--bg-hover)"
                                            : "var(--bg-hover)";
                                    }}
                                    onMouseLeave={(e) => {
                                        e.currentTarget.style.background = isBunny
                                            ? "var(--bg-elevated)"
                                            : "transparent";
                                    }}
                                >
                                    {columns.map((col) => {
                                        const val = row[col];
                                        return (
                                            <td
                                                key={col}
                                                className={`[padding:10px_12px] [white-space:nowrap] ${isTextCol(col) ? "[text-align:left] [font-weight:600]" : "[text-align:right] [font-weight:400] font-numeric"} ${resolveCellColor(row, col, val)}`}
                                            >
                                                <span className="[display:inline-flex] [align-items:center] [gap:4px]">
                                                    {val === null || val === undefined ? "-" : String(val)}
                                                    {(col.toLowerCase().includes("outs") || col.toLowerCase().includes("dismissal")) && isBunny && (
                                                        <AlertTriangle size={12} className="[color:var(--tier-danger)]" />
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

            {hasBunnyAlert && (
                <div className="[display:flex] [align-items:center] [gap:6px] [margin-top:10px] [font-size:0.75rem] [color:var(--tier-danger)]">
                    <AlertTriangle size={12} />
                    <span>Bunny Alert: High dismissal rate detected</span>
                </div>
            )}
        </div>
    );
}

function isTextCol(col: string): boolean {
    const lc = col.toLowerCase();
    return lc.includes("batter") || lc.includes("bowler") || lc.includes("player") ||
        lc.includes("name") || lc.includes("type");
}

function rowHasBunnyAlert(row: MatchupRow): boolean {
    const explicit = row.highlight_flags?.bunny_alert;
    if (typeof explicit === "boolean") return explicit;

    const legacy = row["IsBunny"] ?? row["is_bunny"];
    if (typeof legacy === "boolean") return legacy;
    return false;
}

function resolveCellColor(row: MatchupRow, col: string, val: unknown): string {
    const tone = row.cell_tones?.[col] ?? row.cell_tones?.Outs;
    if (tone === "elite") return "[color:var(--tier-elite)]";
    if (tone === "strong") return "[color:var(--tier-strong)]";
    if (tone === "caution") return "[color:var(--tier-caution)]";
    if (tone === "danger") return "[color:var(--tier-danger)]";
    if (tone === "muted") return "[color:var(--text-disabled)]";
    if (val === null || val === undefined) return "[color:var(--text-disabled)]";
    return "[color:var(--text-primary)]";
}
