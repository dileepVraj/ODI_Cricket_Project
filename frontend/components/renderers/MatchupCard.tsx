/**
 * MatchupCard.tsx - Individual Matchup Card component
 */
"use client";
import React, { useMemo } from "react";
import { MatchupRow, ThreatRating } from "@/lib/comparison-types";

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

function getBowlingBadgeColor(style: string): string {
  if (style.includes("Leg Spin"))  return "var(--accent-secondary)";
  if (style.includes("Off Spin"))  return "var(--accent-primary)";
  if (style.includes("Slow Left-Arm") || style.includes("Left-Arm Orth") || style.toUpperCase().includes("ORTH")) return "var(--tier-strong)";
  if (style.toUpperCase().includes("MED")) return "var(--tier-caution)";
  if (style.toUpperCase().includes("FAST")) return "var(--tier-danger)";
  return "var(--text-muted)";
}

export function PhaseBadge({ label, rating }: { label: string; rating: ThreatRating }) {
  const color = THREAT_STRIP_COLORS[rating];
  const bg = useMemo(() => {
    return rating === "DOMINANT" ? "rgba(34,197,94,0.12)"
         : rating === "THREAT" || rating === "WATCHFUL" ? "rgba(245,158,11,0.10)"
         : rating === "ADVANTAGE" ? "rgba(20,184,166,0.10)"
         : rating === "BUNNY" || rating === "DOMINATED" ? "rgba(239,68,68,0.10)"
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

      <div className="[display:flex]">
        <div style={visualProps.strip} className="[width:8px] [flex-shrink:0]" />

        <div className="[flex:1] [padding:10px_12px] [display:flex] [align-items:center] [justify-content:space-between] [gap:12px] [min-height:64px]">

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

          <div className="[display:flex] [flex-direction:column] [gap:2px] [flex:1] [min-width:0]">
            <span className="[font-size:0.8rem] [color:var(--text-secondary)] [white-space:nowrap]">
              AVG <span className="font-numeric [color:var(--text-primary)] [font-weight:600]">{avg}</span>
              <span className="[margin:0_6px] [color:var(--text-disabled)]">·</span>
              SR <span className="font-numeric [color:var(--text-primary)] [font-weight:600]">{sr}</span>
              <span className="[margin:0_6px] [color:var(--text-disabled)]">·</span>
              <span className="font-numeric [color:var(--text-secondary)]">{balls} balls</span>
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
