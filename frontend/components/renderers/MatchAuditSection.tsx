"use client";

import { useState, type CSSProperties } from "react";
import { ChevronDown, ChevronRight, ClipboardList } from "lucide-react";
import EmptyState from "@/components/common/EmptyState";
import { toMatchAuditRow } from "@/lib/types";

interface MatchAuditSectionProps {
    records: Record<string, unknown>[];
}

const DISPLAY_COLUMNS = ["start_date", "venue", "winner", "team_bat_1", "team_bat_2", "status"] as const;

const COL_LABELS: Record<(typeof DISPLAY_COLUMNS)[number], string> = {
    start_date: "Date",
    venue: "Venue",
    winner: "Winner",
    team_bat_1: "Bat 1st",
    team_bat_2: "Bat 2nd",
    status: "Status",
};
const TEAM_NAME_COLUMNS = new Set(["winner", "team_bat_1", "team_bat_2"]);
const MERGED_INNINGS_COLUMNS = new Set(["team_bat_1", "team_bat_2"]);

function toTeamColorVarName(teamName: string): string {
    return `--venue-team-${teamName.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/(^-|-$)/g, "")}-color`;
}

function getColumnWidthClass(column: string): string {
    if (column === "start_date") return "[width:12%] min-w-[8rem]";
    if (column === "venue") return "[width:24%] min-w-[15rem]";
    if (column === "winner") return "[width:14%] min-w-[10rem]";
    if (column === "team_bat_1" || column === "team_bat_2") return "[width:18%] min-w-[12rem]";
    if (column === "status") return "[width:14%] min-w-[9rem]";
    return "min-w-[7rem]";
}

function resolveTeamNameStyle(value: unknown): CSSProperties | undefined {
    if (typeof value !== "string" || value.trim() === "") {
        return undefined;
    }

    return { color: `var(${toTeamColorVarName(value)})` };
}

function renderMergedInningsCell(teamValue: unknown, scoreValue: unknown) {
    const teamName = typeof teamValue === "string" ? teamValue.trim() : "";
    const inningsScore = typeof scoreValue === "string" || typeof scoreValue === "number"
        ? String(scoreValue).trim()
        : "";

    if (teamName === "" && inningsScore === "") {
        return "-";
    }
    if (teamName === "") {
        return inningsScore;
    }
    if (inningsScore === "") {
        return <span style={resolveTeamNameStyle(teamName)}>{teamName}</span>;
    }

    return (
        <>
            <span style={resolveTeamNameStyle(teamName)}>{teamName}</span>
            <span className="[color:var(--text-primary)]"> {inningsScore}</span>
        </>
    );
}

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

    const columns = DISPLAY_COLUMNS.filter((column) => sortedRecords.some((record) => column in record));

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
                        className="[width:100%] [min-width:68rem] [table-layout:fixed] [border-collapse:separate] [border-spacing:0] [font-size:0.8rem]"
                    >
                        <thead>
                            <tr>
                                {columns.map((col, index) => {
                                    const withDivider = index > 0;
                                    return (
                                        <th
                                            key={col}
                                            className={`${getColumnWidthClass(col)} [padding:14px_16px] [background:var(--bg-active)] [border-bottom:1px_solid_var(--border-strong)] [color:var(--text-secondary)] [font-weight:800] [font-size:0.75rem] [letter-spacing:0.08em] [text-transform:uppercase] [white-space:nowrap] [text-align:left] ${withDivider ? "[border-left:1px_solid_var(--border-default)]" : ""}`}
                                        >
                                            {COL_LABELS[col] ?? col}
                                        </th>
                                    );
                                })}
                            </tr>
                        </thead>
                        <tbody>
                            {sortedRecords.map((row, ri) => {
                                const typedRow = toMatchAuditRow(row);

                                return (
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
                                        {columns.map((col, index) => {
                                            const val = row[col];
                                            const isStatus = col === "status";
                                            const isTeamName = TEAM_NAME_COLUMNS.has(col);
                                            const isMergedInnings = MERGED_INNINGS_COLUMNS.has(col);
                                            const withDivider = index > 0;
                                            const statusBadgeClass = isStatus ? resolveStatusTone(typedRow.status_tone) : "";
                                            const teamNameStyle = isTeamName ? resolveTeamNameStyle(val) : undefined;
                                            const mergedScore = col === "team_bat_1" ? row["score_inn1"] : row["score_inn2"];

                                            return (
                                                <td
                                                    key={col}
                                                    className={`${getColumnWidthClass(col)} [padding:12px_16px] [font-size:0.85rem] align-top ${isMergedInnings || col === "venue" ? "[white-space:normal] break-words" : "[white-space:nowrap]"} [text-align:left] ${withDivider ? "[border-left:1px_solid_var(--border-subtle)]" : ""}`}
                                                >
                                                    {isStatus ? (
                                                        <span className={`badge ${statusBadgeClass} text-[10px] px-2.5 py-0.5 rounded-full uppercase font-black tracking-wider`}>
                                                            {val === null || val === undefined ? "-" : String(val)}
                                                        </span>
                                                    ) : isMergedInnings ? (
                                                        <span className="font-medium leading-[1.35]">
                                                            {renderMergedInningsCell(val, mergedScore)}
                                                        </span>
                                                    ) : (
                                                        <span className={isTeamName ? "font-semibold" : "[color:var(--text-primary)]"} style={teamNameStyle}>
                                                            {val === null || val === undefined ? "-" : String(val)}
                                                        </span>
                                                    )}
                                                </td>
                                            );
                                        })}
                                    </tr>
                                );
                            })}
                        </tbody>
                    </table>
                </div>
            )}
        </div>
    );
}

function resolveStatusTone(tone?: "elite" | "caution" | "danger" | "muted"): string {
    if (tone === "elite") return "badge-elite";
    if (tone === "caution") return "badge-caution";
    if (tone === "danger") return "badge-danger";
    return "[background:var(--bg-active)] [color:var(--text-muted)] [border-color:var(--border-subtle)]";
}
