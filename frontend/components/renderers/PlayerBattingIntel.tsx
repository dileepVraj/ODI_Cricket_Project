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

const METRIC_COLUMNS = [
    { heading: "Runs", key: "total_runs" },
    { heading: "Avg", key: "avg_runs" },
    { heading: "SR", key: "strike_rate" },
    { heading: "Dismissals", key: "dismissals" },
] as const;

function last10ChipClass(score: number | null): string {
    if (score === null) return "[background:var(--bg-active)] [color:var(--text-disabled)] [border:1px_solid_var(--border-subtle)] [opacity:0.5]";
    if (score >= 50) return "[background:var(--bg-active)] [color:var(--tier-elite)] [border:1px_solid_var(--tier-elite)]";
    if (score >= 20) return "[background:var(--bg-active)] [color:var(--tier-caution)] [border:1px_solid_var(--tier-caution)]";
    return "[background:var(--bg-active)] [color:var(--text-muted)] [border:1px_solid_var(--border-subtle)]";
}

function IntelSection({ title, tone, children }: { title: string; tone: SectionTone; children: ReactNode }): ReactNode {
    return <div><div className="[display:flex] [align-items:center] [gap:8px] [margin-bottom:12px]"><div className={`[width:4px] [height:16px] [border-radius:2px] ${toneBarClass(tone)}`} /><span className="[font-size:0.72rem] [font-weight:700] [color:var(--text-secondary)] [text-transform:uppercase] [letter-spacing:0.08em]">{title}</span></div>{children}</div>;
}

function IntelTable({
    title,
    tone,
    labelHeading,
    rows,
    labelFor,
    hideTitle = false,
}: {
    title: string;
    tone: SectionTone;
    labelHeading: string;
    rows: DataRow[];
    labelFor: (row: DataRow) => string;
    hideTitle?: boolean;
}): ReactNode {
    return (
        <div>
            {!hideTitle && <IntelSection title={title} tone={tone}><div /></IntelSection>}
            <div className="[overflow-x:auto]">
                <table className="[width:100%] [border-collapse:collapse] [font-size:0.82rem]">
                    <thead><tr className="[border-bottom:1px_solid_var(--border-subtle)]"><th className="[padding:0_10px_8px_10px] [text-align:left] [font-size:0.68rem] [font-weight:700] [letter-spacing:0.08em] [text-transform:uppercase] [color:var(--text-muted)]">{labelHeading}</th>{METRIC_COLUMNS.map((column) => <th key={column.key} className="[padding:0_10px_8px_10px] [text-align:right] [font-size:0.68rem] [font-weight:700] [letter-spacing:0.08em] [text-transform:uppercase] [color:var(--text-muted)]">{column.heading}</th>)}</tr></thead>
                    <tbody>{rows.map((row) => <tr key={`${labelFor(row)}-${metricText(rowValue(row, "total_runs"))}`} className="[border-bottom:1px_solid_var(--border-subtle)] last:[border-bottom:none]"><td className="[padding:10px] [text-align:left] [font-weight:600] [color:var(--text-primary)]">{labelFor(row)}</td>{METRIC_COLUMNS.map((column) => <td key={column.key} className="[padding:10px] [text-align:right] [color:var(--text-primary)] font-numeric">{metricText(rowValue(row, column.key))}</td>)}</tr>)}</tbody>
                </table>
            </div>
        </div>
    );
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

export default function PlayerBattingIntel({ data }: { data: Record<string, unknown> }) {
    const name = String(data["player_name"] ?? data["name"] ?? data["Player"] ?? "Unknown");
    const venueLabel = String(data["_venue_label"] ?? "");
    const yearsInput = String(data["_years_input"] ?? "");
    const intelHeaderMsg = buildIntelHeaderMsg(name, venueLabel, yearsInput);
    const phaseRuns = Array.isArray(data["phase_runs"]) ? data["phase_runs"].filter((row): row is DataRow => typeof row === "object" && row !== null && !Array.isArray(row)) : [];
    const vsStyle = Array.isArray(data["vs_bowling_style"]) ? data["vs_bowling_style"].filter((row): row is DataRow => typeof row === "object" && row !== null && !Array.isArray(row)) : [];
    const last10 = Array.isArray(data["last_10_runs"]) ? data["last_10_runs"].map((value) => numericValue(typeof value === "string" || typeof value === "number" || value === null ? value : undefined)) : [];
    const orderedPhaseRuns = PHASE_ORDER.map((phase) => phaseRuns.find((row) => labelText(rowValue(row, "phase")).toLowerCase() === phase)).filter((row): row is DataRow => row !== undefined);
    const maxAvg = vsStyle.reduce((highest, row) => Math.max(highest, numericValue(rowValue(row, "avg_runs")) ?? 0), 1);
    const maxStrikeRate = vsStyle.reduce((highest, row) => Math.max(highest, numericValue(rowValue(row, "strike_rate")) ?? 0), 1);

    return (
        <div className="[display:flex] [flex-direction:column] [gap:20px]">
            <div className="[font-size:0.9rem] [font-weight:600] [color:var(--text-secondary)] [padding:4px_0]">{intelHeaderMsg}</div>
            <div className="glass-card animate-fade-in [display:flex] [flex-direction:column] [gap:24px] [padding:20px] [border:1px_solid_var(--border-subtle)]">
                {last10.length > 0 && <IntelSection title="Last 10" tone="primary"><div className="[display:flex] [flex-wrap:wrap] [gap:6px]">{last10.map((score, index) => <span key={`${score === null ? "dnb" : score}-${index}`} className={`${last10ChipClass(score)} [min-width:28px] [padding:3px_8px] [border-radius:9999px] [font-size:0.72rem] [font-weight:700] [text-align:center] font-numeric`}>{score === null ? "–" : metricText(score)}</span>)}</div></IntelSection>}
                {orderedPhaseRuns.length > 0 && <IntelTable title="Phase Runs" tone="primary" labelHeading="Phase" rows={orderedPhaseRuns} labelFor={(row) => PHASE_LABELS[labelText(rowValue(row, "phase")).toLowerCase()] ?? labelText(rowValue(row, "phase"))} />}
                {vsStyle.length > 0 && (
                    <IntelSection title="Vs Bowling Style" tone="secondary">
                        <IntelTable title="" tone="secondary" labelHeading="Style" rows={vsStyle} labelFor={(row) => labelText(rowValue(row, "style"))} hideTitle />
                        <div className="[display:flex] [flex-direction:column] [gap:12px]">
                            <div className="[display:flex] [flex-wrap:wrap] [gap:14px] [font-size:0.7rem] [color:var(--text-muted)]">
                                <span className="[display:inline-flex] [align-items:center] [gap:6px]"><span className="[display:inline-block] [width:10px] [height:10px] [border-radius:9999px] [background:var(--accent-primary)]" />Avg</span>
                                <span className="[display:inline-flex] [align-items:center] [gap:6px]"><span className="[display:inline-block] [width:10px] [height:10px] [border-radius:9999px] [background:var(--tier-caution)]" />SR</span>
                            </div>
                            {vsStyle.map((row) => <div key={`${labelText(rowValue(row, "style"))}-chart`} className="[display:flex] [flex-direction:column] [gap:6px]"><div className="[font-size:0.74rem] [font-weight:600] [color:var(--text-secondary)]">{labelText(rowValue(row, "style"))}</div><IntelBar label="Avg" value={metricText(rowValue(row, "avg_runs"))} width={barWidth(numericValue(rowValue(row, "avg_runs")), maxAvg)} barClass="[background:var(--accent-primary)]" /><IntelBar label="SR" value={metricText(rowValue(row, "strike_rate"))} width={barWidth(numericValue(rowValue(row, "strike_rate")), maxStrikeRate)} barClass="[background:var(--tier-caution)]" /></div>)}
                        </div>
                    </IntelSection>
                )}
            </div>
        </div>
    );
}
