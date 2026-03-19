/**
 * MatchupTable.tsx - Batter-Grouped Card Layout
 */
"use client";
import React, { useMemo, useState } from "react";
import { Crosshair, ChevronDown, ChevronUp } from "lucide-react";
import EmptyState from "@/components/common/EmptyState";
import { MatchupRow, toMatchupRows } from "@/lib/comparison-types";
interface MatchupTableProps { data: Record<string, unknown>[]; homeXI?: string[]; awayXI?: string[]; homeTeamName?: string; awayTeamName?: string; }
type ThreatRating = "NEW MATCHUP" | "LOW DATA" | "BUNNY" | "DOMINATED" | "WATCHFUL" | "CONTESTED" | "ADVANTAGE" | "THREAT" | "DOMINANT";

function getBowlingBadgeColor(style: string): string {
  if (style.includes("Leg Spin"))  return "var(--accent-secondary)";
  if (style.includes("Off Spin"))  return "var(--accent-primary)";
  if (style.includes("Slow Left-Arm") || style.includes("Left-Arm Orth") || style.toUpperCase().includes("ORTH")) return "var(--tier-strong)";
  if (style.toUpperCase().includes("MED")) return "var(--tier-caution)";
  if (style.toUpperCase().includes("FAST")) return "var(--tier-danger)";
  return "var(--text-muted)";
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

const THREAT_BADGE_STYLES: Record<ThreatRating, { bg: string; text: string; border: string }> = {
  "NEW MATCHUP": { bg: "var(--bg-elevated)",            text: "var(--text-disabled)", border: "var(--border-default)" },
  "LOW DATA":    { bg: "var(--bg-elevated)",            text: "var(--text-disabled)", border: "var(--border-default)" },
  BUNNY:         { bg: "var(--bg-danger)",              text: "var(--tier-danger)",   border: "var(--tier-danger)" },
  DOMINATED:     { bg: "var(--bg-danger)",              text: "var(--tier-danger)",   border: "var(--tier-danger)" },
  WATCHFUL:      { bg: "var(--bg-caution)",             text: "var(--tier-caution)",  border: "var(--tier-caution)" },
  CONTESTED:     { bg: "var(--bg-deepest)",             text: "var(--text-muted)",    border: "var(--bg-active)" },
  ADVANTAGE:     { bg: "rgba(0, 200, 170, 0.10)",       text: "var(--tier-strong)",   border: "rgba(0, 200, 170, 0.25)" },
  THREAT:        { bg: "var(--bg-caution)",             text: "var(--tier-caution)",  border: "var(--tier-caution)" },
  DOMINANT:      { bg: "rgba(34, 197, 94, 0.12)",       text: "var(--tier-elite)",    border: "rgba(34, 197, 94, 0.20)" },
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

function PhaseBadge({ label, rating }: { label: string; rating: ThreatRating }) {
  const badgeStyle = useMemo(() => ({
    color: THREAT_STRIP_COLORS[rating],
    borderColor: THREAT_STRIP_COLORS[rating]
  }), [rating]);

  return (
    <div
      style={badgeStyle}
      className="[display:inline-flex] [align-items:center] [gap:4px] [padding:2px_7px] [border-radius:4px] [border:1px_solid] [background:rgba(255,255,255,0.03)]"
    >
      <span className="[font-size:9px] [font-weight:500] [color:var(--text-disabled)] [text-transform:uppercase]">{label}</span>
      <span className="[font-size:9px] [font-weight:700] [text-transform:uppercase]">{rating}</span>
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
  const confidence      = row["confidence"]           as number       | null | undefined;
  const dismissalStruct = row["dismissal_structural"] as number       | null | undefined;
  const dismissalCaught = row["dismissal_caught"]     as number       | null | undefined;
  const dismissalOther  = row["dismissal_other"]      as number       | null | undefined;
  const ppRating        = row["pp_threat_rating"]     as ThreatRating | null | undefined;
  const midRating       = row["mid_threat_rating"]    as ThreatRating | null | undefined;
  const deathRating     = row["death_threat_rating"]  as ThreatRating | null | undefined;

  const rating: ThreatRating = useMemo(() => (row["threat_rating"] as ThreatRating | undefined) ?? "LOW DATA", [row]);

  const visualProps = useMemo(() => ({
    strip: { backgroundColor: THREAT_STRIP_COLORS[rating] },
    badge: {
      backgroundColor: THREAT_BADGE_STYLES[rating].bg,
      color: THREAT_BADGE_STYLES[rating].text,
      borderColor: THREAT_BADGE_STYLES[rating].border
    },
    bowling: { backgroundColor: getBowlingBadgeColor(style) }
  }), [rating, style]);

  const confidenceDotsStyles = useMemo(() => {
    return [1, 2, 3, 4, 5].map(i => ({
      backgroundColor: i <= (confidence ?? 0) ? THREAT_STRIP_COLORS[rating] : "transparent",
      borderColor:     i <= (confidence ?? 0) ? THREAT_STRIP_COLORS[rating] : "var(--border-default)",
    }));
  }, [confidence, rating]);

  return (
    <div className="[display:flex] [flex-direction:column] [border:1px_solid_var(--border-strong)] [border-radius:var(--radius-sm)] [overflow:hidden] [background:var(--bg-surface)] [transition:border-color_var(--transition-fast)] hover:[border-color:var(--text-disabled)]">

      {/* Row: danger strip + main content */}
      <div className="[display:flex]">
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
            {outs > 0 && (dismissalStruct != null || dismissalCaught != null || dismissalOther != null) && (
              <span className="[font-size:0.68rem] [color:var(--text-disabled)] [white-space:nowrap]">
                {[
                  dismissalStruct ? `${dismissalStruct} B/LBW` : null,
                  dismissalCaught ? `${dismissalCaught}c`       : null,
                  dismissalOther  ? `${dismissalOther} oth`     : null,
                ].filter(Boolean).join(" · ")}
              </span>
            )}
          </div>

          {/* Right: confidence dots + threat rating badge */}
          <div className="[display:flex] [flex-direction:column] [align-items:flex-end] [gap:4px] [flex-shrink:0]">
            {confidence != null && confidence > 0 && (
              <div className="[display:flex] [gap:3px]">
                {confidenceDotsStyles.map((dotStyle, i) => (
                  <div
                    key={i}
                    style={dotStyle}
                    className="[width:5px] [height:5px] [border-radius:50%] [border:1px_solid]"
                  />
                ))}
              </div>
            )}
            <div
              style={visualProps.badge}
              className="[display:flex] [align-items:center] [padding:4px_10px] [border-radius:var(--radius-sm)] [border:1px_solid]"
            >
              <span className="[font-size:0.7rem] [font-weight:700] [text-transform:uppercase] [letter-spacing:0.05em] [white-space:nowrap]">
                {rating}
              </span>
            </div>
          </div>

        </div>
      </div>

      {/* Phase breakdown strip */}
      {(ppRating != null || midRating != null || deathRating != null) && (
        <div className="[padding:5px_12px_7px_20px] [display:flex] [gap:6px] [border-top:1px_solid_var(--border-default)] [flex-wrap:wrap] [align-items:center]">
          {ppRating    != null && <PhaseBadge label="PP"  rating={ppRating} />}
          {midRating   != null && <PhaseBadge label="MID" rating={midRating} />}
          {deathRating != null && <PhaseBadge label="DT"  rating={deathRating} />}
        </div>
      )}
    </div>
  );
}
