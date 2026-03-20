/**
 * MatchupCard.tsx - Individual Matchup Row (flat inline style)
 */
"use client";
import React, { useMemo } from "react";
import { BarChart2 } from "lucide-react";
import { MatchupRow, ThreatRating } from "@/lib/comparison-types";
import { stripEmoji } from "@/lib/utils";

export const THREAT_STRIP_COLORS: Record<ThreatRating, string> = {
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

// Solid pill colours matching the design
const PILL_BG: Record<ThreatRating, string> = {
  "NEW MATCHUP": "transparent",
  "LOW DATA":    "transparent",
  BUNNY:         "var(--tier-danger)",
  DOMINATED:     "var(--tier-danger)",
  WATCHFUL:      "var(--tier-caution)",
  CONTESTED:     "var(--tier-caution)",
  ADVANTAGE:     "var(--accent-primary)",
  THREAT:        "var(--tier-caution)",
  DOMINANT:      "var(--tier-elite)",
};

const PILL_TEXT: Record<ThreatRating, string> = {
  "NEW MATCHUP": "var(--text-disabled)",
  "LOW DATA":    "var(--text-disabled)",
  BUNNY:         "white",
  DOMINATED:     "var(--bg-deepest)",
  WATCHFUL:      "var(--bg-deepest)",
  CONTESTED:     "var(--bg-deepest)",
  ADVANTAGE:     "white",
  THREAT:        "var(--bg-deepest)",
  DOMINANT:      "var(--bg-deepest)",
};

function bowlerTypeAbbr(style: string): string {
  const s = style.toLowerCase();
  if (!s) return "–";
  if (s.includes("right") && s.includes("fast"))   return "RF";
  if (s.includes("left")  && s.includes("fast"))   return "LF";
  if (s.includes("right") && s.includes("medium")) return "RM";
  if (s.includes("left")  && s.includes("medium")) return "LM";
  if (s.includes("leg spin") || s.includes("wrist spin")) return "LB";
  if (s.includes("off spin"))                       return "OB";
  if (s.includes("left") && (s.includes("orth") || s.includes("slow"))) return "SLA";
  return style.substring(0, 2).toUpperCase();
}

export function PhaseBadge({ label, rating }: { label: string; rating: ThreatRating }) {
  const color = THREAT_STRIP_COLORS[rating];
  const bg = useMemo(() => {
    return rating === "DOMINANT"                          ? "rgba(34,197,94,0.12)"
         : rating === "THREAT" || rating === "WATCHFUL"  ? "rgba(245,158,11,0.10)"
         : rating === "ADVANTAGE"                        ? "rgba(20,184,166,0.10)"
         : rating === "BUNNY" || rating === "DOMINATED"  ? "rgba(239,68,68,0.10)"
         : "var(--bg-elevated)";
  }, [rating]);

  const styleObj = useMemo(() => ({ borderColor: color, backgroundColor: bg }), [color, bg]);

  return (
    <div
      style={styleObj}
      className="[display:inline-flex] [align-items:center] [gap:3px] [padding:2px_7px] [border-radius:4px] [border:1px_solid]"
    >
      <span className="[font-size:0.65rem] [font-weight:500] [color:var(--text-muted)] [text-transform:uppercase]">{label}:</span>
      <span style={{ color }} className="[font-size:0.72rem] [font-weight:700] [text-transform:uppercase]">{rating}</span>
    </div>
  );
}

export function MatchupCard({ row }: { row: MatchupRow }) {
  const bowler = String(row["Bowler"] ?? row["BOWLER"] ?? "Unknown");
  const style  = stripEmoji(String(row["Style"] ?? row["STYLE"] ?? ""));
  const avg    = row["Avg"]   === null || row["Avg"]   === undefined ? "-" : String(row["Avg"]);
  const sr     = row["SR"]    === null || row["SR"]    === undefined ? "-" : String(row["SR"]);
  const balls  = row["Balls"] === null || row["Balls"] === undefined ? "-" : String(row["Balls"]);

  const rating: ThreatRating = useMemo(
    () => (row["ThreatRating"] as ThreatRating | undefined) ?? "LOW DATA",
    [row]
  );

  const isLowData = rating === "LOW DATA" || rating === "NEW MATCHUP";
  const typeAbbr  = useMemo(() => bowlerTypeAbbr(style), [style]);
  const pillStyle = useMemo(
    () => ({ backgroundColor: PILL_BG[rating], color: PILL_TEXT[rating] }),
    [rating]
  );

  return (
    <div className="[display:flex] [align-items:center] [justify-content:space-between] [padding:10px_12px] hover:[background:rgba(255,255,255,0.03)] [transition:background_150ms]">

      {/* Left: type abbr · bowler name · stats */}
      <div className="[display:flex] [align-items:center] [gap:12px]">
        <div className="[width:32px] [flex-shrink:0] [text-align:center]">
          <span className="[font-size:10px] [font-weight:700] [color:var(--text-muted)] [text-transform:uppercase]">
            {typeAbbr}
          </span>
        </div>
        <span className="[font-size:0.9rem] [font-weight:600] [color:var(--text-primary)] [white-space:nowrap]">
          {bowler}
        </span>
        <div className="[display:flex] [align-items:center] [gap:12px] font-numeric [font-size:0.78rem] [color:var(--text-muted)]">
          <span>AVG <span className="[color:var(--text-primary)] [font-weight:600]">{avg}</span></span>
          <span>SR  <span className="[color:var(--text-primary)] [font-weight:600]">{sr}</span></span>
          <span>BALLS <span className="[color:var(--text-primary)] [font-weight:600]">{balls}</span></span>
        </div>
      </div>

      {/* Right: threat pill · low-data label · bar icon */}
      <div className="[display:flex] [align-items:center] [gap:8px]">
        {!isLowData && (
          <span
            style={pillStyle}
            className="[padding:2px_10px] [border-radius:9999px] [font-size:0.72rem] [font-weight:900] [text-transform:uppercase] [letter-spacing:0.04em] [white-space:nowrap]"
          >
            {rating}
          </span>
        )}
        {isLowData && (
          <span className="[font-size:9px] [font-weight:700] [color:var(--text-disabled)] [text-transform:uppercase] [font-style:italic]">
            Low Data
          </span>
        )}
        <BarChart2 size={14} className="[color:var(--text-muted)]" />
      </div>
    </div>
  );
}
