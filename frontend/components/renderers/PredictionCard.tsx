"use client";

import { Gauge, Info, TrendingDown, TrendingUp } from "lucide-react";

interface PredictionCardProps {
    data: Record<string, unknown>;
}

type Tone = "tertiary" | "elite" | "danger";

function toneClasses(tone: Tone): { chip: string; icon: string } {
    if (tone === "tertiary") {
        return {
            chip: "[background:var(--accent-tertiary)]/15",
            icon: "[color:var(--accent-tertiary)]",
        };
    }
    if (tone === "elite") {
        return {
            chip: "[background:var(--tier-elite)]/15",
            icon: "[color:var(--tier-elite)]",
        };
    }
    return {
        chip: "[background:var(--tier-danger)]/15",
        icon: "[color:var(--tier-danger)]",
    };
}

export default function PredictionCard({ data }: PredictionCardProps) {
    if (!data || typeof data !== "object") {
        return (
            <div className="[padding:20px] [text-align:center] [color:var(--text-muted)]">
                No prediction data available.
            </div>
        );
    }

    const predicted = Number(data["Predicted_Total"] ?? data["predicted_total"] ?? 0);
    const rangeLow = Number(data["Range_Low"] ?? data["range_low"] ?? predicted - 15);
    const rangeHigh = Number(data["Range_High"] ?? data["range_high"] ?? predicted + 15);
    const venuePar = Number(data["Venue_Par"] ?? data["venue_par"] ?? 0);
    const venueAdjusted = Number(data["Venue_Adjusted_Par"] ?? data["venue_adjusted_par"] ?? venuePar);
    const batStrength = data["Batting_Strength"] ?? data["batting_strength"] ?? "-";
    const bowlThreat = data["Bowling_Threat"] ?? data["bowling_threat"] ?? "-";
    const batTeam = String(data["batting_team"] ?? "Batting Team");
    const bowlTeam = String(data["bowling_team"] ?? "Bowling Team");
    const venue = String(data["venue"] ?? data["venue_id"] ?? "");
    const notes = (data["Adjustment_Notes"] ?? data["adjustment_notes"] ?? data["adjustment_msg"] ?? []) as string[];
    const gauge = (data["gauge_positions"] ?? {}) as Record<string, unknown>;
    const aboveParText = String(data["above_par_text"] ?? "At par");
    const aboveParTone = String(data["above_par_tone"] ?? "muted");
    const parMarkerLeft = `${Number(gauge["par_marker_pct"] ?? 50)}%`;
    const rangeLeft = `${Number(gauge["range_left_pct"] ?? 50)}%`;
    const rangeWidth = `${Number(gauge["range_width_pct"] ?? 0)}%`;
    const predictedLeft = `${Number(gauge["predicted_pct"] ?? 50)}%`;
    const gaugeMin = Number(gauge["min_score"] ?? 150);
    const gaugeMax = Number(gauge["max_score"] ?? 350);

    return (
        <div className="[display:flex] [flex-direction:column] [gap:20px]">
            <div className="glass-card [padding:28px_24px] [border:1px_solid_var(--border-accent)] [position:relative] [overflow:hidden]">
                <div className="[position:absolute] [top:-50%] [left:50%] [transform:translateX(-50%)] [width:300px] [height:300px] [border-radius:50%] [background:radial-gradient(circle,_var(--accent-glow)_0%,_transparent_70%)] [pointer-events:none] [opacity:0.6]" />

                <div className="[position:relative]">
                    <div className="[font-size:0.7rem] [text-transform:uppercase] [letter-spacing:0.08em] [color:var(--text-disabled)] [font-weight:600] [margin-bottom:8px]">
                        Predicted 1st Innings Total
                    </div>
                    <div className="[font-size:3.2rem] [font-weight:900] [background:linear-gradient(135deg,_var(--accent-primary),_var(--accent-secondary))] [-webkit-background-clip:text] [-webkit-text-fill-color:transparent] [line-height:1] [margin-bottom:8px] [font-variant-numeric:tabular-nums]">
                        {predicted}
                    </div>
                    <div className="[font-size:0.9rem] [color:var(--text-muted)] [font-weight:500]">
                        Range: <span className="[font-weight:700] [color:var(--text-primary)]">{rangeLow}</span>
                        {" - "}
                        <span className="[font-weight:700] [color:var(--text-primary)]">{rangeHigh}</span>
                    </div>

                    <div className="[margin-top:12px] [font-size:0.8rem] [color:var(--text-muted)] [display:flex] [justify-content:center] [gap:16px] [flex-wrap:wrap]">
                        <span>
                            <strong className="[color:var(--text-primary)]">{batTeam}</strong> batting
                        </span>
                        <span>
                            vs <strong className="[color:var(--text-primary)]">{bowlTeam}</strong>
                        </span>
                        {venue && (
                            <span>
                                at <strong>{venue}</strong>
                            </span>
                        )}
                    </div>
                </div>
            </div>

            <div className="[background:var(--bg-elevated)] [border-radius:var(--radius-lg)] [padding:16px_20px] [border:1px_solid_var(--border-subtle)]">
                <div className="[display:flex] [justify-content:space-between] [margin-bottom:8px] [font-size:0.75rem] [color:var(--text-muted)] [font-weight:500]">
                    <span>{gaugeMin}</span>
                    <span className={`${aboveParToneClass(aboveParTone)} [font-weight:700]`}>
                        {aboveParText}
                    </span>
                    <span>{gaugeMax}</span>
                </div>

                <div className="[position:relative] [height:10px] [border-radius:5px] [background:var(--bg-active)]">
                    <div className="[position:absolute] [top:-4px] [width:2px] [height:18px] [background:var(--text-disabled)] [border-radius:1px]" style={{ left: parMarkerLeft }} />
                    <div className="[position:absolute] [height:100%] [background:linear-gradient(90deg,_var(--accent-primary),_var(--accent-secondary))] [border-radius:5px] [opacity:0.6]" style={{ left: rangeLeft, width: rangeWidth }} />
                    <div className="[position:absolute] [top:-3px] [width:16px] [height:16px] [border-radius:50%] [background:var(--accent-primary)] [border:3px_solid_var(--bg-base)] [transform:translateX(-50%)] [box-shadow:0_0_8px_var(--accent-primary)]" style={{ left: predictedLeft }} />
                </div>

                <div className="[display:flex] [justify-content:space-between] [margin-top:6px] [font-size:0.68rem] [color:var(--text-disabled)]">
                    <span>Low Scoring</span>
                    <span>Venue Par: {venuePar}</span>
                    <span>High Scoring</span>
                </div>
            </div>

            <div className="[display:grid] [grid-template-columns:repeat(auto-fill,_minmax(200px,_1fr))] [gap:12px]">
                <BreakdownCard
                    icon={<Gauge size={18} />}
                    label="Venue Par"
                    value={String(venuePar)}
                    subLabel={`Adjusted: ${venueAdjusted}`}
                    tone="tertiary"
                />
                <BreakdownCard
                    icon={<TrendingUp size={18} />}
                    label="Batting Strength"
                    value={String(batStrength)}
                    subLabel={batTeam}
                    tone="elite"
                />
                <BreakdownCard
                    icon={<TrendingDown size={18} />}
                    label="Bowling Threat"
                    value={String(bowlThreat)}
                    subLabel={bowlTeam}
                    tone="danger"
                />
            </div>

            {Array.isArray(notes) && notes.length > 0 && (
                <div className="[background:var(--bg-elevated)] [border-radius:var(--radius-md)] [padding:14px_18px] [border:1px_solid_var(--border-subtle)]">
                    <div className="[display:flex] [align-items:center] [gap:6px] [margin-bottom:10px] [font-size:0.78rem] [font-weight:600] [color:var(--text-secondary)]">
                        <Info size={14} />
                        Adjustment Notes
                    </div>
                    <ul className="[margin:0px] [padding-left:18px]">
                        {notes.map((note, i) => (
                            <li key={i} className="[font-size:0.8rem] [color:var(--text-muted)] [line-height:1.6]">
                                {note}
                            </li>
                        ))}
                    </ul>
                </div>
            )}
        </div>
    );
}

function aboveParToneClass(tone: string): string {
    if (tone === "elite") return "[color:var(--tier-elite)]";
    if (tone === "caution") return "[color:var(--tier-caution)]";
    if (tone === "danger") return "[color:var(--tier-danger)]";
    return "[color:var(--text-muted)]";
}

function BreakdownCard({
    icon,
    label,
    value,
    subLabel,
    tone,
}: {
    icon: React.ReactNode;
    label: string;
    value: string;
    subLabel: string;
    tone: Tone;
}) {
    const toneClass = toneClasses(tone);
    return (
        <div className="[padding:16px] [background:var(--bg-elevated)] [border-radius:var(--radius-md)] [border:1px_solid_var(--border-subtle)]">
            <div className="[display:flex] [align-items:center] [gap:8px] [margin-bottom:8px]">
                <div className={`[width:32px] [height:32px] [border-radius:var(--radius-sm)] [display:flex] [align-items:center] [justify-content:center] ${toneClass.chip} ${toneClass.icon}`}>
                    {icon}
                </div>
                <span className="[font-size:0.75rem] [font-weight:600] [color:var(--text-muted)] [text-transform:uppercase] [letter-spacing:0.04em]">
                    {label}
                </span>
            </div>
            <div className="[font-size:1.3rem] [font-weight:800] [color:var(--text-primary)] [font-variant-numeric:tabular-nums]">{value}</div>
            <div className="[font-size:0.72rem] [color:var(--text-disabled)] [margin-top:2px]">{subLabel}</div>
        </div>
    );
}
