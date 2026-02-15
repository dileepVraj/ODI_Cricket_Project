/**
 * DataTable.tsx — Sortable, Paginated Data Table
 * 
 * Used by: venue_phases, tactical_matrix, and any generic "table" output.
 * Features:
 *   - Click column header to sort (asc/desc toggle)
 *   - Pagination with configurable page size
 *   - Number columns auto right-aligned
 *   - Color-coded Win% cells
 *   - Hidden columns for internal data (MATCH_IDS)
 */
"use client";

import { useState, useMemo } from "react";
import { ChevronUp, ChevronDown, ChevronsUpDown } from "lucide-react";

interface DataTableProps {
    data: Record<string, unknown>[];
    pageSize?: number;
    title?: string;
}

// Columns to hide from display
const HIDDEN_COLS = new Set(["MATCH_IDS", "match_ids", "RawResult"]);

export default function DataTable({ data, pageSize = 15, title }: DataTableProps) {
    const [sortCol, setSortCol] = useState<string | null>(null);
    const [sortDir, setSortDir] = useState<"asc" | "desc">("asc");
    const [page, setPage] = useState(0);

    if (!data || data.length === 0) {
        return (
            <div style={{ padding: "20px", textAlign: "center", color: "var(--text-muted)" }}>
                No data available.
            </div>
        );
    }

    const allColumns = Object.keys(data[0]);
    const columns = allColumns.filter((c) => !HIDDEN_COLS.has(c));

    function handleSort(col: string) {
        if (sortCol === col) {
            setSortDir((d) => (d === "asc" ? "desc" : "asc"));
        } else {
            setSortCol(col);
            setSortDir("asc");
        }
        setPage(0);
    }

    const sorted = useMemo(() => {
        if (!sortCol) return data;
        return [...data].sort((a, b) => {
            let va = a[sortCol];
            let vb = b[sortCol];
            // Try numeric comparison
            const na = parseFloat(String(va).replace(/[%,]/g, ""));
            const nb = parseFloat(String(vb).replace(/[%,]/g, ""));
            if (!isNaN(na) && !isNaN(nb)) {
                return sortDir === "asc" ? na - nb : nb - na;
            }
            // String comparison
            const sa = String(va ?? "").toLowerCase();
            const sb = String(vb ?? "").toLowerCase();
            return sortDir === "asc" ? sa.localeCompare(sb) : sb.localeCompare(sa);
        });
    }, [data, sortCol, sortDir]);

    const totalPages = Math.ceil(sorted.length / pageSize);
    const paged = sorted.slice(page * pageSize, (page + 1) * pageSize);

    return (
        <div>
            {title && (
                <h4 style={{
                    fontSize: "0.85rem", fontWeight: 600, color: "var(--text-secondary)",
                    marginBottom: "12px", textTransform: "uppercase", letterSpacing: "0.04em",
                }}>
                    {title}
                </h4>
            )}
            <div style={{ overflowX: "auto" }}>
                <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "0.825rem" }}>
                    <thead>
                        <tr>
                            {columns.map((col) => (
                                <th
                                    key={col}
                                    onClick={() => handleSort(col)}
                                    style={{
                                        textAlign: isNumericColumn(data, col) ? "right" : "left",
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
                                        transition: "color var(--transition-fast)",
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
                        {paged.map((row, i) => {
                            const isOverallRow = String(row["Opponent"] ?? "").includes("OVERALL");
                            return (
                                <tr
                                    key={i}
                                    style={{
                                        borderBottom: "1px solid var(--border-subtle)",
                                        background: isOverallRow ? "var(--accent-glow)" : "transparent",
                                        transition: "background var(--transition-fast)",
                                    }}
                                    onMouseEnter={(e) => {
                                        if (!isOverallRow) (e.currentTarget).style.background = "var(--bg-hover)";
                                    }}
                                    onMouseLeave={(e) => {
                                        (e.currentTarget).style.background = isOverallRow ? "var(--accent-glow)" : "transparent";
                                    }}
                                >
                                    {columns.map((col) => {
                                        const val = row[col];
                                        const isNum = isNumericValue(val);
                                        return (
                                            <td
                                                key={col}
                                                style={{
                                                    padding: "10px 12px",
                                                    textAlign: isNum ? "right" : "left",
                                                    whiteSpace: "nowrap",
                                                    fontVariantNumeric: isNum ? "tabular-nums" : undefined,
                                                    fontWeight: isOverallRow ? 700 : 400,
                                                    color: getCellColor(col, val),
                                                }}
                                            >
                                                {formatCell(col, val)}
                                            </td>
                                        );
                                    })}
                                </tr>
                            );
                        })}
                    </tbody>
                </table>
            </div>

            {/* Pagination */}
            {totalPages > 1 && (
                <div style={{
                    display: "flex", justifyContent: "space-between", alignItems: "center",
                    marginTop: "12px", fontSize: "0.78rem", color: "var(--text-muted)",
                }}>
                    <span>
                        Showing {page * pageSize + 1}–{Math.min((page + 1) * pageSize, sorted.length)} of {sorted.length}
                    </span>
                    <div style={{ display: "flex", gap: "4px" }}>
                        <button
                            className="btn-ghost"
                            onClick={() => setPage((p) => Math.max(0, p - 1))}
                            disabled={page === 0}
                            style={{ padding: "4px 10px", fontSize: "0.75rem", opacity: page === 0 ? 0.4 : 1 }}
                        >
                            Prev
                        </button>
                        <button
                            className="btn-ghost"
                            onClick={() => setPage((p) => Math.min(totalPages - 1, p + 1))}
                            disabled={page >= totalPages - 1}
                            style={{ padding: "4px 10px", fontSize: "0.75rem", opacity: page >= totalPages - 1 ? 0.4 : 1 }}
                        >
                            Next
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
}

// ── Helpers ──────────────────────────────────────────────────────────────

function isNumericColumn(data: Record<string, unknown>[], col: string): boolean {
    const sample = data.slice(0, 5).map((r) => r[col]);
    return sample.some((v) => typeof v === "number" || (!isNaN(parseFloat(String(v).replace(/[%,]/g, "")))));
}

function isNumericValue(val: unknown): boolean {
    return typeof val === "number" || (typeof val === "string" && /^[\d,.]+%?$/.test(val.trim()));
}

function getCellColor(col: string, val: unknown): string {
    const str = String(val ?? "");
    // Win% color coding
    if (col.toLowerCase().includes("win") && str.includes("%")) {
        const n = parseFloat(str);
        if (n >= 60) return "var(--tier-elite)";
        if (n >= 45) return "var(--tier-strong)";
        if (n >= 30) return "var(--tier-caution)";
        if (n > 0) return "var(--tier-danger)";
    }
    // Form guide emoji pass-through
    if (str.includes("✅") || str.includes("❌") || str.includes("🤝")) {
        return "var(--text-primary)";
    }
    if (val === null || val === undefined) return "var(--text-disabled)";
    return "var(--text-primary)";
}

function formatCell(col: string, val: unknown): string {
    if (val === null || val === undefined) return "—";
    return String(val);
}
