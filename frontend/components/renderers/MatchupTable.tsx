/**
 * MatchupTable.tsx - Batter-Grouped Card Layout
 */
"use client";
import React, { useMemo, useState } from "react";
import { ChevronDown, ChevronUp } from "lucide-react";
import EmptyState from "@/components/common/EmptyState";
import { MatchupRow, toMatchupRows, ThreatRating } from "@/lib/comparison-types";
import { MatchupCard } from "./MatchupCard";

interface MatchupTableProps {
  data: Record<string, unknown>[];
  homeXI?: string[];
  awayXI?: string[];
  homeTeamName?: string;
  awayTeamName?: string;
}

const THREAT_STRIP_COLORS: Record<ThreatRating, string> = {
  "NEW MATCHUP": "var(--text-disabled)",
  "LOW DATA":    "var(--text-disabled)",
  BUNNY:         "var(--tier-danger)",
  DOMINATED:     "var(--tier-danger)",
  WATCHFUL:      "var(--tier-caution)",
  CONTESTED:     "var(--bg-active)",
  ADVANTAGE:     "var(--tier-strong)",
  THREAT:        "var(--tier-caution)",
  DOMINANT:      "var(--tier-elite)",
};

const LEGEND_ITEMS: Array<{ label: string; color: string }> = [
  { label: "NEW MATCHUP", color: "var(--text-disabled)" },
  { label: "LOW DATA",    color: "var(--text-disabled)" },
  { label: "BUNNY",       color: "var(--tier-danger)" },
  { label: "DOMINATED",   color: "var(--tier-danger)" },
  { label: "WATCHFUL",    color: "var(--tier-caution)" },
  { label: "CONTESTED",   color: "var(--text-muted)" },
  { label: "ADVANTAGE",   color: "var(--tier-strong)" },
  { label: "THREAT",      color: "var(--tier-caution)" },
  { label: "DOMINANT",    color: "var(--tier-elite)" },
];

const LEGEND_SCALE_ITEMS = LEGEND_ITEMS.filter(
    item => item.label !== "NEW MATCHUP" && item.label !== "LOW DATA"
);

function LegendStrip() {
    return (
        <div className="[margin-bottom:12px]">
            <div className="[display:flex] [align-items:center] [gap:12px] [padding:6px_0] [border-bottom:1px_solid_var(--border-subtle)] [overflow-x:auto] [flex-wrap:nowrap] [white-space:nowrap]">
                {LEGEND_SCALE_ITEMS.map((item, i) => (
                    <React.Fragment key={item.label}>
                        {i > 0 && <span className="[color:var(--text-disabled)] [font-size:10px] [flex-shrink:0]">·</span>}
                        <div className="[display:inline-flex] [align-items:center] [gap:5px] [flex-shrink:0]">
                            <div style={{ backgroundColor: item.color }} className="[width:7px] [height:7px] [border-radius:50%] [flex-shrink:0]" />
                            <span className="[font-size:10px] [color:var(--text-secondary)] [font-weight:500] [text-transform:uppercase] [letter-spacing:0.04em]">{item.label}</span>
                        </div>
                    </React.Fragment>
                ))}
            </div>
            <div className="[font-size:0.65rem] [color:var(--text-disabled)] [padding-top:4px]">
                NEW MATCHUP = limited data&nbsp;&nbsp;·&nbsp;&nbsp;LOW DATA = &lt;20 balls
            </div>
        </div>
    );
}

const THREAT_ORDER: ThreatRating[] = ["BUNNY", "DOMINATED", "THREAT", "DOMINANT", "WATCHFUL", "ADVANTAGE", "CONTESTED", "LOW DATA", "NEW MATCHUP"];
function computeDangerSummary(rows: MatchupRow[]): Array<{ rating: ThreatRating; count: number }> {
    const counts: Partial<Record<ThreatRating, number>> = {};
    rows.forEach(row => {
        const r = (row["threat_rating"] as ThreatRating | undefined) ?? "LOW DATA";
        counts[r] = (counts[r] ?? 0) + 1;
    });
    return THREAT_ORDER.filter(r => (counts[r] ?? 0) > 0).map(r => ({ rating: r, count: counts[r]! }));
}

export default function MatchupTable({ data, homeXI, awayXI, homeTeamName, awayTeamName }: MatchupTableProps) {
    const [batterFilter, setBatterFilter] = useState("");
    const rows = useMemo(() => toMatchupRows(data || []), [data]);
    const batterGroups = useMemo(() => {
        const groups: Record<string, MatchupRow[]> = {}, order: string[] = [];
        rows.forEach((row) => { const b = String(row["Batter"] ?? row["BATTER"] ?? "Unknown"); if (!groups[b]) { groups[b] = []; order.push(b); } groups[b].push(row); });
        return order.map(b => ({ batter: b, rows: groups[b] }));
    }, [rows]);

    const homeBatterGroups = useMemo(() => {
        const xi = homeXI ? batterGroups.filter(g => homeXI.includes(g.batter)) : batterGroups;
        return batterFilter ? xi.filter(g => g.batter.toLowerCase().includes(batterFilter.toLowerCase())) : xi;
    }, [batterGroups, homeXI, batterFilter]);

    const awayBatterGroups = useMemo(() => {
        const xi = awayXI ? batterGroups.filter(g => awayXI.includes(g.batter)) : [];
        return batterFilter ? xi.filter(g => g.batter.toLowerCase().includes(batterFilter.toLowerCase())) : xi;
    }, [batterGroups, awayXI, batterFilter]);

    const [expandedGroups, setExpandedGroups] = useState<Record<string, boolean>>({});

    if (!data || data.length === 0) return <EmptyState message="No matchup data available." />;

    return (
        <div className="[display:flex] [flex-direction:column] [gap:16px]">
            <div className="[display:flex] [align-items:center] [justify-content:space-between] [margin-bottom:4px]">
                <div className="[display:flex] [align-items:center] [gap:8px]">
                    <span className="[font-size:0.95rem] [font-weight:600] [color:var(--text-primary)]">Player Matchups</span>
                    <span className="[font-size:0.72rem] [padding:2px_8px] [border-radius:9999px] [background:var(--bg-active)] [color:var(--text-muted)] [font-weight:500]">{rows.length} matchups</span>
                </div>
                <input
                    type="text"
                    placeholder="Filter batters..."
                    value={batterFilter}
                    onChange={e => setBatterFilter(e.target.value)}
                    className="context-input [max-width:180px] [height:28px] [font-size:0.82rem]"
                    aria-label="Filter batters by name"
                />
            </div>

            <LegendStrip />

            <div className="[display:grid] [grid-template-columns:1fr_1fr] [gap:24px] [align-items:start]">
                <div className="[display:flex] [flex-direction:column] [gap:12px]">
                    <div className="[font-size:0.78rem] [font-weight:600] [color:var(--text-secondary)] [text-transform:uppercase] [letter-spacing:0.04em] [padding-bottom:8px] [border-bottom:1px_solid_rgb(26,39,64)]">{homeTeamName || "Home"} Batters vs {awayTeamName || "Away"} Bowlers</div>
                    {homeBatterGroups.length > 0 ? homeBatterGroups.map(g => ( <MatchupBatterGroup key={g.batter} batter={g.batter} rows={g.rows} isExpanded={!!expandedGroups[g.batter]} onToggle={() => setExpandedGroups(p => ({ ...p, [g.batter]: !p[g.batter] }))} /> )) : <EmptyState message="No home team batter matchups." />}
                </div>
                <div className="[display:flex] [flex-direction:column] [gap:12px]">
                    <div className="[font-size:0.78rem] [font-weight:600] [color:var(--text-secondary)] [text-transform:uppercase] [letter-spacing:0.04em] [padding-bottom:8px] [border-bottom:1px_solid_rgb(26,39,64)]">{awayTeamName || "Away"} Batters vs {homeTeamName || "Home"} Bowlers</div>
                    {awayBatterGroups.length > 0 ? awayBatterGroups.map(g => ( <MatchupBatterGroup key={g.batter} batter={g.batter} rows={g.rows} isExpanded={!!expandedGroups[g.batter]} onToggle={() => setExpandedGroups(p => ({ ...p, [g.batter]: !p[g.batter] }))} /> )) : <EmptyState message="No away team batter matchups." />}
                </div>
            </div>
        </div>
    );
}

function MatchupBatterGroup({ batter, rows, isExpanded, onToggle }: { batter: string; rows: MatchupRow[]; isExpanded: boolean; onToggle: () => void; }) {
    const summary = useMemo(() => computeDangerSummary(rows), [rows]);
    return (
        <div className="[border:1px_solid_var(--border-default)] [border-radius:var(--radius-md)] [overflow:hidden] [background:var(--bg-deepest)]">
            <button
                onClick={onToggle}
                aria-label={`${isExpanded ? "Collapse" : "Expand"} matchups for ${batter}`}
                className="[width:100%] [padding:10px_14px] [display:flex] [flex-direction:column] [align-items:flex-start] [gap:4px] [background:var(--bg-elevated)] [border-left:3px_solid_var(--accent-primary)] [border-bottom:1px_solid_var(--border-default)] [transition:background_var(--transition-fast)] hover:[background:var(--bg-hover)]"
            >
                <div className="[width:100%] [display:flex] [align-items:center] [justify-content:space-between]">
                    <div className="[display:flex] [align-items:center] [gap:8px]">
                        {isExpanded ? <ChevronUp size={16} className="[color:var(--text-muted)]" /> : <ChevronDown size={16} className="[color:var(--text-muted)]" />}
                        <span className="[font-weight:700] [color:var(--text-primary)] [font-size:0.92rem]">{batter}</span>
                        <span className="[font-size:0.75rem] [color:var(--text-muted)]"><span className="[margin:0_4px]">·</span>{rows.length} matchups</span>
                    </div>
                </div>
                {!isExpanded && (
                    <div className="[display:flex] [align-items:center] [gap:8px] [flex-wrap:wrap] [margin-left:24px]">
                        {summary.map((item, i) => ( <React.Fragment key={item.rating}>{i > 0 && <span className="[color:rgb(71,85,105)] [font-size:10px]">·</span>}<span style={{ color: THREAT_STRIP_COLORS[item.rating] }} className="[font-size:11px] [font-weight:600] [text-transform:uppercase]">{item.count} {item.rating}</span></React.Fragment> ))}
                    </div>
                )}
            </button>
            {isExpanded && <div className="[padding:12px] [display:flex] [flex-direction:column] [gap:12px]">{rows.map((row, i) => ( <MatchupCard key={i} row={row} /> ))}</div>}
        </div>
    );
}
