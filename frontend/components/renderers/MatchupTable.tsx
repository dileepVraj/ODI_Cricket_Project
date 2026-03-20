/**
 * MatchupTable.tsx - Batter-Grouped Card Layout (tab-based, design-matched)
 */
"use client";
import React, { useMemo, useState } from "react";
import { ChevronDown, ChevronUp, User } from "lucide-react";
import EmptyState from "@/components/common/EmptyState";
import { MatchupRow, toMatchupRows, ThreatRating } from "@/lib/comparison-types";
import { MatchupCard, PhaseBadge } from "./MatchupCard";

interface MatchupTableProps {
  data: Record<string, unknown>[];
  homeXI?: string[];
  awayXI?: string[];
  homeTeamName?: string;
  awayTeamName?: string;
}

const PHASE_KEYS = [
  { label: "PP",  key: "PP_ThreatRating" },
  { label: "MID", key: "Mid_ThreatRating" },
  { label: "DT",  key: "Death_ThreatRating" },
] as const;

function computePhaseSummary(rows: MatchupRow[]): Array<{ label: string; rating: ThreatRating }> {
  return PHASE_KEYS.flatMap(({ label, key }) => {
    const ratings = rows
      .map(r => r[key] as ThreatRating | null | undefined)
      .filter((r): r is ThreatRating => !!r && r !== "LOW DATA" && r !== "NEW MATCHUP");
    if (ratings.length === 0) return [];
    const counts: Partial<Record<ThreatRating, number>> = {};
    ratings.forEach(r => { counts[r] = (counts[r] ?? 0) + 1; });
    const top = (Object.entries(counts).sort((a, b) => (b[1] as number) - (a[1] as number))[0][0]) as ThreatRating;
    return [{ label, rating: top }];
  });
}

const LEGEND_ROWS = [
  { label: "BUNNY",     dot: "var(--tier-danger)",  text: "var(--tier-danger)",  bg: "rgba(220,38,38,0.10)",  border: "rgba(220,38,38,0.30)" },
  { label: "DOMINATED", dot: "var(--tier-danger)",  text: "var(--tier-danger)",  bg: "rgba(248,113,113,0.10)", border: "rgba(248,113,113,0.30)" },
  { label: "WATCHFUL",  dot: "var(--tier-caution)", text: "var(--tier-caution)", bg: "rgba(234,179,8,0.10)",  border: "rgba(234,179,8,0.30)" },
  { label: "CONTESTED", dot: "var(--tier-caution)", text: "var(--tier-caution)", bg: "rgba(249,115,22,0.10)", border: "rgba(249,115,22,0.30)" },
  { label: "ADVANTAGE", dot: "var(--accent-primary)", text: "var(--accent-primary)", bg: "rgba(59,130,246,0.10)", border: "rgba(59,130,246,0.30)" },
  { label: "DOMINANT",  dot: "var(--bg-deepest)",    text: "var(--bg-deepest)",    bg: "var(--tier-elite)",     border: "var(--tier-elite)" },
];

function LegendFooter() {
  return (
    <div className="[display:flex] [align-items:center] [justify-content:space-between] [padding:10px_16px] [border-top:1px_solid_var(--border-subtle)] [flex-wrap:wrap] [gap:8px]">
      <div className="[display:flex] [align-items:center] [gap:4px] [overflow-x:auto] [flex-wrap:nowrap]">
        <span className="[font-size:9px] [font-weight:700] [color:var(--text-muted)] [text-transform:uppercase] [margin-right:6px] [flex-shrink:0]">
          Legend:
        </span>
        {LEGEND_ROWS.map(item => (
          <LegendItem key={item.label} item={item} />
        ))}
      </div>
      <p className="[font-size:9px] [color:var(--text-muted)] [font-style:italic]">
        * NEW MATCHUP = limited data | LOW DATA = &lt;20 balls
      </p>
    </div>
  );
}

function LegendItem({ item }: { item: typeof LEGEND_ROWS[0] }) {
  const style = useMemo(() => ({ backgroundColor: item.bg, borderColor: item.border }), [item.bg, item.border]);
  const dotStyle = useMemo(() => ({ backgroundColor: item.dot }), [item.dot]);
  const textStyle = useMemo(() => ({ color: item.text }), [item.text]);

  return (
    <div
      style={style}
      className="[display:flex] [align-items:center] [gap:4px] [padding:2px_8px] [border-radius:4px] [border:1px_solid] [flex-shrink:0]"
    >
      <div style={dotStyle} className="[width:6px] [height:6px] [border-radius:50%]" />
      <span style={textStyle} className="[font-size:9px] [font-weight:700] [text-transform:uppercase]">
        {item.label}
      </span>
    </div>
  );
}
export default function MatchupTable({ data, homeXI, awayXI, homeTeamName, awayTeamName }: MatchupTableProps) {
  const [activeTab, setActiveTab]       = useState<"home" | "away">("home");
  const [batterFilter, setBatterFilter] = useState("");
  const [expandedGroups, setExpandedGroups] = useState<Record<string, boolean>>({});

  const rows = useMemo(() => toMatchupRows(data || []), [data]);

  const batterGroups = useMemo(() => {
    const groups: Record<string, MatchupRow[]> = {}, order: string[] = [];
    rows.forEach(row => {
      const b = String(row["Batter"] ?? row["BATTER"] ?? "Unknown");
      if (!groups[b]) { groups[b] = []; order.push(b); }
      groups[b].push(row);
    });
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

  if (!data || data.length === 0) return <EmptyState message="No matchup data available." />;

  const activeGroups  = activeTab === "home" ? homeBatterGroups : awayBatterGroups;
  const homeLabel     = `${homeTeamName ?? "Home"} Batters vs ${awayTeamName ?? "Away"} Bowlers`;
  const awayLabel     = `${awayTeamName ?? "Away"} Batters vs ${homeTeamName ?? "Home"} Bowlers`;

  return (
    <div className="[display:flex] [flex-direction:column] [border:1px_solid_var(--border-subtle)] [border-radius:var(--radius-md)] [overflow:hidden] [background:var(--bg-deepest)]">

      {/* Tab switcher */}
      <div className="[display:grid] [grid-template-columns:1fr_1fr] [border-bottom:1px_solid_var(--border-subtle)]">
        {(["home", "away"] as const).map((tab) => {
          const isActive = activeTab === tab;
          const label    = tab === "home" ? homeLabel : awayLabel;
          return (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`[padding:12px_20px] [text-align:left] [border-bottom:2px_solid] [transition:all_150ms] ${
                isActive
                  ? "[border-color:var(--accent-primary)] [background:rgba(80,180,34,0.05)]"
                  : "[border-color:transparent] hover:[background:rgba(255,255,255,0.03)]"
              }`}
            >
              <p className={`[font-size:0.78rem] [font-weight:700] [text-transform:uppercase] [letter-spacing:0.04em] ${
                isActive ? "[color:var(--accent-primary)]" : "[color:var(--text-muted)]"
              }`}>
                {label}
              </p>
            </button>
          );
        })}
      </div>

      {/* Sub-header: count + filter */}
      <div className="[display:flex] [align-items:center] [justify-content:space-between] [padding:8px_16px] [border-bottom:1px_solid_var(--border-subtle)]">
        <span className="[font-size:0.72rem] [padding:2px_8px] [border-radius:9999px] [background:var(--bg-active)] [color:var(--text-muted)] [font-weight:500]">
          {rows.length} matchups
        </span>
        <input
          type="text"
          placeholder="Filter batters..."
          value={batterFilter}
          onChange={e => setBatterFilter(e.target.value)}
          className="context-input [max-width:180px] [height:28px] [font-size:0.82rem]"
          aria-label="Filter batters by name"
        />
      </div>

      {/* Batter list */}
      <div className="[flex:1] [overflow-y:auto]">
        {activeGroups.length > 0
          ? activeGroups.map(g => (
              <MatchupBatterGroup
                key={g.batter}
                batter={g.batter}
                rows={g.rows}
                isExpanded={!!expandedGroups[g.batter]}
                onToggle={() => setExpandedGroups(p => ({ ...p, [g.batter]: !p[g.batter] }))}
              />
            ))
          : <div className="[padding:24px]"><EmptyState message="No matchup data for this side." /></div>
        }
      </div>

      {/* Legend footer */}
      <LegendFooter />
    </div>
  );
}

function MatchupBatterGroup({
  batter, rows, isExpanded, onToggle,
}: {
  batter: string; rows: MatchupRow[]; isExpanded: boolean; onToggle: () => void;
}) {
  const phaseSummary = useMemo(() => computePhaseSummary(rows), [rows]);

  return (
    <div className="[border-left:3px_solid_var(--accent-primary)] [border-bottom:1px_solid_var(--border-subtle)] [background:var(--bg-surface)] hover:[background:var(--bg-hover)] [transition:background_150ms]">
      <button
        onClick={onToggle}
        aria-label={`${isExpanded ? "Collapse" : "Expand"} matchups for ${batter}`}
        className="[width:100%] [display:flex] [align-items:center] [justify-content:space-between] [padding:10px_14px]"
      >
        {/* Avatar + name + phase badges */}
        <div className="[display:flex] [align-items:center] [gap:12px]">
          <div className="[width:40px] [height:40px] [border-radius:4px] [background:rgba(255,255,255,0.05)] [border:1px_solid_var(--border-default)] [display:flex] [align-items:center] [justify-content:center] [flex-shrink:0]">
            <User size={18} className="[color:var(--text-muted)]" />
          </div>
          <div className="[display:flex] [flex-direction:column] [gap:4px] [text-align:left]">
            <h3 className="[font-size:0.92rem] [font-weight:700] [color:var(--text-primary)]">{batter}</h3>
            {phaseSummary.length > 0 && (
              <div className="[display:flex] [gap:4px] [flex-wrap:wrap]">
                {phaseSummary.map(({ label, rating }) => (
                  <PhaseBadge key={label} label={label} rating={rating} />
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Right: active label + count + chevron */}
        <div className="[display:flex] [align-items:center] [gap:12px] [flex-shrink:0]">
          {isExpanded && (
            <span className="[font-size:11px] [font-weight:700] [color:var(--accent-primary)] [text-transform:uppercase] [letter-spacing:0.04em]">
              Active Matchup
            </span>
          )}
          <span className="[font-size:11px] [font-weight:500] [color:var(--text-muted)] [text-transform:uppercase]">
            {rows.length} matchups
          </span>
          {isExpanded
            ? <ChevronUp size={16} className="[color:var(--text-muted)]" />
            : <ChevronDown size={16} className="[color:var(--text-muted)]" />
          }
        </div>
      </button>

      {isExpanded && (
        <div className="[background:rgba(28,33,39,0.5)] [border-top:1px_solid_var(--border-subtle)]">
          {rows.map((row, i) => (
            <div key={i} style={i > 0 ? { borderTop: "1px solid var(--border-subtle)" } : {}}>
              <MatchupCard row={row} />
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
