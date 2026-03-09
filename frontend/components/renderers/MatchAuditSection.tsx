"use client";

import { useState } from "react";
import { ChevronDown, ChevronRight, ClipboardList } from "lucide-react";
import EmptyState from "@/components/common/EmptyState";
import { toMatchAuditRow } from "@/lib/types";

interface MatchAuditSectionProps {
    records: Record<string, unknown>[];
}
const COL_LABELS: Record<string, string> = {
    start_date: "Date",
    venue: "Venue",
    winner: "Winner",
    team_bat_1: "Bat 1st",
    score_inn1: "1st Inn",
    team_bat_2: "Bat 2nd",
    score_inn2: "2nd Inn",
    status: "Status",
};

export default function MatchAuditSection({ records }: MatchAuditSectionProps) {
    const [isOpen, setIsOpen] = useState(true);

    if (!records || records.length === 0) {
        return <EmptyState message="No audit data available." />;
    }

    const sortedRecords = [...records].sort((a, b) => {
        const aTs = Date.parse(String(a["start_date"] ?? ""));
        const bTs = Date.parse(String(b["start_date"] ?? ""));
        const aValid = Number.isFinite(aTs);
        const bValid = Number.isFinite(bTs);
        if (aValid && bValid) return bTs - aTs;
        if (aValid) return -1;
        if (bValid) return 1;
        return 0;
    });

    const columns = Object.keys(sortedRecords[0]).filter((c) => c in COL_LABELS);

    return (
        <div className="[margin-top:20px]">
            <button
                onClick={() => setIsOpen(!isOpen)}
                className={`[display:flex] [align-items:center] [gap:10px] [background:none] [border:none] [cursor:pointer] [padding:4px_0] [width:100%] ${isOpen ? "[margin-bottom:10px]" : "[margin-bottom:0px]"}`}
            >
                <div
                    className="[width:4px] [height:20px] [border-radius:2px] [background:var(--text-muted)]"
                />
                <ClipboardList size={14} className="[color:var(--text-secondary)]" />
                <h4
                    className="[font-size:0.8rem] [font-weight:700] [color:var(--text-secondary)] [text-transform:uppercase] [letter-spacing:0.06em] [flex:1] [text-align:left]"
                >
                    Match Audit ({records.length} matches)
                </h4>
                {isOpen ? (
                    <ChevronDown size={14} className="[color:var(--text-muted)]" />
                ) : (
                    <ChevronRight size={14} className="[color:var(--text-muted)]" />
                )}
            </button>

            {isOpen && (
                <div
                    className="[background:var(--bg-elevated)] [border-radius:var(--radius-md)] [border:1px_solid_var(--border-subtle)] [overflow-x:auto] [box-shadow:var(--shadow-card-deep)]"
                >
                    <table
                        className="[width:100%] [border-collapse:collapse] [font-size:0.8rem]"
                    >
                        <thead>
                            <tr>
                                {columns.map((col) => {
                                    const right = col === "score_inn1" || col === "score_inn2";
                                    return (
                                        <th
                                            key={col}
                                            className={`[padding:11px_14px] [border-bottom:1px_solid_var(--border-default)] [color:var(--text-muted)] [font-weight:600] [font-size:0.7rem] [letter-spacing:0.02em] [white-space:nowrap] ${right ? "[text-align:right]" : "[text-align:left]"}`}
                                        >
                                            {COL_LABELS[col] ?? col}
                                        </th>
                                    );
                                })}
                            </tr>
                        </thead>
                        <tbody>
                            {sortedRecords.map((row, ri) => (
                                <tr
                                    key={ri}
                                    className={`[transition:background_var(--transition-fast)] ${ri < sortedRecords.length - 1 ? "[border-bottom:1px_solid_var(--border-subtle)]" : "[border-bottom:none]"}`}
                                    onMouseEnter={(e) => {
                                        e.currentTarget.style.background = "var(--bg-hover)";
                                    }}
                                    onMouseLeave={(e) => {
                                        e.currentTarget.style.background = "transparent";
                                    }}
                                >
                                    {columns.map((col) => {
                                        const val = row[col];
                                        const isStatus = col === "status";
                                        const right = col === "score_inn1" || col === "score_inn2";
                                        const typedRow = toMatchAuditRow(row);
                                        const statusTone = isStatus ? resolveStatusTone(typedRow.status_tone) : "[color:var(--text-primary)]";
                                        return (
                                            <td
                                                key={col}
                                                className={`[padding:11px_14px] [font-size:0.8rem] [white-space:nowrap] ${right ? "[text-align:right] font-numeric" : "[text-align:left]"} ${statusTone}`}
                                            >
                                                {val === null || val === undefined ? "-" : String(val)}
                                            </td>
                                        );
                                    })}
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}
        </div>
    );
}

function resolveStatusTone(tone?: "elite" | "caution" | "danger" | "muted"): string {
    if (tone === "elite") return "[color:var(--tier-elite)]";
    if (tone === "caution") return "[color:var(--tier-caution)]";
    if (tone === "danger") return "[color:var(--tier-danger)]";
    return "[color:var(--text-muted)]";
}
