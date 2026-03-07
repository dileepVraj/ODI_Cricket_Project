"use client";

import { Activity, BarChart3, Clock, Target, Zap } from "lucide-react";
import EmptyState from "@/components/common/EmptyState";
import MatchAuditSection from "./MatchAuditSection";

interface PhaseData {
    avg: number;
    n: number;
    wkts: number;
}

interface InningsStats {
    pp: PhaseData;
    mid: PhaseData;
    dth: PhaseData;
    total: PhaseData;
}

interface LegacyGlobalHabitsTeam {
    pp_rr: number;
    mid_rr: number;
    dth_rr: number;
    avg_score: number;
}

interface BatFirstHabits {
    home_team_pp_runs?: number;
    away_team_pp_runs?: number;
    home_team_pp_wkts?: number;
    away_team_pp_wkts?: number;
    home_team_mid_runs?: number;
    away_team_mid_runs?: number;
    home_team_mid_wkts?: number;
    away_team_mid_wkts?: number;
    home_team_dth_runs?: number;
    away_team_dth_runs?: number;
    home_team_dth_wkts?: number;
    away_team_dth_wkts?: number;
}

interface ChasingHabits {
    home_team_pp_runs?: number;
    away_team_pp_runs?: number;
    home_team_mid_wkts?: number;
    away_team_mid_wkts?: number;
    home_team_dth_wkts?: number;
    away_team_dth_wkts?: number;
}

interface ScenarioRow {
    label: string;
    home_value?: number;
    away_value?: number;
    higher_better?: boolean;
    diff_text?: string;
    diff_tone?: "success" | "danger" | "muted";
}

interface PhaseAnalysisData {
    stadium_id?: string;
    match_count?: number;
    years?: number;
    filter_criteria?: {
        min_first_innings_balls?: number;
        min_first_innings_overs?: number;
        keep_all_outs?: boolean;
        keep_successful_chases?: boolean;
        drop_short_no_result_only?: boolean;
    };
    baseline?: { "1"?: InningsStats; "2"?: InningsStats };
    home_at_venue?: { team: string; stats: { "1"?: InningsStats; "2"?: InningsStats } } | null;
    away_at_venue?: { team: string; stats: { "1"?: InningsStats; "2"?: InningsStats } } | null;
    global_habits?: {
        start_year?: number | string;
        bat_first?: BatFirstHabits;
        chasing?: ChasingHabits;
        scenario_rows?: {
            bat_first?: ScenarioRow[];
            chasing?: ScenarioRow[];
        };
        home?: LegacyGlobalHabitsTeam;
        away?: LegacyGlobalHabitsTeam;
    } | null;
    match_audit?: Record<string, unknown>[];
    MATCH_IDS?: string;
}

interface PhaseAnalysisCardProps {
    data: PhaseAnalysisData;
}

const baseThClass =
    "[padding:11px_14px] [border-bottom:1px_solid_var(--border-default)] [color:var(--text-muted)] [font-weight:600] [font-size:0.72rem] [letter-spacing:0.02em] [white-space:nowrap]";
const thClass = (align: "left" | "right") => `${baseThClass} ${align === "left" ? "[text-align:left]" : "[text-align:right]"}`;
const baseTdClass =
    "[padding:11px_14px] font-numeric [color:var(--text-primary)]";
const tdClass = (align: "left" | "right") =>
    `${baseTdClass} ${align === "left" ? "[text-align:left]" : "[text-align:right] [font-family:var(--font-numeric)]"}`;

function accentBarClass(accentColor: string): string {
    if (accentColor === "var(--accent-primary)") return "[background:var(--accent-primary)]";
    if (accentColor === "var(--accent-secondary)") return "[background:var(--accent-secondary)]";
    if (accentColor === "var(--accent-tertiary)") return "[background:var(--accent-tertiary)]";
    return "[background:var(--tier-strong)]";
}

export default function PhaseAnalysisCard({ data }: PhaseAnalysisCardProps) {
    if (!data || typeof data !== "object") {
        return <EmptyState message="No phase analysis data available." />;
    }

    const stadiumId = String(data.stadium_id ?? "Unknown");
    const stadiumLabel =
        stadiumId.split("_").slice(1).join(" ").replace(/\b\w/g, (c) => c.toUpperCase()) || stadiumId;
    const matchCount = data.match_count ?? 0;
    const years = data.years ?? 5;

    return (
        <div className="[display:flex] [flex-direction:column] [gap:20px]">
            <div className="glass-card [padding:18px_22px] [display:flex] [align-items:center] [gap:16px] [flex-wrap:wrap] [border-left:4px_solid_var(--accent-primary)]">
                <div className="[width:40px] [height:40px] [border-radius:var(--radius-md)] [background:var(--accent-glow)] [display:flex] [align-items:center] [justify-content:center]">
                    <Activity size={20} className="[color:var(--accent-primary)]" />
                </div>

                <div className="[flex:1]">
                    <div className="[font-size:0.7rem] [text-transform:uppercase] [letter-spacing:0.06em] [color:var(--text-disabled)] [font-weight:600]">
                        Phase Analysis
                    </div>
                    <div className="[font-size:1.1rem] [font-weight:800] [color:var(--text-primary)]">{stadiumLabel}</div>
                </div>

                <div className="[display:flex] [gap:20px]">
                    <StatPill label="Matches" value={String(matchCount)} />
                    <StatPill label="Period" value={`${years}yr`} />
                </div>
            </div>

            {data.filter_criteria && <FilterCriteriaNotice criteria={data.filter_criteria} />}

            {data.baseline && (
                <PhaseTable
                    title="Venue Baseline (All Teams)"
                    stats={data.baseline}
                    accentColor="var(--accent-tertiary)"
                />
            )}

            {data.home_at_venue?.stats && (
                <PhaseTable
                    title={`${data.home_at_venue.team} at this Venue`}
                    stats={data.home_at_venue.stats}
                    accentColor="var(--accent-primary)"
                />
            )}

            {data.away_at_venue?.stats && (
                <PhaseTable
                    title={`${data.away_at_venue.team} at this Venue`}
                    stats={data.away_at_venue.stats}
                    accentColor="var(--accent-secondary)"
                />
            )}

            {data.global_habits && (
                <GlobalHabitsCard
                    habits={data.global_habits}
                    homeTeam={data.home_at_venue?.team}
                    awayTeam={data.away_at_venue?.team}
                />
            )}

            {data.match_audit && <MatchAuditSection records={data.match_audit} />}
        </div>
    );
}

function FilterCriteriaNotice({
    criteria,
}: {
    criteria: NonNullable<PhaseAnalysisData["filter_criteria"]>;
}) {
    const overs = criteria.min_first_innings_overs ?? 45;
    const firstBalls = criteria.min_first_innings_balls ?? 270;
    const keepAllOuts = criteria.keep_all_outs !== false;
    const keepChases = criteria.keep_successful_chases !== false;
    const dropShortNoResultOnly = criteria.drop_short_no_result_only !== false;

    return (
        <div className="[background:var(--bg-elevated)] [border:1px_solid_var(--border-subtle)] [border-left:3px_solid_var(--warning)] [border-radius:var(--radius-md)] [padding:10px_12px]">
            <div className="[font-size:0.72rem] [font-weight:700] [letter-spacing:0.05em] [text-transform:uppercase] [color:var(--text-secondary)] [margin-bottom:4px]">
                Filter Criteria
            </div>
            <div className="[font-size:0.82rem] [color:var(--text-muted)] [line-height:1.5]">
                {`Baseline rule: 1st innings should be >= ${overs} overs (${firstBalls} balls). `}
                {keepAllOuts ? "All-out innings are retained even below 45 overs. " : ""}
                {keepChases ? "Successful chases are retained regardless of chase score. " : ""}
                {dropShortNoResultOnly ? "Only short no-result/abandoned anomalies are excluded." : ""}
            </div>
        </div>
    );
}

function StatPill({ label, value }: { label: string; value: string }) {
    return (
        <div className="[text-align:center] [min-width:50px]">
            <div className="[font-size:0.6rem] [text-transform:uppercase] [color:var(--text-disabled)] [font-weight:600]">{label}</div>
            <div className="[font-size:1rem] [font-weight:700] [color:var(--text-primary)] font-numeric">{value}</div>
        </div>
    );
}

function PhaseTable({
    title,
    stats,
    accentColor,
}: {
    title: string;
    stats: { "1"?: InningsStats; "2"?: InningsStats };
    accentColor: string;
}) {
    const inn1 = stats["1"];
    const inn2 = stats["2"];

    const phases = [
        { key: "pp", label: "Powerplay (1-10)", icon: <Zap size={14} /> },
        { key: "mid", label: "Middle (11-40)", icon: <Clock size={14} /> },
        { key: "dth", label: "Death (41-50)", icon: <Target size={14} /> },
        { key: "total", label: "Total", icon: <BarChart3 size={14} /> },
    ] as const;

    return (
        <div>
            <div className="[display:flex] [align-items:center] [gap:10px] [margin-bottom:10px]">
                <div className={`[width:4px] [height:20px] [border-radius:2px] ${accentBarClass(accentColor)}`} />
                <h4 className="[font-size:0.8rem] [font-weight:700] [color:var(--text-secondary)] [text-transform:uppercase] [letter-spacing:0.06em]">
                    {title}
                </h4>
            </div>

            <div className="[background:var(--bg-elevated)] [border-radius:var(--radius-md)] [border:1px_solid_var(--border-subtle)] [overflow:hidden] [box-shadow:0_8px_22px_rgba(2,_8,_23,_0.2)]">
                <table className="[width:100%] [border-collapse:collapse] [font-size:0.84rem]">
                    <thead>
                        <tr>
                            <th className={thClass("left")}>Phase</th>
                            <th className={thClass("right")}>1st Inn Avg</th>
                            <th className={thClass("right")}>1st Inn Wkts</th>
                            <th className={thClass("right")}>2nd Inn Avg</th>
                            <th className={thClass("right")}>2nd Inn Wkts</th>
                            <th className={thClass("right")}>Matches</th>
                        </tr>
                    </thead>
                    <tbody>
                        {phases.map((phase, i) => {
                            const d1 = inn1?.[phase.key];
                            const d2 = inn2?.[phase.key];
                            const isTotal = phase.key === "total";
                            return (
                                <tr
                                    key={phase.key}
                                    className={`[transition:background-color_0.2s] ${i < phases.length - 1 ? "[border-bottom:1px_solid_var(--border-subtle)]" : ""} ${isTotal ? "[font-weight:700] [background:var(--bg-active)]" : "[font-weight:500] hover:[background:var(--bg-hover)]"}`}
                                >
                                    <td className={`${tdClass("left")} [font-weight:600]`}>
                                        <span className="[display:inline-flex] [align-items:center] [gap:6px]">
                                            {phase.icon} {phase.label}
                                        </span>
                                    </td>
                                    <td className={tdClass("right")}>{fmtNum(d1?.avg)}</td>
                                    <td className={tdClass("right")}>{isTotal ? "-" : fmtNum(d1?.wkts)}</td>
                                    <td className={tdClass("right")}>{fmtNum(d2?.avg)}</td>
                                    <td className={tdClass("right")}>{isTotal ? "-" : fmtNum(d2?.wkts)}</td>
                                    <td className={tdClass("right")}>{d1?.n ?? d2?.n ?? "-"}</td>
                                </tr>
                            );
                        })}
                    </tbody>
                </table>
            </div>
        </div>
    );
}

function GlobalHabitsCard({
    habits,
    homeTeam,
    awayTeam,
}: {
    habits: NonNullable<PhaseAnalysisData["global_habits"]>;
    homeTeam?: string;
    awayTeam?: string;
}) {
    const batFirst = habits.bat_first;
    const chasing = habits.chasing;
    const scenarioRows = habits.scenario_rows;
    const home = habits.home;
    const away = habits.away;
    const startYear = habits.start_year;
    const homeLabel = homeTeam ?? "Home";
    const awayLabel = awayTeam ?? "Away";

    const fallbackBatFirstRows: ScenarioRow[] = [
        { label: "Avg PP Runs", home_value: batFirst?.home_team_pp_runs, away_value: batFirst?.away_team_pp_runs, higher_better: true, diff_text: "-", diff_tone: "muted" as const },
        { label: "Avg PP Wkts", home_value: batFirst?.home_team_pp_wkts, away_value: batFirst?.away_team_pp_wkts, higher_better: false, diff_text: "-", diff_tone: "muted" as const },
        { label: "Avg Mid Runs", home_value: batFirst?.home_team_mid_runs, away_value: batFirst?.away_team_mid_runs, higher_better: true, diff_text: "-", diff_tone: "muted" as const },
        { label: "Avg Mid Wkts", home_value: batFirst?.home_team_mid_wkts, away_value: batFirst?.away_team_mid_wkts, higher_better: false, diff_text: "-", diff_tone: "muted" as const },
        { label: "Avg Death Runs", home_value: batFirst?.home_team_dth_runs, away_value: batFirst?.away_team_dth_runs, higher_better: true, diff_text: "-", diff_tone: "muted" as const },
        { label: "Avg Death Wkts", home_value: batFirst?.home_team_dth_wkts, away_value: batFirst?.away_team_dth_wkts, higher_better: false, diff_text: "-", diff_tone: "muted" as const },
    ].filter((row) => row.home_value !== undefined || row.away_value !== undefined);

    const fallbackChasingRows: ScenarioRow[] = [
        { label: "Avg PP Score", home_value: chasing?.home_team_pp_runs, away_value: chasing?.away_team_pp_runs, higher_better: true, diff_text: "-", diff_tone: "muted" as const },
        { label: "Avg Mid Wkts", home_value: chasing?.home_team_mid_wkts, away_value: chasing?.away_team_mid_wkts, higher_better: false, diff_text: "-", diff_tone: "muted" as const },
        { label: "Avg Death Wkts", home_value: chasing?.home_team_dth_wkts, away_value: chasing?.away_team_dth_wkts, higher_better: false, diff_text: "-", diff_tone: "muted" as const },
    ].filter((row) => row.home_value !== undefined || row.away_value !== undefined);

    const batFirstRows = (scenarioRows?.bat_first && scenarioRows.bat_first.length > 0) ? scenarioRows.bat_first : fallbackBatFirstRows;
    const chasingRows = (scenarioRows?.chasing && scenarioRows.chasing.length > 0) ? scenarioRows.chasing : fallbackChasingRows;
    const hasScenarioView = batFirstRows.length > 0 || chasingRows.length > 0;

    if (!hasScenarioView && !home && !away) {
        return <EmptyState message="No global habits data available." />;
    }

    const renderScenarioTable = ({
        title,
        rows,
    }: {
        title: string;
        rows: ScenarioRow[];
    }) => (
        <div className="[background:var(--bg-elevated)] [border-radius:var(--radius-md)] [border:1px_solid_var(--border-subtle)] [overflow:hidden] [box-shadow:0_8px_22px_rgba(2,_8,_23,_0.2)]">
            <div className="[padding:10px_12px] [border-bottom:1px_solid_var(--border-subtle)] [font-size:0.8rem] [font-weight:700] [color:var(--text-secondary)] [text-transform:uppercase] [letter-spacing:0.04em]">
                {title}
            </div>
            <table className="[width:100%] [border-collapse:collapse] [font-size:0.82rem]">
                <thead>
                    <tr>
                        <th className={thClass("left")}>Metric</th>
                        <th className={thClass("right")}>{homeLabel}</th>
                        <th className={thClass("right")}>{awayLabel}</th>
                        <th className={thClass("right")}>Diff</th>
                    </tr>
                </thead>
                <tbody>
                    {rows.map((row, i) => {
                        const diffText = row.diff_text ?? "-";
                        const diffToneClass = row.diff_tone === "success"
                            ? "[color:var(--success)]"
                            : row.diff_tone === "danger"
                                ? "[color:var(--danger)]"
                                : "[color:var(--text-muted)]";
                        return (
                            <tr
                                key={row.label}
                                className={`[transition:background-color_0.2s] hover:[background:var(--bg-hover)] ${i < rows.length - 1 ? "[border-bottom:1px_solid_var(--border-subtle)]" : ""}`}
                            >
                                <td className={`${tdClass("left")} [font-weight:600]`}>{row.label}</td>
                                <td className={tdClass("right")}>{fmtNum(row.home_value)}</td>
                                <td className={tdClass("right")}>{fmtNum(row.away_value)}</td>
                                <td className={`${tdClass("right")} [font-weight:700] ${diffToneClass}`}>{diffText}</td>
                            </tr>
                        );
                    })}
                </tbody>
            </table>
        </div>
    );

    const legacyMetrics = [
        { label: "PP Run Rate", key: "pp_rr" as const },
        { label: "Middle Run Rate", key: "mid_rr" as const },
        { label: "Death Run Rate", key: "dth_rr" as const },
        { label: "Avg Score", key: "avg_score" as const },
    ];

    return (
        <div>
            <div className="[display:flex] [align-items:center] [gap:10px] [margin-bottom:10px]">
                <div className="[width:4px] [height:20px] [border-radius:2px] [background:var(--tier-strong)]" />
                <h4 className="[font-size:0.8rem] [font-weight:700] [color:var(--text-secondary)] [text-transform:uppercase] [letter-spacing:0.06em]">
                    {`Global Habits (Any Venue${startYear ? `, Since ${startYear}` : ""})`}
                </h4>
            </div>

            {hasScenarioView ? (
                <div className="[display:grid] [grid-template-columns:repeat(auto-fit,_minmax(320px,_1fr))] [gap:12px]">
                    {batFirstRows.length > 0 && renderScenarioTable({ title: "Scenario 1: Bat First", rows: batFirstRows })}
                    {chasingRows.length > 0 && renderScenarioTable({ title: "Scenario 2: Chasing", rows: chasingRows })}
                </div>
            ) : (
                <div className="[background:var(--bg-elevated)] [border-radius:var(--radius-md)] [border:1px_solid_var(--border-subtle)] [overflow:hidden] [box-shadow:0_8px_22px_rgba(2,_8,_23,_0.2)]">
                    <table className="[width:100%] [border-collapse:collapse] [font-size:0.825rem]">
                        <thead>
                            <tr>
                                <th className={thClass("left")}>Metric</th>
                                <th className={thClass("right")}>{homeLabel}</th>
                                <th className={thClass("right")}>{awayLabel}</th>
                            </tr>
                        </thead>
                        <tbody>
                            {legacyMetrics.map((m, i) => (
                                <tr
                                    key={m.key}
                                    className={`[transition:background-color_0.2s] hover:[background:var(--bg-hover)] ${i < legacyMetrics.length - 1 ? "[border-bottom:1px_solid_var(--border-subtle)]" : ""}`}
                                >
                                    <td className={`${tdClass("left")} [font-weight:600]`}>{m.label}</td>
                                    <td className={tdClass("right")}>{home ? fmtNum(home[m.key]) : "-"}</td>
                                    <td className={tdClass("right")}>{away ? fmtNum(away[m.key]) : "-"}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}
        </div>
    );
}

function fmtNum(val: unknown): string {
    if (val === null || val === undefined) return "-";
    const n = Number(val);
    if (Number.isNaN(n)) return String(val);
    return n.toFixed(1);
}
