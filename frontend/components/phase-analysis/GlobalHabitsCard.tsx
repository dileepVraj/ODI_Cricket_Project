"use client";

import EmptyState from "@/components/common/EmptyState";
import { thClass, tdClass, fmtNum } from "@/components/phase-analysis/PhaseTableStyles";

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

interface LegacyGlobalHabitsTeam {
    pp_rr: number;
    mid_rr: number;
    dth_rr: number;
    avg_score: number;
}

interface PhaseAnalysisData {
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
}

export default function GlobalHabitsCard({
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
                            ? "[color:var(--tier-elite)]"
                            : row.diff_tone === "danger"
                                ? "[color:var(--tier-danger)]"
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
