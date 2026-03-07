"use client";

import { useMemo, useState } from "react";
import { ChevronDown, ChevronUp, ChevronsUpDown, Trophy } from "lucide-react";
import { useRouter } from "next/navigation";
import EmptyState from "@/components/common/EmptyState";
import { useAppContext } from "@/lib/context";
import { MatrixRow, toMatrixRows } from "@/lib/types";

interface MatrixTableProps {
    data: Record<string, unknown>[];
}

const HIDDEN_COLS = new Set(["MATCH_IDS", "match_ids", "cell_tones", "highlight_flags", "derived_badges"]);

export default function MatrixTable({ data }: MatrixTableProps) {
    const [sortCol, setSortCol] = useState<string | null>(null);
    const [sortDir, setSortDir] = useState<"asc" | "desc">("desc");
    const { activeFormat } = useAppContext();
    const router = useRouter();
    const hasRows = Array.isArray(data) && data.length > 0;
    const rows = useMemo(() => (hasRows ? toMatrixRows(data) : []), [data, hasRows]);

    const overallRow = useMemo(
        () => rows.find((r) => String(r["Opponent"] ?? "").includes("OVERALL")),
        [rows]
    );
    const regularRows = useMemo(
        () => rows.filter((r) => !String(r["Opponent"] ?? "").includes("OVERALL")),
        [rows]
    );
    const allColumns = useMemo(
        () => (rows.length > 0 ? Object.keys(rows[0]).filter((c) => !HIDDEN_COLS.has(c)) : []),
        [rows]
    );

    function handleSort(col: string) {
        if (sortCol === col) {
            setSortDir((d) => (d === "asc" ? "desc" : "asc"));
        } else {
            setSortCol(col);
            setSortDir("desc");
        }
    }

    function navigateToOpponent(opponent: string): void {
        if (!activeFormat || !opponent) {
            return;
        }

        const target = `/${encodeURIComponent(activeFormat)}/rivalry/global_h2h?team_b=${encodeURIComponent(opponent)}`;
        router.push(target);
    }

    function handleActivationKey(
        event: React.KeyboardEvent<HTMLElement>,
        action: () => void
    ): void {
        if (event.key !== "Enter" && event.key !== " ") {
            return;
        }

        event.preventDefault();
        action();
    }

    const sortedRows = useMemo(() => {
        if (!sortCol) return regularRows;
        return [...regularRows].sort((a, b) => {
            const va = a[sortCol];
            const vb = b[sortCol];
            if (typeof va === "number" && typeof vb === "number") {
                return sortDir === "asc" ? va - vb : vb - va;
            }
            return sortDir === "asc"
                ? String(va ?? "").localeCompare(String(vb ?? ""))
                : String(vb ?? "").localeCompare(String(va ?? ""));
        });
    }, [regularRows, sortCol, sortDir]);

    if (!hasRows) {
        return <EmptyState message="No matrix data available." />;
    }

    return (
        <div className="[overflow-x:auto]">
            {overallRow && (
                <div className="glass-card [padding:16px_20px] [display:flex] [align-items:center] [gap:16px] [flex-wrap:wrap] [border:1px_solid_var(--border-accent)] [margin-bottom:12px]">
                    <div className="[width:36px] [height:36px] [border-radius:var(--radius-md)] [background:var(--accent-glow)] [display:flex] [align-items:center] [justify-content:center]">
                        <Trophy size={18} className="[color:var(--accent-primary)]" />
                    </div>
                    <div className="[flex:1]">
                        <div className="[font-size:0.7rem] [text-transform:uppercase] [letter-spacing:0.06em] [color:var(--text-disabled)] [font-weight:600]">
                            Overall Record
                        </div>
                        <div className="[font-size:1.1rem] [font-weight:800] [color:var(--text-primary)]">
                            {String(overallRow["Won"] ?? 0)}W - {String(overallRow["Lost"] ?? 0)}L
                            {overallRow["Tie/NR"] ? ` - ${overallRow["Tie/NR"]}NR` : ""}
                        </div>
                    </div>
                    {allColumns
                        .filter((c) => c !== "Opponent" && c !== "Won" && c !== "Lost" && c !== "Tie/NR")
                        .slice(0, 4)
                        .map((col) => (
                            <div key={col} className="[text-align:center] [min-width:60px]">
                                <div className="[font-size:0.65rem] [text-transform:uppercase] [color:var(--text-disabled)] [font-weight:600]">{col}</div>
                                <div className={`[font-size:0.95rem] [font-weight:700] ${getCellToneClass(overallRow, col, overallRow[col])}`}>
                                    {String(overallRow[col] ?? "-")}
                                </div>
                            </div>
                        ))}
                </div>
            )}

            <table className="[width:100%] [border-collapse:collapse] [font-size:0.825rem]">
                <thead>
                    <tr>
                        {allColumns.map((col) => (
                            <th
                                key={col}
                                onClick={() => handleSort(col)}
                                onKeyDown={(event) => handleActivationKey(event, () => handleSort(col))}
                                role="button"
                                tabIndex={0}
                                aria-sort={
                                    sortCol === col
                                        ? sortDir === "asc"
                                            ? "ascending"
                                            : "descending"
                                        : "none"
                                }
                                className={`[padding:10px_12px] [border-bottom:2px_solid_var(--border-default)] [font-weight:600] [text-transform:uppercase] [font-size:0.7rem] [letter-spacing:0.05em] [white-space:nowrap] [cursor:pointer] [user-select:none] ${col === "Opponent" || col === "form_guide" ? "[text-align:left]" : "[text-align:right]"} ${sortCol === col ? "[color:var(--accent-primary)]" : "[color:var(--text-muted)]"}`}
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
                    {sortedRows.map((row, i) => (
                        <tr key={i} className="[border-bottom:1px_solid_var(--border-subtle)] hover:[background:var(--bg-hover)] [transition:background_var(--transition-fast)]">
                            {allColumns.map((col) => {
                                const val = row[col];
                                const isNum = col !== "Opponent" && col !== "form_guide";
                                const isOpponent = col === "Opponent";
                                return (
                                    <td
                                        key={col}
                                        className={`[padding:10px_12px] [white-space:nowrap] ${col === "Opponent" || col === "form_guide" ? "[text-align:left]" : "[text-align:right]"} ${isNum ? "font-numeric" : ""} ${isOpponent ? "[font-weight:600] [cursor:pointer]" : "[font-weight:400] [cursor:default]"} ${getCellToneClass(row, col, val)}`}
                                        onClick={() => {
                                            if (isOpponent) {
                                                navigateToOpponent(String(val ?? ""));
                                            }
                                        }}
                                        onKeyDown={(event) => {
                                            if (isOpponent) {
                                                handleActivationKey(event, () => navigateToOpponent(String(val ?? "")));
                                            }
                                        }}
                                        role={isOpponent ? "button" : undefined}
                                        tabIndex={isOpponent ? 0 : undefined}
                                        aria-label={isOpponent ? `Open rivalry view for ${String(val ?? "")}` : undefined}
                                    >
                                        {col === "form_guide" ? <FormGuide value={String(val ?? "")} /> : formatVal(val)}
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

function FormGuide({ value }: { value: string }) {
    const chars = value.split("").filter((c) => c.trim() !== "");
    return (
        <span className="[display:inline-flex] [gap:3px] [font-size:0.9rem]">
            {chars.map((c, i) => (
                <span key={i} className="[font-size:0.85rem]">
                    {c}
                </span>
            ))}
        </span>
    );
}

function formatVal(val: unknown): string {
    if (val === null || val === undefined) return "-";
    return String(val);
}

function getCellToneClass(row: MatrixRow, col: string, val: unknown): string {
    const tone = row.cell_tones?.[col];
    if (tone === "elite") return "[color:var(--tier-elite)]";
    if (tone === "strong") return "[color:var(--tier-strong)]";
    if (tone === "caution") return "[color:var(--tier-caution)]";
    if (tone === "danger") return "[color:var(--tier-danger)]";
    if (tone === "muted") return "[color:var(--text-disabled)]";
    if (val === null || val === undefined) return "[color:var(--text-disabled)]";
    return "[color:var(--text-primary)]";
}
