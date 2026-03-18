/**
 * MatchupTable.tsx - Batter-Grouped Card Layout
 *
 * Used by: matchups (output_type: "matchup_table")
 */
"use client";

import React, { useMemo, useState } from "react";
import { Crosshair, AlertTriangle, ChevronDown, ChevronUp } from "lucide-react";
import EmptyState from "@/components/common/EmptyState";
import { MatchupRow, toMatchupRows, ToneToken } from "@/lib/comparison-types";

interface MatchupTableProps {
    data: Record<string, unknown>[];
}

/** @schema-exempt — UI-only grouping structure */
interface BatterGroup {
    batter: string;
    rows: MatchupRow[];
}

export default function MatchupTable({ data }: MatchupTableProps) {
    if (!data || data.length === 0) {
        return <EmptyState message="No matchup data available." />;
    }

    const rows = useMemo(() => toMatchupRows(data), [data]);

    const batterGroups = useMemo(() => {
        const groups: Record<string, MatchupRow[]> = {};
        const order: string[] = [];

        rows.forEach((row) => {
            const batter = String(row["BATTER"] ?? row["Batter"] ?? "Unknown");
            if (!groups[batter]) {
                groups[batter] = [];
                order.push(batter);
            }
            groups[batter].push(row);
        });

        return order.map(batter => ({
            batter,
            rows: groups[batter]
        }));
    }, [rows]);

    const [expandedGroups, setExpandedGroups] = useState<Record<string, boolean>>(() => {
        const initial: Record<string, boolean> = {};
        if (batterGroups.length > 0) {
            initial[batterGroups[0].batter] = true;
        }
        return initial;
    });

    const toggleGroup = (batter: string) => {
        setExpandedGroups((prev) => ({
            ...prev,
            [batter]: !prev[batter],
        }));
    };

    return (
        <div className="[display:flex] [flex-direction:column] [gap:16px]">
            <div className="[display:flex] [align-items:center] [gap:8px] [margin-bottom:4px]">
                <Crosshair size={16} className="[color:var(--accent-primary)]" />
                <span className="[font-size:0.8rem] [font-weight:600] [color:var(--text-secondary)] [text-transform:uppercase] [letter-spacing:0.04em]">
                    Player Matchups ({rows.length} records)
                </span>
            </div>

            <div className="[display:flex] [flex-direction:column] [gap:12px]">
                {batterGroups.map((group) => (
                    <MatchupBatterGroup
                        key={group.batter}
                        batter={group.batter}
                        rows={group.rows}
                        isExpanded={!!expandedGroups[group.batter]}
                        onToggle={() => toggleGroup(group.batter)}
                    />
                ))}
            </div>
        </div>
    );
}

function MatchupBatterGroup({
    batter,
    rows,
    isExpanded,
    onToggle
}: {
    batter: string;
    rows: MatchupRow[];
    isExpanded: boolean;
    onToggle: () => void;
}) {
    return (
        <div className="[border:1px_solid_var(--border-subtle)] [border-radius:8px] [overflow:hidden] [background:var(--bg-surface)]">
            <button
                onClick={onToggle}
                className="[width:100%] [padding:12px_16px] [display:flex] [align-items:center] [justify-content:space-between] [background:var(--bg-elevated)] [transition:background_var(--transition-fast)] hover:[background:var(--bg-hover)]"
            >
                <div className="[display:flex] [align-items:center] [gap:8px]">
                    {isExpanded ? <ChevronUp size={16} className="[color:var(--text-muted)]" /> : <ChevronDown size={16} className="[color:var(--text-muted)]" />}
                    <span className="[font-weight:600] [color:var(--text-primary)] [font-size:0.9rem]">
                        {batter}
                    </span>
                    <span className="[font-size:0.75rem] [color:var(--text-muted)] [font-weight:400]">
                        [{rows.length} matchups]
                    </span>
                </div>
            </button>

            {isExpanded && (
                <div className="[padding:12px] [display:flex] [flex-direction:column] [gap:12px]">
                    {rows.map((row, i) => (
                        <MatchupCard key={i} row={row} />
                    ))}
                </div>
            )}
        </div>
    );
}

function MatchupCard({ row }: { row: MatchupRow }) {
    const batter = String(row["BATTER"] ?? row["Batter"] ?? "Unknown");
    const bowler = String(row["BOWLER"] ?? row["Bowler"] ?? "Unknown");
    const style = String(row["STYLE"] ?? row["Style"] ?? "");
    const isBunny = row.highlight_flags?.bunny_alert === true;
    const srTone = row.cell_tones?.["SR"];

    const stats = [
        { label: "RUNS", value: row["RUNS"] },
        { label: "BALLS", value: row["BALLS"] },
        { label: "OUTS", value: row["OUTS"] },
        { label: "AVG", value: row["AVG"] },
        { label: "SR", value: row["SR"] },
    ];

    const { width, colorClass } = getAdvantageProps(srTone);

    return (
        <div className="[padding:12px] [border:1px_solid_var(--border-subtle)] [border-radius:6px] [background:var(--bg-base)] [display:flex] [flex-direction:column] [gap:10px] [transition:all_var(--transition-fast)] hover:[border-color:var(--border-default)]">
            <div className="[display:flex] [align-items:center] [justify-content:space-between] [gap:8px]">
                <div className="[display:flex] [align-items:center] [gap:8px] [flex-wrap:wrap]">
                    <span className="[font-size:0.85rem] [font-weight:600] [color:var(--text-primary)]">
                        {batter} <span className="[color:var(--text-muted)] [font-weight:400] [margin:0_2px]">vs</span> {bowler}
                    </span>
                    {style && <StyleTag style={style} />}
                </div>
                {isBunny && (
                    <div className="[display:flex] [align-items:center] [gap:4px] [padding:2px_8px] [border-radius:4px] [background:var(--bg-elevated)] [border:1px_solid_var(--tier-caution)] [color:var(--tier-caution)] [font-size:0.65rem] [font-weight:700] [text-transform:uppercase] [letter-spacing:0.05em]">
                        <AlertTriangle size={10} />
                        BUNNY
                    </div>
                )}
            </div>

            <div className="[display:grid] [grid-template-columns:repeat(5,1fr)] [gap:4px]">
                {stats.map((s) => (
                    <div key={s.label} className="[display:flex] [flex-direction:column] [gap:2px]">
                        <span className="[font-size:0.6rem] [font-weight:600] [color:var(--text-muted)] [text-transform:uppercase]">
                            {s.label}
                        </span>
                        <span className="[font-size:0.85rem] [font-weight:500] [color:var(--text-primary)] font-numeric">
                            {s.value === null || s.value === undefined ? "-" : String(s.value)}
                        </span>
                    </div>
                ))}
            </div>

            <div className="[display:flex] [flex-direction:column] [gap:4px]">
                <div className="[width:100%] [height:4px] [background:var(--border-subtle)] [border-radius:2px] [overflow:hidden]">
                    <div
                        style={{ width }}
                        className={`[height:100%] [transition:width_var(--transition-normal)] ${colorClass}`}
                    />
                </div>
                <span className="[font-size:0.6rem] [font-weight:600] [color:var(--text-muted)] [text-transform:uppercase] [letter-spacing:0.02em]">
                    Advantage
                </span>
            </div>
        </div>
    );
}

function StyleTag({ style }: { style: string }) {
    const dotClass = getStyleDotClass(style);

    return (
        <div className="[display:inline-flex] [align-items:center] [gap:6px] [padding:2px_8px] [background:var(--bg-elevated)] [border-radius:12px] [border:1px_solid_var(--border-subtle)] [font-size:0.65rem] [font-weight:600] [color:var(--text-secondary)] [text-transform:uppercase] [letter-spacing:0.03em]">
            <div className={`[width:6px] [height:6px] [border-radius:50%] ${dotClass}`} />
            {style}
        </div>
    );
}

function getStyleDotClass(style: string) {
    if (style.includes("Leg Spin")) return "[background:var(--tier-caution)]";
    if (style.includes("Off Spin")) return "[background:var(--accent-primary)]";
    if (style.includes("Fast") || style.includes("Med")) return "[background:var(--tier-danger)]";
    return "[background:var(--border-default)]";
}

function getAdvantageProps(tone: ToneToken | undefined) {
    if (tone === "elite" || tone === "strong") {
        return {
            width: tone === "elite" ? "90%" : "70%",
            colorClass: "[background:var(--accent-primary)]"
        };
    }
    if (tone === "danger" || tone === "caution") {
        return {
            width: tone === "caution" ? "40%" : "20%",
            colorClass: "[background:var(--tier-danger)]"
        };
    }
    return { width: "50%", colorClass: "[background:var(--border-default)]" };
}
