/**
 * DataTable.tsx - Sortable, Paginated Data Table
 *
 * Used by: venue_phases, tactical_matrix, and generic "table" outputs.
 */
"use client";

import { useState, useMemo } from "react";
import { ChevronUp, ChevronDown, ChevronsUpDown } from "lucide-react";

interface DataTableProps {
    data: Record<string, unknown>[];
    pageSize?: number;
    title?: string;
}

type ToneToken = "elite" | "strong" | "caution" | "danger" | "muted" | "default";

interface DataRow extends Record<string, unknown> {
    cell_tones?: Record<string, ToneToken>;
}

const HIDDEN_COLS = new Set([
    "MATCH_IDS",
    "match_ids",
    "RawResult",
    "cell_tones",
    "highlight_flags",
    "derived_badges",
    "row_kind",
]);

export default function DataTable({ data, pageSize = 15, title }: DataTableProps) {
    const [sortCol, setSortCol] = useState<string | null>(null);
    const [sortDir, setSortDir] = useState<"asc" | "desc">("asc");
    const [page, setPage] = useState(0);
    const hasRows = Array.isArray(data) && data.length > 0;
    const rows = useMemo(() => (hasRows ? (data as DataRow[]) : []), [data, hasRows]);
    const allColumns = useMemo(() => (hasRows ? Object.keys(data[0]) : []), [data, hasRows]);
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
        if (!sortCol) return rows;
        return [...rows].sort((a, b) => {
            const va = a[sortCol];
            const vb = b[sortCol];
            if (typeof va === "number" && typeof vb === "number") {
                return sortDir === "asc" ? va - vb : vb - va;
            }
            const sa = String(va ?? "").toLowerCase();
            const sb = String(vb ?? "").toLowerCase();
            return sortDir === "asc" ? sa.localeCompare(sb) : sb.localeCompare(sa);
        });
    }, [rows, sortCol, sortDir]);

    if (!hasRows) {
        return (
            <div className="[padding:20px] [text-align:center] [color:var(--text-muted)]">
                No data available.
            </div>
        );
    }

    const totalPages = Math.ceil(sorted.length / pageSize);
    const paged = sorted.slice(page * pageSize, (page + 1) * pageSize);

    return (
        <div>
            {title && (
                <h4 className="[font-size:0.85rem] [font-weight:600] [color:var(--text-secondary)] [margin-bottom:12px] [text-transform:uppercase] [letter-spacing:0.04em]">
                    {title}
                </h4>
            )}
            <div className="[overflow-x:auto]">
                <table className="[width:100%] [border-collapse:collapse] [font-size:0.825rem]">
                    <thead>
                        <tr>
                            {columns.map((col) => (
                                <th
                                    key={col}
                                    onClick={() => handleSort(col)}
                                    className={`[padding:10px_12px] [border-bottom:2px_solid_var(--border-default)] [font-weight:600] [text-transform:uppercase] [font-size:0.7rem] [letter-spacing:0.05em] [white-space:nowrap] [cursor:pointer] [user-select:none] [transition:color_var(--transition-fast)] ${isNumericColumn(data, col) ? "[text-align:right]" : "[text-align:left]"} ${sortCol === col ? "[color:var(--accent-primary)]" : "[color:var(--text-muted)]"}`}
                                >
                                    <span className="[display:inline-flex] [align-items:center] [gap:4px]">
                                        {col}
                                        {sortCol === col ? (
                                            sortDir === "asc" ? <ChevronUp size={12} /> : <ChevronDown size={12} />
                                        ) : (
                                            <ChevronsUpDown size={10} className="[opacity:0.3]" />
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
                                    className={`[border-bottom:1px_solid_var(--border-subtle)] [transition:background_var(--transition-fast)] ${isOverallRow ? "[background:var(--accent-glow)]" : "[background:transparent]"}`}
                                    onMouseEnter={(e) => {
                                        if (!isOverallRow) e.currentTarget.style.background = "var(--bg-hover)";
                                    }}
                                    onMouseLeave={(e) => {
                                        e.currentTarget.style.background = isOverallRow ? "var(--accent-glow)" : "transparent";
                                    }}
                                >
                                    {columns.map((col) => {
                                        const val = row[col];
                                        const isNum = isNumericValue(val);
                                        return (
                                            <td
                                                key={col}
                                                className={`[padding:10px_12px] [white-space:nowrap] ${isNum ? "[text-align:right] [font-variant-numeric:tabular-nums]" : "[text-align:left]"} ${isOverallRow ? "[font-weight:700]" : "[font-weight:400]"} [color:${getCellColor(row as DataRow, col, val)}]`}
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

            {totalPages > 1 && (
                <div className="[display:flex] [justify-content:space-between] [align-items:center] [margin-top:12px] [font-size:0.78rem] [color:var(--text-muted)]">
                    <span>
                        Showing {page * pageSize + 1}-{Math.min((page + 1) * pageSize, sorted.length)} of {sorted.length}
                    </span>
                    <div className="[display:flex] [gap:4px]">
                        <button
                            className={`btn-ghost [padding:4px_10px] [font-size:0.75rem] ${page === 0 ? "[opacity:0.4]" : "[opacity:1]"}`}
                            onClick={() => setPage((p) => Math.max(0, p - 1))}
                            disabled={page === 0}
                        >
                            Prev
                        </button>
                        <button
                            className={`btn-ghost [padding:4px_10px] [font-size:0.75rem] ${page >= totalPages - 1 ? "[opacity:0.4]" : "[opacity:1]"}`}
                            onClick={() => setPage((p) => Math.min(totalPages - 1, p + 1))}
                            disabled={page >= totalPages - 1}
                        >
                            Next
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
}

function isNumericColumn(data: Record<string, unknown>[], col: string): boolean {
    const sample = data.slice(0, 5).map((r) => r[col]);
    return sample.some((v) => typeof v === "number");
}

function isNumericValue(val: unknown): boolean {
    return typeof val === "number";
}

function getCellColor(row: DataRow, col: string, val: unknown): string {
    const tone = row.cell_tones?.[col];
    if (tone === "elite") return "var(--tier-elite)";
    if (tone === "strong") return "var(--tier-strong)";
    if (tone === "caution") return "var(--tier-caution)";
    if (tone === "danger") return "var(--tier-danger)";
    if (tone === "muted") return "var(--text-disabled)";
    if (val === null || val === undefined) return "var(--text-disabled)";
    return "var(--text-primary)";
}

function formatCell(col: string, val: unknown): string {
    if (val === null || val === undefined) return "-";
    if (typeof val === "string" || typeof val === "number" || typeof val === "boolean") {
        return String(val);
    }
    if (Array.isArray(val)) {
        const rendered = val
            .map((item) => {
                if (item === null || item === undefined) return "-";
                if (typeof item === "object") {
                    try {
                        return JSON.stringify(item);
                    } catch {
                        return String(item);
                    }
                }
                return String(item);
            })
            .join(", ");
        return rendered.length > 140 ? `${rendered.slice(0, 137)}...` : rendered;
    }
    if (typeof val === "object") {
        try {
            const rendered = JSON.stringify(val);
            return rendered.length > 140 ? `${rendered.slice(0, 137)}...` : rendered;
        } catch {
            return "[object]";
        }
    }
    return String(val);
}
