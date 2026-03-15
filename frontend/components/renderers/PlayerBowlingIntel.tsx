"use client";

import type { ReactNode } from "react";
import {
    type DataRow,
    PHASE_LABELS,
    PHASE_ORDER,
    type SectionTone,
    barWidth,
    buildIntelHeaderMsg,
    labelText,
    metricText,
    numericValue,
    rowValue,
    toneBarClass,
} from "@/lib/player-intel";

const BOWL_METRIC_COLUMNS = [
    { heading: "Wkts", key: "wickets" },
    { heading: "Econ", key: "economy" },
    { heading: "Avg", key: "average" },
    { heading: "SR", key: "strike_rate" },
] as const;

function last10BowlingChipClass(wickets: number | null): string {
    if (wickets === null) return "[background:var(--bg-active)] [color:var(--text-disabled)] [border:1px_solid_var(--border-subtle)] [opacity:0.5]";
    if (wickets >= 3) return "[background:var(--bg-active)] [color:var(--tier-elite)] [border:1px_solid_var(--tier-elite)]";
    if (wickets >= 1) return "[background:var(--bg-active)] [color:var(--tier-caution)] [border:1px_solid_var(--tier-caution)]";
    return "[background:var(--bg-active)] [color:var(--text-muted)] [border:1px_solid_var(--border-subtle)]";
}

function IntelSection({ title, tone, children }: { title: string; tone: SectionTone; children: ReactNode }): ReactNode {
    return <div><div className="[display:flex] [align-items:center] [gap:8px] [margin-bottom:12px]"><div className={`[width:4px] [height:16px] [border-radius:2px] ${toneBarClass(tone)}`} /><span className="[font-size:0.72rem] [font-weight:700] [color:var(--text-secondary)] [text-transform:uppercase] [letter-spacing:0.08em]">{title}</span></div>{children}</div>;
}

function IntelBar({ label, value, width, barClass }: { label: string; value: string; width: string; barClass: string }): ReactNode {
    return (
        <div className="[display:grid] [grid-template-columns:32px_minmax(0,_1fr)_44px] [align-items:center] [gap:8px]">
            <span className="[font-size:0.68rem] [font-weight:700] [color:var(--text-muted)]">{label}</span>
            <div className="[height:8px] [overflow:hidden] [border-radius:9999px] [background:var(--bg-active)]"><div className={`${barClass} [height:100%] [border-radius:9999px] [transition:width_var(--transition-normal)]`} style={{ width }} /></div>
            <span className="[font-size:0.72rem] [text-align:right] [color:var(--text-primary)] font-numeric">{value}</span>
        </div>
    );
}

export default function PlayerBowlingIntel({ data }: { data: Record<string, unknown> }) {
    const name = String(data["player_name"] ?? data["name"] ?? data["Player"] ?? "Unknown");
    const venueLabel = String(data["_venue_label"] ?? "");
    const yearsInput = String(data["_years_input"] ?? "");
    const intelHeaderMsg = buildIntelHeaderMsg(name, venueLabel, yearsInput);
    const phaseBowling = Array.isArray(data["phase_bowling"]) ? data["phase_bowling"].filter((row): row is DataRow => typeof row === "object" && row !== null && !Array.isArray(row)) : [];
    const last10Bowling = Array.isArray(data["last_10_bowling"]) ? data["last_10_bowling"].map((value) => numericValue(typeof value === "string" || typeof value === "number" || value === null ? value : undefined)) : [];
    const orderedPhaseBowling = PHASE_ORDER.map((phase) => phaseBowling.find((row) => labelText(rowValue(row, "phase")).toLowerCase() === phase)).filter((row): row is DataRow => row !== undefined);
    const maxDotPct = orderedPhaseBowling.reduce((highest, row) => Math.max(highest, numericValue(rowValue(row, "dot_pct")) ?? 0), 1);
    const maxBoundaryPct = orderedPhaseBowling.reduce((highest, row) => Math.max(highest, numericValue(rowValue(row, "boundary_pct")) ?? 0), 1);

    return (
        <div className="[display:flex] [flex-direction:column] [gap:20px]">
            <div className="[font-size:0.9rem] [font-weight:600] [color:var(--text-secondary)] [padding:4px_0]">{intelHeaderMsg}</div>
            <div className="glass-card animate-fade-in [display:flex] [flex-direction:column] [gap:24px] [padding:20px] [border:1px_solid_var(--border-subtle)]">
                {last10Bowling.length > 0 && <IntelSection title="Last 10 (Wickets)" tone="primary"><div className="[display:flex] [flex-wrap:wrap] [gap:6px]">{last10Bowling.map((wickets, index) => <span key={`${wickets === null ? "dnb" : wickets}-${index}`} className={`${last10BowlingChipClass(wickets)} [min-width:28px] [padding:3px_8px] [border-radius:9999px] [font-size:0.72rem] [font-weight:700] [text-align:center] font-numeric`}>{wickets === null ? "–" : metricText(wickets)}</span>)}</div></IntelSection>}
                {orderedPhaseBowling.length > 0 && (
                    <div>
                        <IntelSection title="Phase Bowling" tone="primary"><div /></IntelSection>
                        <div className="[overflow-x:auto]">
                            <table className="[width:100%] [border-collapse:collapse] [font-size:0.82rem]">
                                <thead><tr className="[border-bottom:1px_solid_var(--border-subtle)]"><th className="[padding:0_10px_8px_10px] [text-align:left] [font-size:0.68rem] [font-weight:700] [letter-spacing:0.08em] [text-transform:uppercase] [color:var(--text-muted)]">Phase</th>{BOWL_METRIC_COLUMNS.map((column) => <th key={column.key} className="[padding:0_10px_8px_10px] [text-align:right] [font-size:0.68rem] [font-weight:700] [letter-spacing:0.08em] [text-transform:uppercase] [color:var(--text-muted)]">{column.heading}</th>)}</tr></thead>
                                <tbody>{orderedPhaseBowling.map((row) => <tr key={`bowl-${labelText(rowValue(row, "phase"))}`} className="[border-bottom:1px_solid_var(--border-subtle)] last:[border-bottom:none]"><td className="[padding:10px] [text-align:left] [font-weight:600] [color:var(--text-primary)]">{PHASE_LABELS[labelText(rowValue(row, "phase")).toLowerCase()] ?? labelText(rowValue(row, "phase"))}</td>{BOWL_METRIC_COLUMNS.map((column) => <td key={column.key} className="[padding:10px] [text-align:right] [color:var(--text-primary)] font-numeric">{metricText(rowValue(row, column.key))}</td>)}</tr>)}</tbody>
                            </table>
                        </div>
                    </div>
                )}
                {orderedPhaseBowling.length > 0 && (
                    <IntelSection title="Pressure Metrics" tone="secondary">
                        <div className="[display:flex] [flex-wrap:wrap] [gap:14px] [margin-bottom:12px] [font-size:0.7rem] [color:var(--text-muted)]">
                            <span className="[display:inline-flex] [align-items:center] [gap:6px]"><span className="[display:inline-block] [width:10px] [height:10px] [border-radius:9999px] [background:var(--accent-primary)]" />Dot %</span>
                            <span className="[display:inline-flex] [align-items:center] [gap:6px]"><span className="[display:inline-block] [width:10px] [height:10px] [border-radius:9999px] [background:var(--tier-danger)]" />Boundary %</span>
                        </div>
                        <div className="[display:flex] [flex-direction:column] [gap:12px]">
                            {orderedPhaseBowling.map((row) => <div key={`pressure-${labelText(rowValue(row, "phase"))}`} className="[display:flex] [flex-direction:column] [gap:6px]"><div className="[font-size:0.74rem] [font-weight:600] [color:var(--text-secondary)]">{PHASE_LABELS[labelText(rowValue(row, "phase")).toLowerCase()] ?? labelText(rowValue(row, "phase"))}</div><IntelBar label="Dot" value={`${metricText(rowValue(row, "dot_pct"))}%`} width={barWidth(numericValue(rowValue(row, "dot_pct")), maxDotPct)} barClass="[background:var(--accent-primary)]" /><IntelBar label="Bdry" value={`${metricText(rowValue(row, "boundary_pct"))}%`} width={barWidth(numericValue(rowValue(row, "boundary_pct")), maxBoundaryPct)} barClass="[background:var(--tier-danger)]" /></div>)}
                        </div>
                    </IntelSection>
                )}
            </div>
        </div>
    );
}
