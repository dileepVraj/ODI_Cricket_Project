/**
 * MatchupTable.tsx - Batter-Dossier Grid Layout
 */
"use client";
import React, { useMemo, useState, useEffect } from "react";
import EmptyState from "@/components/common/EmptyState";
import { 
  MatchupRow, 
  toMatchupRows, 
  ThreatRating, 
  THREAT_BORDER_CLASSES, 
  THREAT_TEXT_CLASSES, 
  PHASE_SEVERITY_ORDER 
} from "@/lib/comparison-types";
import { MatchupCard } from "./MatchupCard";

const PHASE_KEYS = [
  { l: "PP", k: "PP_ThreatRating" }, 
  { l: "MID", k: "Mid_ThreatRating" }, 
  { l: "DT", k: "Death_ThreatRating" }
] as const;

function getWorst(s: Array<{ l: string; r: ThreatRating }>): ThreatRating {
  if (s.length === 0) return "LOW DATA";
  let w = s[0].r;
  for (const { r } of s) {
    const wi = PHASE_SEVERITY_ORDER.indexOf(w);
    const ri = PHASE_SEVERITY_ORDER.indexOf(r);
    if (ri !== -1 && (wi === -1 || ri < wi)) w = r;
  }
  return w;
}

function getSummary(r: MatchupRow[]): Array<{ l: string; r: ThreatRating }> {
  return PHASE_KEYS.flatMap(({ l, k }) => {
    const rs = r.map(x => x[k] as ThreatRating | undefined).filter((x): x is ThreatRating => !!x && x !== "LOW DATA" && x !== "NEW MATCHUP");
    if (rs.length === 0) return [];
    const c: Partial<Record<ThreatRating, number>> = {};
    rs.forEach(x => { c[x] = (c[x] ?? 0) + 1; });
    const top = (Object.entries(c).sort((a, b) => (b[1] as number) - (a[1] as number))[0][0]) as ThreatRating;
    return [{ l, r: top }];
  });
}

const LEGEND = [
  { l: "BUNNY", d: "[background:var(--tier-danger)]", t: "[color:var(--tier-danger)]", b: "[background:rgba(220,38,38,0.10)]", br: "[border-color:rgba(220,38,38,0.30)]" },
  { l: "DOMINATED", d: "[background:var(--tier-danger)]", t: "[color:var(--tier-danger)]", b: "[background:rgba(248,113,113,0.10)]", br: "[border-color:rgba(248,113,113,0.30)]" },
  { l: "WATCHFUL", d: "[background:var(--tier-caution)]", t: "[color:var(--tier-caution)]", b: "[background:rgba(234,179,8,0.10)]", br: "[border-color:rgba(234,179,8,0.30)]" },
  { l: "CONTESTED", d: "[background:var(--tier-caution)]", t: "[color:var(--tier-caution)]", b: "[background:rgba(249,115,22,0.10)]", br: "[border-color:rgba(249,115,22,0.30)]" },
  { l: "ADVANTAGE", d: "[background:var(--accent-primary)]", t: "[color:var(--accent-primary)]", b: "[background:rgba(59,130,246,0.10)]", br: "[border-color:rgba(59,130,246,0.30)]" },
  { l: "DOMINANT", d: "[background:var(--bg-deepest)]", t: "[color:var(--bg-deepest)]", b: "[background:var(--tier-elite)]", br: "[border-color:var(--tier-elite)]" }
];

const T_ORDER: ThreatRating[] = ["BUNNY", "DOMINATED", "WATCHFUL", "CONTESTED", "ADVANTAGE", "THREAT", "DOMINANT"];

export default function MatchupTable({ data, homeXI, awayXI, homeTeamName, awayTeamName }: { data: Record<string, unknown>[]; homeXI?: string[]; awayXI?: string[]; homeTeamName?: string; awayTeamName?: string; }) {
  const [tab, setTab] = useState<"home" | "away">("home");
  const [sel, setSel] = useState<string | null>(null);
  const rows = useMemo(() => toMatchupRows(data || []), [data]);
  
  const grps = useMemo(() => {
    const g: Record<string, MatchupRow[]> = {}, o: string[] = [];
    rows.forEach(r => {
      const b = String(r.Batter ?? "Unknown");
      if (!g[b]) { g[b] = []; o.push(b); }
      g[b].push(r);
    });
    return o.map(b => ({ b, r: g[b] }));
  }, [rows]);

  const act = useMemo(() => {
    const xi = tab === "home" ? homeXI : awayXI;
    return xi ? grps.filter(g => xi.includes(g.b)) : (tab === "home" ? grps : []);
  }, [tab, grps, homeXI, awayXI]);

  const eSel = sel && act.some(g => g.b === sel) ? sel : (act[0]?.b || null);
  const sRows = act.find(g => g.b === eSel)?.r || [];
  const vFil = sRows.some(r => r.VenueFiltered === true);
  const tB = sRows.reduce((s, r) => s + (r.Balls ?? 0), 0);
  const tM = sRows.length === 0 ? 0 : Math.max(0, ...sRows.map(r => r.MatchCount ?? 0));

  const tC = useMemo(() => {
    const c: Record<ThreatRating, number> = { BUNNY: 0, DOMINATED: 0, WATCHFUL: 0, CONTESTED: 0, ADVANTAGE: 0, THREAT: 0, DOMINANT: 0, "LOW DATA": 0, "NEW MATCHUP": 0 };
    sRows.forEach(r => { if (r.ThreatRating) c[r.ThreatRating]++; });
    return c;
  }, [sRows]);

  useEffect(() => { setSel(null); }, [tab]);

  if (!data || data.length === 0) return <EmptyState message="No matchup data available." />;

  return (
    <div className="terminal-panel [display:flex] [flex-direction:column] [overflow:hidden]">
      <div className="[display:flex] [border-bottom:1px_solid_var(--border-subtle)]">
        {(["home", "away"] as const).map(t => {
          const l = t === "home" ? `${homeTeamName ?? "Home"} Batters vs ${awayTeamName ?? "Away"} Bowlers` : `${awayTeamName ?? "Away"} Batters vs ${homeTeamName ?? "Home"} Bowlers`;
          return (
            <button 
              key={t} 
              onClick={() => setTab(t)} 
              aria-label={`View ${l}`} 
              className={`format-tab ${tab === t ? "active" : ""}`}
            >
              <span>{l}</span>
            </button>
          );
        })}
      </div>

      <div className="[display:flex] [align-items:center] [gap:8px] [padding:6px_16px] [border-bottom:1px_solid_var(--border-subtle)] [flex-shrink:0]">
        <span className="[font-size:0.72rem] [padding:2px_8px] [border-radius:9999px] [background:var(--bg-active)] [color:var(--text-muted)] [font-weight:500]">{rows.length} matchups</span>
        {vFil ? <span className="[font-size:9px] [font-weight:700] [text-transform:uppercase] [padding:2px_7px] [border-radius:4px] [background:rgba(245,158,11,0.15)] [border:1px_solid_rgba(245,158,11,0.4)] [color:var(--tier-caution)]">AT VENUE</span> : <span className="[font-size:9px] [font-weight:700] [text-transform:uppercase] [padding:2px_7px] [border-radius:4px] [background:var(--bg-elevated)] [border:1px_solid_var(--border-subtle)] [color:var(--text-muted)]">ALL GROUNDS</span>}
      </div>

      <div className="[display:flex] [gap:6px] [padding:8px_16px] [overflow-x:auto] [border-bottom:1px_solid_var(--border-subtle)] [flex-shrink:0] no-scrollbar">
        {act.map(g => {
          const r = getWorst(getSummary(g.r));
          const iA = eSel === g.b;
          return (
            <button 
              key={g.b} 
              onClick={() => setSel(g.b)} 
              aria-label={`Matchups for ${g.b}`} 
              aria-pressed={iA} 
              className={`[display:inline-flex] [align-items:center] [padding:4px_12px] [border-radius:4px] [font-size:0.78rem] [font-weight:600] [cursor:pointer] [white-space:nowrap] [flex-shrink:0] [border-left-width:3px] [border-left-style:solid] ${THREAT_BORDER_CLASSES[r]} ${iA ? "[background:var(--bg-active)] [color:var(--text-primary)] [border-top:1px_solid_rgba(37,99,235,0.5)] [border-right:1px_solid_rgba(37,99,235,0.5)] [border-bottom:1px_solid_rgba(37,99,235,0.5)]" : "[background:var(--bg-elevated)] [color:var(--text-muted)] [border-top:1px_solid_var(--border-subtle)] [border-right:1px_solid_var(--border-subtle)] [border-bottom:1px_solid_var(--border-subtle)]"}`}
            >
              <span>{g.b}</span>
            </button>
          );
        })}
      </div>

      {eSel && (
        <div className="[display:flex] [align-items:flex-start] [justify-content:space-between] [padding:10px_16px] [border-bottom:1px_solid_var(--border-subtle)] [flex-shrink:0]">
          <div className="[display:flex] [flex-direction:column]">
            <span className="[font-size:1.05rem] [font-weight:700] [color:var(--text-primary)]">{eSel}</span>
            <span className="[font-size:0.72rem] [color:var(--text-muted)] [margin-top:2px]">{vFil ? "AT VENUE" : "ALL GROUNDS"}:&nbsp;<span className="font-numeric [color:var(--text-primary)] [font-weight:600]">{tM}m · {tB}b</span></span>
          </div>
          <div className="[display:flex] [gap:6px] [align-items:center] [flex-wrap:wrap] [justify-content:flex-end] [max-width:55%]">
            {T_ORDER.filter(r => tC[r] > 0).map((r, i, a) => (
              <React.Fragment key={r}>
                <span className={`[font-size:9px] [font-weight:700] [text-transform:uppercase] ${THREAT_TEXT_CLASSES[r]}`}>{tC[r]} {r}</span>
                {i < a.length - 1 && <span className="[font-size:9px] [color:var(--text-muted)]">·</span>}
              </React.Fragment>
            ))}
            {T_ORDER.every(r => (tC[r] ?? 0) === 0) && <span className="[font-size:9px] [color:var(--text-muted)] [font-style:italic]">No data yet</span>}
          </div>
        </div>
      )}

      <div className="[flex:1] [overflow-y:auto] [padding:12px_16px]">
        {sRows.length > 0 ? (
          <div className="[display:grid] [grid-template-columns:repeat(2,minmax(0,1fr))] [gap:10px] max-[640px]:[grid-template-columns:1fr]">
            {sRows.map((r, i) => <MatchupCard key={r.Bowler ?? i} row={r} />)}
          </div>
        ) : (
          <EmptyState message="No data for this batter." />
        )}
      </div>

      <div className="[display:flex] [align-items:center] [justify-content:space-between] [padding:10px_16px] [border-top:1px_solid_var(--border-subtle)] [flex-wrap:wrap] [gap:8px]">
        <div className="[display:flex] [align-items:center] [gap:4px] [overflow-x:auto] [flex-wrap:nowrap]">
          <span className="[font-size:9px] [font-weight:700] [color:var(--text-muted)] [text-transform:uppercase] [margin-right:6px] [flex-shrink:0]">Legend:</span>
          {LEGEND.map(i => (
            <div key={i.l} className={`[display:flex] [align-items:center] [gap:4px] [padding:2px_8px] [border-radius:4px] [border-width:1px] [border-style:solid] [flex-shrink:0] ${i.b} ${i.br}`}>
              <div className={`[width:6px] [height:6px] [border-radius:50%] ${i.d}`} />
              <span className={`[font-size:9px] [font-weight:700] [text-transform:uppercase] ${i.t}`}>{i.l}</span>
            </div>
          ))}
        </div>
        <p className="[font-size:9px] [color:var(--text-muted)] [font-style:italic]">* NEW MATCHUP = limited data | LOW DATA = &lt;20 balls</p>
      </div>
    </div>
  );
}
