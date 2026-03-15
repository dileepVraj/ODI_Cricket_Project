"use client";
import { useState, type ReactNode } from "react";
import { Award, ChevronDown, ChevronUp, Target, User } from "lucide-react";
import EmptyState from "@/components/common/EmptyState";
import QuickLinks from "@/components/layout/QuickLinks";
import { useAppContext } from "@/lib/context";
import type { QuickLink } from "@/lib/api";
import { PlayerPayloadFragment, toPlayerPayloadFragment } from "@/lib/types";

interface PlayerProfileCardProps { data: Record<string, unknown>; }
type SectionTone = "primary" | "secondary" | "tertiary";
type Scalar = string | number | null | undefined;
type DataRow = Record<string, unknown>;

const PHASE_LABELS: Record<string, string> = { pp: "Powerplay", mid: "Middle", dth: "Death Overs" };
const PHASE_ORDER = ["pp", "mid", "dth"] as const;
const BAT_KEYS = ["innings", "runs", "average", "strike_rate", "hundreds", "fifties", "highest_score", "not_outs", "balls_faced", "fours", "sixes", "Innings", "Runs", "Average", "SR", "100s", "50s", "HS", "NO"];
const BOWL_KEYS = ["wickets", "bowling_avg", "economy", "bowling_sr", "best_bowling", "overs", "maiden", "Wickets", "Bowl_Avg", "Econ", "Bowl_SR", "Best"];
const METRIC_COLUMNS = [
    { heading: "Runs", key: "total_runs" },
    { heading: "Avg", key: "avg_runs" },
    { heading: "SR", key: "strike_rate" },
    { heading: "Dismissals", key: "dismissals" },
] as const;

function toneBarClass(tone: SectionTone): string {
    if (tone === "primary") return "[background:var(--accent-primary)]";
    if (tone === "secondary") return "[background:var(--accent-secondary)]";
    return "[background:var(--accent-tertiary)]";
}

function rowValue(row: DataRow, key: string): Scalar {
    const value = row[key];
    return typeof value === "string" || typeof value === "number" || value === null || value === undefined ? value : undefined;
}

function numericValue(value: Scalar): number | null {
    if (typeof value === "number") return Number.isFinite(value) ? value : null;
    if (typeof value !== "string") return value === null ? null : null;
    const trimmed = value.trim();
    if (trimmed === "") return null;
    const parsed = Number(trimmed);
    return Number.isFinite(parsed) ? parsed : null;
}

function metricText(value: Scalar): string {
    const numeric = numericValue(value);
    if (numeric === null) return "–";
    return Number.isInteger(numeric) ? String(numeric) : numeric.toFixed(1);
}

function labelText(value: Scalar): string {
    if (value === null || value === undefined) return "";
    return String(value).trim();
}

function last10ChipClass(score: number | null): string {
    if (score === null) return "[background:var(--bg-active)] [color:var(--text-disabled)] [border:1px_solid_var(--border-subtle)] [opacity:0.5]";
    if (score >= 50) return "[background:var(--bg-active)] [color:var(--tier-elite)] [border:1px_solid_var(--tier-elite)]";
    if (score >= 20) return "[background:var(--bg-active)] [color:var(--tier-caution)] [border:1px_solid_var(--tier-caution)]";
    return "[background:var(--bg-active)] [color:var(--text-muted)] [border:1px_solid_var(--border-subtle)]";
}

export default function PlayerProfileCard({ data }: PlayerProfileCardProps) {
    const { activeFormat, manifest } = useAppContext();
    const [intelOpen, setIntelOpen] = useState(false);
    const playerScoutLinks: QuickLink[] = !manifest ? [] : manifest.categories.find((c) => c.key === "player_scout")?.quick_links ?? [];
    if (!data || typeof data !== "object") return <EmptyState message="No player data available." />;

    const name = String(data["player_name"] ?? data["name"] ?? data["Player"] ?? "Unknown");
    const team = String(data["team"] ?? data["Team"] ?? "");
    const role = String(data["role"] ?? data["Role"] ?? "");
    const view = String(data["_view"] ?? "");
    const venueLabel = String(data["_venue_label"] ?? "");
    const yearsInput = String(data["_years_input"] ?? "");
    let intelHeaderMsg: string;
    if (venueLabel && yearsInput) {
        intelHeaderMsg = `${name} at ${venueLabel} - Last ${yearsInput} Years`;
    } else if (venueLabel) {
        intelHeaderMsg = `${name} at ${venueLabel} - All Time`;
    } else if (yearsInput) {
        intelHeaderMsg = `${name} - Last ${yearsInput} Years`;
    } else {
        intelHeaderMsg = `${name} - Overall`;
    }
    const battingObj = toPlayerPayloadFragment(data["batting"]);
    const bowlingObj = toPlayerPayloadFragment(data["bowling"]);
    const venueCtx = toPlayerPayloadFragment(data["venue_stats"]);
    const opponentCtx = toPlayerPayloadFragment(data["vs_opponent_stats"]);
    const phaseRuns = Array.isArray(data["phase_runs"]) ? data["phase_runs"].filter((row): row is DataRow => typeof row === "object" && row !== null && !Array.isArray(row)) : [];
    const vsStyle = Array.isArray(data["vs_bowling_style"]) ? data["vs_bowling_style"].filter((row): row is DataRow => typeof row === "object" && row !== null && !Array.isArray(row)) : [];
    const last10 = Array.isArray(data["last_10_runs"]) ? data["last_10_runs"].map((value) => numericValue(typeof value === "string" || typeof value === "number" || value === null ? value : undefined)) : [];
    const pickStats = (obj: PlayerPayloadFragment | null, keys: string[]): [string, unknown][] => !obj ? [] : keys.filter((key) => key in obj).map((key) => [key, obj[key]]);
    const contextToStats = (ctx: PlayerPayloadFragment | null): [string, unknown][] => {
        if (!ctx) return [];
        const batting = toPlayerPayloadFragment(ctx["batting"]);
        const bowling = toPlayerPayloadFragment(ctx["bowling"]);
        return [...pickStats(batting, ["innings", "runs", "average", "strike_rate", "highest_score", "centuries", "fifties"]), ...pickStats(bowling, ["innings", "wickets", "average", "economy", "best_figures"])];
    };
    const displayEntries = Object.entries(data).filter(([key]) => !["player_name", "name", "Player", "team", "Team", "role", "Role", "MATCH_IDS", "raw_matches", "_view", "_venue_label", "_years_input"].includes(key) && typeof data[key] !== "object");
    const battingStatsNested = pickStats(battingObj, ["innings", "runs", "average", "strike_rate", "centuries", "fifties", "highest_score"]);
    const bowlingStatsNested = pickStats(bowlingObj, ["innings", "wickets", "average", "economy", "best_figures"]);
    const battingStats = battingStatsNested.length > 0 ? battingStatsNested : displayEntries.filter(([key]) => BAT_KEYS.some((batKey) => key.toLowerCase().includes(batKey.toLowerCase())));
    const bowlingStats = bowlingStatsNested.length > 0 ? bowlingStatsNested : displayEntries.filter(([key]) => BOWL_KEYS.some((bowlKey) => key.toLowerCase().includes(bowlKey.toLowerCase())));
    const otherStats = displayEntries.filter(([key]) => !BAT_KEYS.some((batKey) => key.toLowerCase().includes(batKey.toLowerCase())) && !BOWL_KEYS.some((bowlKey) => key.toLowerCase().includes(bowlKey.toLowerCase())));
    const opponentStats = contextToStats(opponentCtx);
    const venueStats = contextToStats(venueCtx);
    const hasIntel = phaseRuns.length > 0 || vsStyle.length > 0 || last10.length > 0;

    return (
        <div className="[display:flex] [flex-direction:column] [gap:20px]">
            <div className="glass-card [padding:24px] [display:flex] [align-items:center] [gap:20px] [border:1px_solid_var(--border-accent)]">
                <div className="[width:56px] [height:56px] [border-radius:50%] [background:linear-gradient(135deg,_var(--accent-primary),_var(--accent-secondary))] [display:flex] [align-items:center] [justify-content:center] [flex-shrink:0]"><User size={28} className="[color:var(--text-primary)]" /></div>
                <div className="[flex:1]">
                    <h3 className="[font-size:1.3rem] [font-weight:800] [color:var(--text-primary)] [margin-bottom:4px]">{name}</h3>
                    <div className="[display:flex] [gap:8px] [align-items:center] [flex-wrap:wrap]">
                        {team && <span className="badge badge-strong [font-size:0.7rem]">{team}</span>}
                        {role && <span className="[padding:2px_10px] [border-radius:9999px] [background:var(--bg-active)] [color:var(--text-muted)] [font-size:0.7rem] [font-weight:500]">{role}</span>}
                    </div>
                </div>
            </div>
            {view === "batting_intel" && (
                <>
                    <div className="[font-size:0.9rem] [font-weight:600] [color:var(--text-secondary)] [padding:4px_0]">
                        {intelHeaderMsg}
                    </div>
                    <BattingIntelPanel last10={last10} phaseRuns={phaseRuns} vsStyle={vsStyle} />
                </>
            )}
            {view !== "batting_intel" && (
                <>
                    {battingStats.length > 0 && <StatSection title="Batting" icon={<Award size={14} />} stats={battingStats} tone="primary" />}
                    {bowlingStats.length > 0 && <StatSection title="Bowling" icon={<Target size={14} />} stats={bowlingStats} tone="secondary" />}
                    {opponentStats.length > 0 && <StatSection title="Vs Opponent" icon={<Target size={14} />} stats={opponentStats} tone="tertiary" />}
                    {venueStats.length > 0 && <StatSection title="At Venue" icon={<Award size={14} />} stats={venueStats} tone="tertiary" />}
                    {otherStats.length > 0 && <StatSection title="Details" icon={<User size={14} />} stats={otherStats} tone="tertiary" />}
                </>
            )}
            {view === "" && hasIntel && (
                <>
                    <button
                        className="btn-ghost [display:flex] [align-items:center] [justify-content:center] [gap:6px] [width:100%] [margin-top:4px] [font-size:0.82rem] [font-weight:600] [color:var(--accent-primary)]"
                        aria-label="Toggle batting intel"
                        onClick={() => setIntelOpen((value) => !value)}
                    >
                        {intelOpen ? <ChevronUp size={14} /> : <ChevronDown size={14} />}{intelOpen ? "Hide Intel" : "Batting Intel"}
                    </button>
                    {intelOpen && <BattingIntelPanel last10={last10} phaseRuns={phaseRuns} vsStyle={vsStyle} />}
                </>
            )}
            {activeFormat && playerScoutLinks.length > 0 && <QuickLinks links={playerScoutLinks} />}
        </div>
    );
}

function StatSection({ title, icon, stats, tone }: { title: string; icon: ReactNode; stats: [string, unknown][]; tone: SectionTone; }) {
    return (
        <div>
            <div className="[display:flex] [align-items:center] [gap:8px] [margin-bottom:10px]">
                <div className={`[width:4px] [height:16px] [border-radius:2px] ${toneBarClass(tone)}`} />
                <span className="[font-size:0.78rem] [font-weight:700] [color:var(--text-secondary)] [text-transform:uppercase] [letter-spacing:0.06em] [display:inline-flex] [align-items:center] [gap:6px]">{icon} {title}</span>
            </div>
            <div className="[display:grid] [grid-template-columns:repeat(auto-fill,_minmax(140px,_1fr))] [gap:8px]">
                {stats.map(([key, value]) => (
                    <div key={key} className="[padding:12px_14px] [background:var(--bg-elevated)] [border-radius:var(--radius-md)] [border:1px_solid_var(--border-subtle)]">
                        <div className="[font-size:0.65rem] [text-transform:uppercase] [letter-spacing:0.05em] [color:var(--text-disabled)] [font-weight:600] [margin-bottom:3px]">{key.replace(/_/g, " ")}</div>
                        <div className="[font-size:1.1rem] [font-weight:700] [color:var(--text-primary)] font-numeric">{value === null || value === undefined ? "-" : String(value)}</div>
                    </div>
                ))}
            </div>
        </div>
    );
}

function BattingIntelPanel({ last10, phaseRuns, vsStyle }: { last10: Array<number | null>; phaseRuns: DataRow[]; vsStyle: DataRow[]; }) {
    const orderedPhaseRuns = PHASE_ORDER.map((phase) => phaseRuns.find((row) => labelText(rowValue(row, "phase")).toLowerCase() === phase)).filter((row): row is DataRow => row !== undefined);
    const maxAvg = vsStyle.reduce((highest, row) => Math.max(highest, numericValue(rowValue(row, "avg_runs")) ?? 0), 1);
    const maxStrikeRate = vsStyle.reduce((highest, row) => Math.max(highest, numericValue(rowValue(row, "strike_rate")) ?? 0), 1);
    return (
        <div className="glass-card animate-fade-in [display:flex] [flex-direction:column] [gap:24px] [padding:20px] [border:1px_solid_var(--border-subtle)]">
            {last10.length > 0 && (
                <IntelSection title="Last 10" tone="primary">
                    <div className="[display:flex] [flex-wrap:wrap] [gap:6px]">{last10.map((score, index) => <span key={`${score === null ? "dnb" : score}-${index}`} className={`${last10ChipClass(score)} [min-width:28px] [padding:3px_8px] [border-radius:9999px] [font-size:0.72rem] [font-weight:700] [text-align:center] font-numeric`}>{score === null ? "–" : metricText(score)}</span>)}</div>
                </IntelSection>
            )}
            {orderedPhaseRuns.length > 0 && <IntelTable title="Phase Runs" tone="primary" labelHeading="Phase" rows={orderedPhaseRuns} labelFor={(row) => PHASE_LABELS[labelText(rowValue(row, "phase")).toLowerCase()] ?? labelText(rowValue(row, "phase"))} />}
            {vsStyle.length > 0 && (
                <IntelSection title="Vs Bowling Style" tone="secondary">
                    <IntelTable title="" tone="secondary" labelHeading="Style" rows={vsStyle} labelFor={(row) => labelText(rowValue(row, "style"))} hideTitle />
                    <div className="[display:flex] [flex-direction:column] [gap:12px]">
                        <div className="[display:flex] [flex-wrap:wrap] [gap:14px] [font-size:0.7rem] [color:var(--text-muted)]">
                            <span className="[display:inline-flex] [align-items:center] [gap:6px]"><span className="[display:inline-block] [width:10px] [height:10px] [border-radius:9999px] [background:var(--accent-primary)]" />Avg</span>
                            <span className="[display:inline-flex] [align-items:center] [gap:6px]"><span className="[display:inline-block] [width:10px] [height:10px] [border-radius:9999px] [background:var(--tier-caution)]" />SR</span>
                        </div>
                        {vsStyle.map((row) => (
                            <div key={`${labelText(rowValue(row, "style"))}-chart`} className="[display:flex] [flex-direction:column] [gap:6px]">
                                <div className="[font-size:0.74rem] [font-weight:600] [color:var(--text-secondary)]">{labelText(rowValue(row, "style"))}</div>
                                <IntelBar label="Avg" value={metricText(rowValue(row, "avg_runs"))} width={barWidth(numericValue(rowValue(row, "avg_runs")), maxAvg)} barClass="[background:var(--accent-primary)]" />
                                <IntelBar label="SR" value={metricText(rowValue(row, "strike_rate"))} width={barWidth(numericValue(rowValue(row, "strike_rate")), maxStrikeRate)} barClass="[background:var(--tier-caution)]" />
                            </div>
                        ))}
                    </div>
                </IntelSection>
            )}
        </div>
    );
}

function IntelSection({ title, tone, children }: { title: string; tone: SectionTone; children: ReactNode; }) {
    return <div><div className="[display:flex] [align-items:center] [gap:8px] [margin-bottom:12px]"><div className={`[width:4px] [height:16px] [border-radius:2px] ${toneBarClass(tone)}`} /><span className="[font-size:0.72rem] [font-weight:700] [color:var(--text-secondary)] [text-transform:uppercase] [letter-spacing:0.08em]">{title}</span></div>{children}</div>;
}

function IntelTable({ title, tone, labelHeading, rows, labelFor, hideTitle = false }: { title: string; tone: SectionTone; labelHeading: string; rows: DataRow[]; labelFor: (row: DataRow) => string; hideTitle?: boolean; }) {
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

function barWidth(value: number | null, maxValue: number): string {
    if (value === null || maxValue <= 0) return "0%";
    return `${Math.min(100, Math.max(0, (value / maxValue) * 100))}%`;
}

function IntelBar({ label, value, width, barClass }: { label: string; value: string; width: string; barClass: string; }) {
    return (
        <div className="[display:grid] [grid-template-columns:32px_minmax(0,_1fr)_44px] [align-items:center] [gap:8px]">
            <span className="[font-size:0.68rem] [font-weight:700] [color:var(--text-muted)]">{label}</span>
            <div className="[height:8px] [overflow:hidden] [border-radius:9999px] [background:var(--bg-active)]"><div className={`${barClass} [height:100%] [border-radius:9999px] [transition:width_var(--transition-normal)]`} style={{ width }} /></div>
            <span className="[font-size:0.72rem] [text-align:right] [color:var(--text-primary)] font-numeric">{value}</span>
        </div>
    );
}
