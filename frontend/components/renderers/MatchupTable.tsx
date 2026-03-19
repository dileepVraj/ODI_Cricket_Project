/**
 * MatchupTable.tsx - Batter-Grouped Card Layout
 */
"use client";
import React, { useMemo, useState } from "react";
import { Crosshair, AlertTriangle, ChevronDown, ChevronUp } from "lucide-react";
import EmptyState from "@/components/common/EmptyState";
import { MatchupRow, toMatchupRows, ToneToken } from "@/lib/comparison-types";
interface MatchupTableProps { data: Record<string, unknown>[]; homeXI?: string[]; awayXI?: string[]; homeTeamName?: string; awayTeamName?: string; }
type ThreatRating = "BUNNY" | "THREAT" | "CAUTION" | "SAFE" | "LOW DATA" | "CONTESTED";
function computeThreatRating(row: MatchupRow): ThreatRating {
    const balls = typeof row["Balls"] === "number" ? row["Balls"] : parseFloat(String(row["Balls"] ?? "0"));
    const avg = typeof row["Avg"] === "number" ? row["Avg"] : parseFloat(String(row["Avg"] ?? "0"));
    const sr = typeof row["SR"] === "number" ? row["SR"] : parseFloat(String(row["SR"] ?? "0"));
    const outs = typeof row["Outs"] === "number" ? row["Outs"] : parseFloat(String(row["Outs"] ?? "0"));
    if (Number.isNaN(balls) || balls < 10) return "LOW DATA";
    const dismissalPct = balls > 0 ? (outs / balls) * 100 : 0;
    if (outs >= 2 && (avg < 20 || dismissalPct > 35)) return "BUNNY";
    if (sr > 105 && avg > 28 && balls >= 15) return "THREAT";
    if (sr > 95 || avg > 25) return "CAUTION";
    if (outs >= 1 && sr < 80) return "SAFE";
    return "CONTESTED";
}
const LEGEND_ITEMS: Array<{ label: string; color: string }> = [ { label: "BUNNY", color: "var(--tier-danger)" }, { label: "THREAT", color: "rgb(249, 115, 22)" }, { label: "CAUTION", color: "var(--tier-caution)" }, { label: "SAFE", color: "var(--tier-elite)" }, { label: "LOW DATA", color: "rgb(107, 114, 128)" }, { label: "CONTESTED", color: "var(--text-muted)" } ];
function LegendStrip() {
    return (
        <div className="[display:flex] [align-items:center] [gap:16px] [padding:8px_0] [border-bottom:1px_solid_rgb(26,39,64)] [margin-bottom:16px] [flex-wrap:wrap]">
            {LEGEND_ITEMS.map((item, i) => (
                <React.Fragment key={item.label}>
                    {i > 0 && <span className="[color:rgb(71,85,105)] [font-size:10px]">·</span>}
                    <div className="[display:flex] [align-items:center] [gap:6px]">
                        <div style={{ backgroundColor: item.color, width: "8px" }} className="[width:8px] [height:8px] [border-radius:50%] [flex-shrink:0]" />
                        <span className="[font-size:11px] [color:rgb(100,116,139)] [font-weight:500] [text-transform:uppercase] [letter-spacing:0.04em]">{item.label}</span>
                    </div>
                </React.Fragment>
            ))}
        </div>
    );
}
const THREAT_COLORS: Record<ThreatRating, string> = { BUNNY: "var(--tier-danger)", THREAT: "rgb(249, 115, 22)", CAUTION: "var(--tier-caution)", SAFE: "var(--tier-elite)", "LOW DATA": "rgb(107, 114, 128)", CONTESTED: "var(--text-muted)" };
function computeDangerSummary(rows: MatchupRow[]): Array<{ rating: ThreatRating; count: number }> {
    const counts: Partial<Record<ThreatRating, number>> = {};
    rows.forEach(row => { const r = computeThreatRating(row); counts[r] = (counts[r] ?? 0) + 1; });
    const ORDER: ThreatRating[] = ["BUNNY", "THREAT", "CAUTION", "SAFE", "LOW DATA", "CONTESTED"];
    return ORDER.filter(r => (counts[r] ?? 0) > 0).map(r => ({ rating: r, count: counts[r]! }));
}
export default function MatchupTable({ data, homeXI, awayXI, homeTeamName, awayTeamName }: MatchupTableProps) {
    const rows = useMemo(() => toMatchupRows(data || []), [data]);
    const batterGroups = useMemo(() => {
        const groups: Record<string, MatchupRow[]> = {}, order: string[] = [];
        rows.forEach((row) => { const b = String(row["Batter"] ?? row["BATTER"] ?? "Unknown"); if (!groups[b]) { groups[b] = []; order.push(b); } groups[b].push(row); });
        return order.map(b => ({ batter: b, rows: groups[b] }));
    }, [rows]);
    const homeBatterGroups = useMemo(() => batterGroups.filter(g => homeXI ? homeXI.includes(g.batter) : true), [batterGroups, homeXI]);
    const awayBatterGroups = useMemo(() => batterGroups.filter(g => awayXI ? awayXI.includes(g.batter) : false), [batterGroups, awayXI]);
    const [expandedGroups, setExpandedGroups] = useState<Record<string, boolean>>(() => {
        const initial: Record<string, boolean> = {};
        if (batterGroups.length > 0) initial[batterGroups[0].batter] = true;
        return initial;
    });
    if (!data || data.length === 0) return <EmptyState message="No matchup data available." />;
    return (
        <div className="[display:flex] [flex-direction:column] [gap:16px]">
            <div className="[display:flex] [align-items:center] [gap:8px] [margin-bottom:4px]">
                <Crosshair size={16} className="[color:var(--accent-primary)]" />
                <span className="[font-size:0.8rem] [font-weight:600] [color:var(--text-secondary)] [text-transform:uppercase] [letter-spacing:0.04em]">Player Matchups ({rows.length} records)</span>
            </div>
            <LegendStrip />
            <div className="[display:grid] [grid-template-columns:1fr_1fr] [gap:24px] [align-items:start]">
                <div className="[display:flex] [flex-direction:column] [gap:12px]">
                    <div className="[font-size:0.75rem] [font-weight:700] [color:var(--text-secondary)] [text-transform:uppercase] [letter-spacing:0.06em] [padding-bottom:8px] [border-bottom:1px_solid_rgb(26,39,64)]">{homeTeamName || "Home"} Batters vs {awayTeamName || "Away"} Bowlers</div>
                    {homeBatterGroups.length > 0 ? homeBatterGroups.map(g => ( <MatchupBatterGroup key={g.batter} batter={g.batter} rows={g.rows} isExpanded={!!expandedGroups[g.batter]} onToggle={() => setExpandedGroups(p => ({ ...p, [g.batter]: !p[g.batter] }))} /> )) : <EmptyState message="No home team batter matchups." />}
                </div>
                <div className="[display:flex] [flex-direction:column] [gap:12px]">
                    <div className="[font-size:0.75rem] [font-weight:700] [color:var(--text-secondary)] [text-transform:uppercase] [letter-spacing:0.06em] [padding-bottom:8px] [border-bottom:1px_solid_rgb(26,39,64)]">{awayTeamName || "Away"} Batters vs {homeTeamName || "Home"} Bowlers</div>
                    {awayBatterGroups.length > 0 ? awayBatterGroups.map(g => ( <MatchupBatterGroup key={g.batter} batter={g.batter} rows={g.rows} isExpanded={!!expandedGroups[g.batter]} onToggle={() => setExpandedGroups(p => ({ ...p, [g.batter]: !p[g.batter] }))} /> )) : <EmptyState message="No away team batter matchups." />}
                </div>
            </div>
        </div>
    );
}
function MatchupBatterGroup({ batter, rows, isExpanded, onToggle }: { batter: string; rows: MatchupRow[]; isExpanded: boolean; onToggle: () => void; }) {
    const summary = useMemo(() => computeDangerSummary(rows), [rows]);
    const borderLeft = isExpanded ? "[border-left:3px_solid_rgb(0,200,170)]" : "[border-left:3px_solid_transparent]";
    return (
        <div className="[border:1px_solid_rgb(48,54,61)] [border-radius:8px] [overflow:hidden] [background:rgb(13,17,23)]">
            <button onClick={onToggle} aria-label={`${isExpanded ? "Collapse" : "Expand"} matchups for ${batter}`} className={`[width:100%] [padding:14px_16px] [display:flex] [flex-direction:column] [align-items:flex-start] [gap:4px] [background:rgb(28,33,40)] [transition:all_var(--transition-fast)] hover:[background:var(--bg-hover)] ${borderLeft}`}>
                <div className="[width:100%] [display:flex] [align-items:center] [justify-content:space-between]">
                    <div className="[display:flex] [align-items:center] [gap:8px]">
                        {isExpanded ? <ChevronUp size={16} className="[color:rgb(139,148,158)]" /> : <ChevronDown size={16} className="[color:rgb(139,148,158)]" />}
                        <span className="[font-weight:700] [color:rgb(240,246,252)] [font-size:0.95rem]">{batter}</span>
                        <span className="[font-size:0.75rem] [color:rgb(139,148,158)] [font-weight:400]"><span className="[margin:0_4px]">·</span>{rows.length} matchups</span>
                    </div>
                    <ChevronDown size={16} className={`[color:rgb(139,148,158)] [transition:transform_0.2s] ${isExpanded ? "[transform:rotate(180deg)]" : ""}`} />
                </div>
                {!isExpanded && (
                    <div className="[display:flex] [align-items:center] [gap:8px] [flex-wrap:wrap] [margin-left:24px]">
                        {summary.map((item, i) => ( <React.Fragment key={item.rating}>{i > 0 && <span className="[color:rgb(71,85,105)] [font-size:10px]">·</span>}<span style={{ color: THREAT_COLORS[item.rating] }} className="[font-size:11px] [font-weight:600] [text-transform:uppercase]">{item.count} {item.rating}</span></React.Fragment> ))}
                    </div>
                )}
            </button>
            {isExpanded && <div className="[padding:12px] [display:flex] [flex-direction:column] [gap:12px]">{rows.map((row, i) => ( <MatchupCard key={i} row={row} /> ))}</div>}
        </div>
    );
}
function MatchupCard({ row }: { row: MatchupRow }) {
    const batter = String(row["Batter"] ?? row["BATTER"] ?? "Unknown"), bowler = String(row["Bowler"] ?? row["BOWLER"] ?? "Unknown"), style = String(row["Style"] ?? row["STYLE"] ?? "");
    const isBunny = row.highlight_flags?.bunny_alert === true || row["IsBunny"] === true || row["is_bunny"] === true;
    const adv = getAdvantageProps(row.cell_tones?.["SR"], row["SR"]);
    const stats = [ { label: "RUNS", value: row["Runs"] }, { label: "BALLS", value: row["Balls"] }, { label: "OUTS", value: row["Outs"] }, { label: "AVG", value: row["Avg"] }, { label: "SR", value: row["SR"] } ];
    return (
        <div className={`[padding:12px] [border:1px_solid_rgb(48,54,61)] [border-radius:6px] [background:rgb(22,27,34)] [display:flex] [flex-direction:column] [gap:10px] [transition:all_var(--transition-fast)] hover:[border-color:rgb(139,148,158)]`}>
            <div className="[display:flex] [align-items:center] [justify-content:space-between] [gap:8px]">
                <div className="[display:flex] [align-items:center] [gap:8px] [flex-wrap:wrap]"><span className="[font-size:0.9rem] [color:rgb(240,246,252)] [font-weight:700]">{batter} <span className="[color:rgb(139,148,158)] [font-weight:400] [margin:0_2px]">vs</span> <span className="[font-weight:500]">{bowler}</span></span>{style && <StyleTag style={style} />}</div>
                {isBunny && <div className="[display:flex] [align-items:center] [gap:4px] [padding:2px_8px] [border-radius:4px] [background:rgb(45,31,0)] [border:1px_solid_rgb(245,158,11)] [color:rgb(245,158,11)] [font-size:0.65rem] [font-weight:700] [text-transform:uppercase] [letter-spacing:0.05em]"><AlertTriangle size={10} />BUNNY</div>}
            </div>
            <div className="[display:grid] [grid-template-columns:repeat(5,1fr)] [gap:4px]">{stats.map((s) => ( <div key={s.label} className="[display:flex] [flex-direction:column] [gap:2px]"><span className="[font-size:0.6rem] [font-weight:600] [color:rgb(139,148,158)] [text-transform:uppercase]">{s.label}</span><span className="[font-size:0.9rem] [color:rgb(240,246,252)] font-numeric">{s.value === null || s.value === undefined ? "-" : String(s.value)}</span></div> ))}</div>
            <div className="[display:flex] [flex-direction:column] [gap:4px]"><div className="[width:100%] [height:4px] [background:rgb(33,38,45)] [border-radius:2px] [overflow:hidden]"><div style={{ width: adv.width, backgroundColor: adv.backgroundColor }} className="[height:100%] [transition:width_0.3s_ease]" /></div><span style={{ color: adv.backgroundColor }} className="[font-size:0.6rem] [font-weight:600] [text-transform:uppercase] [letter-spacing:0.04em]">{adv.label}</span></div>
        </div>
    );
}
function StyleTag({ style }: { style: string }) {
    const dotClass = getStyleDotClass(style);
    return ( <div className="[display:inline-flex] [align-items:center] [gap:6px] [padding:2px_8px] [background:rgb(28,33,40)] [border-radius:12px] [border:1px_solid_rgb(48,54,61)] [font-size:0.65rem] [font-weight:600] [color:rgb(139,148,158)] [text-transform:uppercase] [letter-spacing:0.03em]"><div className={`[width:6px] [height:6px] [border-radius:50%] ${dotClass}`} />{style}</div> );
}
function getStyleDotClass(style: string) {
    if (style.includes("Leg Spin")) return "[background:rgb(245,158,11)]";
    if (style.includes("Off Spin")) return "[background:rgb(0,200,170)]";
    if (style.includes("Fast") || style.includes("Med")) return "[background:rgb(248,81,73)]";
    return "[background:rgb(139,148,158)]";
}
function getAdvantageProps(srTone: ToneToken | undefined, srRaw: unknown): { width: string; backgroundColor: string; label: string } {
    if (srTone === "elite") return { width: "90%", backgroundColor: "rgb(0, 200, 170)", label: "Batter Advantage" };
    if (srTone === "strong") return { width: "70%", backgroundColor: "rgb(0, 200, 170)", label: "Batter Advantage" };
    if (srTone === "caution") return { width: "40%", backgroundColor: "rgb(248, 81, 73)", label: "Bowler Advantage" };
    if (srTone === "danger") return { width: "20%", backgroundColor: "rgb(248, 81, 73)", label: "Bowler Advantage" };
    const sr = typeof srRaw === "number" ? srRaw : parseFloat(String(srRaw ?? ""));
    if (!Number.isNaN(sr)) {
        if (sr >= 130) return { width: "70%", backgroundColor: "rgb(0, 200, 170)", label: "Batter Advantage" };
        if (sr >= 100) return { width: "50%", backgroundColor: "rgb(48, 54, 61)", label: "Contested" };
        return { width: "40%", backgroundColor: "rgb(248, 81, 73)", label: "Bowler Advantage" };
    }
    return { width: "50%", backgroundColor: "rgb(48, 54, 61)", label: "Contested" };
}
