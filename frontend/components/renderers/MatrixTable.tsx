/**
 * MatrixTable.tsx — Opponent-per-Row Dominance Matrix
 * 
 * Used by: home_dominance, away_performance, global_performance, continent_perf
 * 
 * Data shape: List of { Opponent, Mat, Won, Lost, Tie/NR, Win%, Last 5, Avg 1st, ... }
 * First row may be "⚡ OVERALL" summary.
 * 
 * Features:
 *   - OVERALL row highlighted with accent glow
 *   - Win% color-coded (green→red 4-tier)
 *   - Last 5 form guide with emoji styling
 *   - Sortable columns
 */
"use client";

import { useState, useMemo } from "react";
import { ChevronUp, ChevronDown, ChevronsUpDown, Trophy } from "lucide-react";

interface MatrixTableProps {
    data: Record<string, unknown>[];
}

const HIDDEN_COLS = new Set(["MATCH_IDS", "match_ids"]);

export default function MatrixTable({ data }: MatrixTableProps) {
    const [sortCol, setSortCol] = useState<string | null>(null);
    const [sortDir, setSortDir] = useState<"asc" | "desc">("desc");

    if (!data || data.length === 0) {
        return (
            <div style={{ padding: "20px", textAlign: "center", color: "var(--text-muted)" }}>
                No matrix data available.
            </div>
        );
    }

    // Separate OVERALL row from the rest
    const overallRow = data.find((r) => String(r["Opponent"] ?? "").includes("OVERALL"));
    const regularRows = data.filter((r) => !String(r["Opponent"] ?? "").includes("OVERALL"));

    const allColumns = Object.keys(data[0]).filter((c) => !HIDDEN_COLS.has(c));

    function handleSort(col: string) {
        if (sortCol === col) {
            setSortDir((d) => (d === "asc" ? "desc" : "asc"));
        } else {
            setSortCol(col);
            setSortDir("desc");
        }
    }

    const sortedRows = useMemo(() => {
        if (!sortCol) return regularRows;
        return [...regularRows].sort((a, b) => {
            const va = parseFloat(String(a[sortCol] ?? "0").replace(/[%,]/g, ""));
            const vb = parseFloat(String(b[sortCol] ?? "0").replace(/[%,]/g, ""));
            if (!isNaN(va) && !isNaN(vb)) {
                return sortDir === "asc" ? va - vb : vb - va;
            }
            return sortDir === "asc"
                ? String(a[sortCol] ?? "").localeCompare(String(b[sortCol] ?? ""))
                : String(b[sortCol] ?? "").localeCompare(String(a[sortCol] ?? ""));
        });
    }, [regularRows, sortCol, sortDir]);

    return (
        <div style={{ overflowX: "auto" }}>
            {/* OVERALL Summary Card (if exists) */}
            {overallRow && (
                <div
                    className="glass-card"
                    style={{
                        padding: "16px 20px",
                        marginBottom: "16px",
                        display: "flex",
                        alignItems: "center",
                        gap: "16px",
                        flexWrap: "wrap",
                        border: "1px solid var(--border-accent)",
                    }}
                >
                    <div style={{
                        width: 36, height: 36, borderRadius: "var(--radius-md)",
                        background: "var(--accent-glow)", display: "flex",
                        alignItems: "center", justifyContent: "center",
                    }}>
                        <Trophy size={18} style={{ color: "var(--accent-primary)" }} />
                    </div>
                    <div style={{ flex: 1 }}>
                        <div style={{
                            fontSize: "0.7rem", textTransform: "uppercase", letterSpacing: "0.06em",
                            color: "var(--text-disabled)", fontWeight: 600,
                        }}>
                            Overall Record
                        </div>
                        <div style={{ fontSize: "1.1rem", fontWeight: 800, color: "var(--text-primary)" }}>
                            {String(overallRow["Won"] ?? 0)}W – {String(overallRow["Lost"] ?? 0)}L
                            {overallRow["Tie/NR"] ? ` – ${overallRow["Tie/NR"]}NR` : ""}
                        </div>
                    </div>
                    {allColumns
                        .filter((c) => c !== "Opponent" && c !== "Won" && c !== "Lost" && c !== "Tie/NR")
                        .slice(0, 4)
                        .map((col) => (
                            <div key={col} style={{ textAlign: "center", minWidth: 60 }}>
                                <div style={{
                                    fontSize: "0.65rem", textTransform: "uppercase",
                                    color: "var(--text-disabled)", fontWeight: 600,
                                }}>
                                    {col}
                                </div>
                                <div style={{
                                    fontSize: "0.95rem", fontWeight: 700,
                                    color: col.toLowerCase().includes("win")
                                        ? getWinColor(overallRow[col])
                                        : "var(--text-primary)",
                                }}>
                                    {String(overallRow[col] ?? "—")}
                                </div>
                            </div>
                        ))}
                </div>
            )}

            {/* Matrix Table */}
            <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "0.825rem" }}>
                <thead>
                    <tr>
                        {allColumns.map((col) => (
                            <th
                                key={col}
                                onClick={() => handleSort(col)}
                                style={{
                                    textAlign: col === "Opponent" || col === "Last 5" ? "left" : "right",
                                    padding: "10px 12px",
                                    borderBottom: "2px solid var(--border-default)",
                                    color: sortCol === col ? "var(--accent-primary)" : "var(--text-muted)",
                                    fontWeight: 600,
                                    textTransform: "uppercase",
                                    fontSize: "0.7rem",
                                    letterSpacing: "0.05em",
                                    whiteSpace: "nowrap",
                                    cursor: "pointer",
                                    userSelect: "none",
                                }}
                            >
                                <span style={{ display: "inline-flex", alignItems: "center", gap: "4px" }}>
                                    {col}
                                    {sortCol === col ? (
                                        sortDir === "asc" ? <ChevronUp size={12} /> : <ChevronDown size={12} />
                                    ) : (
                                        <ChevronsUpDown size={10} style={{ opacity: 0.3 }} />
                                    )}
                                </span>
                            </th>
                        ))}
                    </tr>
                </thead>
                <tbody>
                    {sortedRows.map((row, i) => (
                        <tr
                            key={i}
                            style={{
                                borderBottom: "1px solid var(--border-subtle)",
                                transition: "background var(--transition-fast)",
                            }}
                            onMouseEnter={(e) => { (e.currentTarget).style.background = "var(--bg-hover)"; }}
                            onMouseLeave={(e) => { (e.currentTarget).style.background = "transparent"; }}
                        >
                            {allColumns.map((col) => {
                                const val = row[col];
                                const isNum = col !== "Opponent" && col !== "Last 5";
                                return (
                                    <td
                                        key={col}
                                        style={{
                                            padding: "10px 12px",
                                            textAlign: col === "Opponent" || col === "Last 5" ? "left" : "right",
                                            whiteSpace: "nowrap",
                                            fontVariantNumeric: isNum ? "tabular-nums" : undefined,
                                            fontWeight: col === "Opponent" ? 600 : 400,
                                            color: col.toLowerCase().includes("win")
                                                ? getWinColor(val)
                                                : val === null || val === undefined
                                                    ? "var(--text-disabled)"
                                                    : "var(--text-primary)",
                                        }}
                                    >
                                        {col === "Last 5" ? (
                                            <FormGuide value={String(val ?? "")} />
                                        ) : (
                                            formatVal(val)
                                        )}
                                    </td>
                                );
                            })}
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
}

// ── Form Guide Sub-Component ────────────────────────────────────────────

function FormGuide({ value }: { value: string }) {
    // The engine returns strings like "✅✅❌✅❌" or "W W L W L"
    const chars = value.split("").filter((c) => c.trim() !== "");
    return (
        <span style={{ display: "inline-flex", gap: "3px", fontSize: "0.9rem" }}>
            {chars.map((c, i) => (
                <span key={i} style={{ fontSize: "0.85rem" }}>
                    {c}
                </span>
            ))}
        </span>
    );
}

// ── Helpers ──────────────────────────────────────────────────────────────

function getWinColor(val: unknown): string {
    const n = parseFloat(String(val ?? "0").replace("%", ""));
    if (isNaN(n)) return "var(--text-primary)";
    if (n >= 60) return "var(--tier-elite)";
    if (n >= 45) return "var(--tier-strong)";
    if (n >= 30) return "var(--tier-caution)";
    if (n > 0) return "var(--tier-danger)";
    return "var(--text-disabled)";
}

function formatVal(val: unknown): string {
    if (val === null || val === undefined) return "—";
    return String(val);
}
