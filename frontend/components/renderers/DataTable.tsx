/**
 * DataTable.tsx - Sortable, Paginated Data Table
 *
 * Used by: venue_phases, tactical_matrix, and generic "table" outputs.
 */
"use client";

import { useState, useMemo } from "react";
import { ChevronUp, ChevronDown, ChevronsUpDown } from "lucide-react";
import { type DataRow, toDataRows } from "@/lib/comparison-types";

interface DataTableProps {
    data: Record<string, unknown>[];
    pageSize?: number;
    title?: string;
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
    const rows = useMemo(() => (hasRows ? toDataRows(data) : []), [data, hasRows]);
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

    function handleHeaderKeyDown(
        event: React.KeyboardEvent<HTMLTableCellElement>,
        col: string
    ): void {
        if (event.key !== "Enter" && event.key !== " ") return;
        event.preventDefault();
        handleSort(col);
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
        return <p className="data-empty">No table data available.</p>;
    }

    const totalPages = Math.ceil(sorted.length / pageSize);
    const paged = sorted.slice(page * pageSize, (page + 1) * pageSize);

    return (
        <div>
            {title && <h4 className="data-table-title">{title}</h4>}
            <div className="data-table-wrapper">
                <table className="data-table">
                    <thead>
                        <tr>
                            {columns.map((col) => {
                                const isNumCol = isNumericColumn(data, col);
                                const thClass = [
                                    "data-header",
                                    isNumCol ? "data-header-right" : "data-header-left",
                                    sortCol === col ? "data-header-active" : "",
                                ].join(" ").trim();
                                return (
                                    <th
                                        key={col}
                                        onClick={() => handleSort(col)}
                                        onKeyDown={(e) => handleHeaderKeyDown(e, col)}
                                        role="button"
                                        tabIndex={0}
                                        aria-sort={
                                            sortCol === col
                                                ? sortDir === "asc"
                                                    ? "ascending"
                                                    : "descending"
                                                : "none"
                                        }
                                        className={thClass}
                                    >
                                        <span className="data-header-inner">
                                            {col}
                                            {sortCol === col ? (
                                                sortDir === "asc"
                                                    ? <ChevronUp size={12} />
                                                    : <ChevronDown size={12} />
                                            ) : (
                                                <ChevronsUpDown size={10} />
                                            )}
                                        </span>
                                    </th>
                                );
                            })}
                        </tr>
                    </thead>
                    <tbody>
                        {paged.map((row, i) => {
                            const isOverallRow = String(row["Opponent"] ?? "").includes("OVERALL");
                                const trClass = [
                                    "data-row",
                                    "data-row-zebra",
                                    isOverallRow ? "data-row-active" : "",
                                ].join(" ").trim();
                            return (
                                <tr
                                    key={i}
                                    className={trClass}
                                >
                                    {columns.map((col) => {
                                        const val = row[col];
                                        const isNum = isNumericValue(val);
                                        const tdClass = [
                                            isNum ? "data-cell-numeric" : "data-cell",
                                            isOverallRow ? "font-bold" : "",
                                        ].join(" ").trim();
                                        const cellStyle = { color: getCellColor(row, col, val) };
                                        return (
                                            <td
                                                key={col}
                                                className={tdClass}
                                                style={cellStyle}
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
                <div className="data-table-footer">
                    <span>
                        Showing {page * pageSize + 1}–{Math.min((page + 1) * pageSize, sorted.length)} of {sorted.length}
                    </span>
                    <div className="data-table-pagination">
                        <button
                            className="btn-ghost"
                            onClick={() => setPage((p) => Math.max(0, p - 1))}
                            disabled={page === 0}
                            aria-label="Previous page"
                        >
                            Prev
                        </button>
                        <button
                            className="btn-ghost"
                            onClick={() => setPage((p) => Math.min(totalPages - 1, p + 1))}
                            disabled={page >= totalPages - 1}
                            aria-label="Next page"
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
    if (tone === "elite")   return "var(--tier-elite)";
    if (tone === "strong")  return "var(--tier-strong)";
    if (tone === "caution") return "var(--tier-caution)";
    if (tone === "danger")  return "var(--tier-danger)";
    if (tone === "muted")   return "var(--text-disabled)";
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
                    try { return JSON.stringify(item); } catch { return String(item); }
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
