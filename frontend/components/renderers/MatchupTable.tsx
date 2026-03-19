/**
 * MatchupTable.tsx - Batter-Grouped Card Layout
 */
"use client";
import React, { useMemo, useState } from "react";
import { Crosshair, ChevronDown, ChevronUp } from "lucide-react";
import EmptyState from "@/components/common/EmptyState";
import { MatchupRow, toMatchupRows } from "@/lib/comparison-types";
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

function getBowlingBadgeColor(style: string): string {
  if (style.includes("Leg Spin"))  return "var(--accent-secondary)";
  if (style.includes("Off Spin"))  return "var(--accent-primary)";
  if (style.includes("Slow Left-Arm") || style.includes("Left-Arm Orth") || style.toUpperCase().includes("ORTH")) return "var(--tier-strong)";
  if (style.toUpperCase().includes("MED")) return "var(--tier-caution)";
  if (style.toUpperCase().includes("FAST")) return "var(--tier-danger)";
  return "var(--text-muted)";
}

const THREAT_STRIP_COLORS: Record<ThreatRating, string> = {
  BUNNY:      "var(--tier-danger)",
  THREAT:     "var(--tier-caution)",
  CAUTION:    "var(--tier-caution)",
  SAFE:       "var(--tier-elite)",
  "LOW DATA": "var(--text-disabled)",
  CONTESTED:  "var(--bg-active)",
};

const THREAT_BADGE_STYLES: Record<ThreatRating, { bg: string; text: string; border: string }> = {
  BUNNY:      { bg: "var(--bg-danger)", text: "var(--tier-danger)", border: "var(--tier-danger)" },
  THREAT:     { bg: "var(--bg-caution)", text: "var(--tier-caution)", border: "var(--tier-caution)" },
  CAUTION:    { bg: "var(--bg-caution)", text: "var(--tier-caution)", border: "var(--border-caution)" },
  SAFE:       { bg: "rgba(34, 197, 94, 0.12)", text: "var(--tier-elite)", border: "rgba(34, 197, 94, 0.20)" },
  "LOW DATA": { bg: "var(--bg-elevated)", text: "var(--text-disabled)", border: "var(--border-default)" },
  CONTESTED:  { bg: "var(--bg-deepest)", text: "var(--text-muted)", border: "var(--bg-active)" },
};

const LEGEND_ITEMS: Array<{ label: string; color: string }> = [
  { label: "BUNNY", color: "var(--tier-danger)" },
  { label: "THREAT", color: "var(--tier-caution)" },
  { label: "CAUTION", color: "var(--tier-caution)" },
  { label: "SAFE", color: "var(--tier-elite)" },
  { label: "LOW DATA", color: "var(--text-disabled)" },
  { label: "CONTESTED", color: "var(--text-muted)" }
];

function LegendStrip() {
    return (
        <div className="[display:flex] [align-items:center] [gap:16px] [padding:8px_0] [border-bottom:1px_solid_rgb(26,39,64)] [margin-bottom:16px] [flex-wrap:wrap]">
            {LEGEND_ITEMS.map((item, i) => (
                <React.Fragment key={item.label}>
                    {i > 0 && <span className="[color:rgb(71,85,105)] [font-size:10px]">·</span>}
                    <div className="[display:flex] [align-items:center] [gap:6px]">
                        <div style={{ backgroundColor: item.color }} className="[width:8px] [height:8px] [border-radius:50%] [flex-shrink:0]" />
                        <span className="[font-size:11px] [color:rgb(100,116,139)] [font-weight:500] [text-transform:uppercase] [letter-spacing:0.04em]">{item.label}</span>
                    </div>
                </React.Fragment>
            ))}
        </div>
    );
}

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
                        {summary.map((item, i) => ( <React.Fragment key={item.rating}>{i > 0 && <span className="[color:rgb(71,85,105)] [font-size:10px]">·</span>}<span style={{ color: THREAT_STRIP_COLORS[item.rating] }} className="[font-size:11px] [font-weight:600] [text-transform:uppercase]">{item.count} {item.rating}</span></React.Fragment> ))}
                    </div>
                )}
            </button>
            {isExpanded && <div className="[padding:12px] [display:flex] [flex-direction:column] [gap:12px]">{rows.map((row, i) => ( <MatchupCard key={i} row={row} /> ))}</div>}
        </div>
    );
}

function MatchupCard({ row }: { row: MatchupRow }) {
  const bowler = String(row["Bowler"] ?? row["BOWLER"] ?? "Unknown");
  const style  = String(row["Style"]  ?? row["STYLE"]  ?? "");
  const avg    = row["Avg"]   === null || row["Avg"]   === undefined ? "-" : String(row["Avg"]);
  const sr     = row["SR"]    === null || row["SR"]    === undefined ? "-" : String(row["SR"]);
  const balls  = row["Balls"] === null || row["Balls"] === undefined ? "-" : String(row["Balls"]);
  const outs   = row["Outs"]  === null || row["Outs"]  === undefined ? 0   : Number(row["Outs"]);

  const rating = useMemo(() => computeThreatRating(row), [row]);

  const visualProps = useMemo(() => ({
    strip: { backgroundColor: THREAT_STRIP_COLORS[rating] },
    badge: {
      backgroundColor: THREAT_BADGE_STYLES[rating].bg,
      color: THREAT_BADGE_STYLES[rating].text,
      borderColor: THREAT_BADGE_STYLES[rating].border
    },
    bowling: { backgroundColor: getBowlingBadgeColor(style) }
  }), [rating, style]);

  return (
    <div className="[display:flex] [border:1px_solid_var(--border-strong)] [border-radius:var(--radius-sm)] [overflow:hidden] [background:var(--bg-surface)] [transition:border-color_var(--transition-fast)] hover:[border-color:var(--text-disabled)]">

      {/* Left danger strip */}
      <div style={visualProps.strip} className="[width:8px] [flex-shrink:0]" />

      {/* Main content */}
      <div className="[flex:1] [padding:10px_12px] [display:flex] [align-items:center] [justify-content:space-between] [gap:12px] [min-height:64px]">

        {/* Left: bowler + bowling badge */}
        <div className="[display:flex] [flex-direction:column] [gap:4px] [min-width:0]">
          <span className="[font-size:0.875rem] [font-weight:700] [color:var(--text-primary)] [white-space:nowrap] [overflow:hidden] [text-overflow:ellipsis]">
            {bowler}
          </span>
          {style && (
            <div
              style={visualProps.bowling}
              className="[display:inline-flex] [align-items:center] [padding:2px_8px] [border-radius:9999px] [width:fit-content]"
            >
              <span className="[font-size:10px] [font-weight:600] [color:white] [text-transform:uppercase] [letter-spacing:0.03em] [white-space:nowrap]">
                {style}
              </span>
            </div>
          )}
        </div>

        {/* Center: stats */}
        <div className="[display:flex] [flex-direction:column] [gap:2px] [flex:1] [min-width:0]">
          <span className="[font-size:0.8rem] [color:var(--text-secondary)] [white-space:nowrap]">
            AVG <span className="[color:var(--text-primary)] [font-weight:600]">{avg}</span>
            <span className="[margin:0_6px] [color:var(--text-disabled)]">·</span>
            SR <span className="[color:var(--text-primary)] [font-weight:600]">{sr}</span>
            <span className="[margin:0_6px] [color:var(--text-disabled)]">·</span>
            <span className="[color:var(--text-secondary)]">{balls} balls</span>
          </span>
          <span className="[font-size:0.72rem] [color:var(--text-muted)]">
            {outs} {outs === 1 ? "out" : "outs"}
          </span>
        </div>

        {/* Right: threat rating badge */}
        <div
          style={visualProps.badge}
          className="[display:flex] [align-items:center] [padding:4px_10px] [border-radius:var(--radius-sm)] [border:1px_solid] [flex-shrink:0]"
        >
          <span className="[font-size:0.7rem] [font-weight:700] [text-transform:uppercase] [letter-spacing:0.05em] [white-space:nowrap]">
            {rating === "LOW DATA" ? "LOW DATA" : rating}
          </span>
        </div>

      </div>
    </div>
  );
}
