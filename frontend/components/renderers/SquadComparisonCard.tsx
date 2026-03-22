"use client";

import React from "react";
import EmptyState from "@/components/common/EmptyState";
import DataTable from "@/components/renderers/DataTable";

interface SquadMetrics {
    caps: number;
    runs: number;
    wickets: number;
    centuries: number;
    fifties: number;
    five_wkt_hauls: number;
    avg_caps: number;
}

interface SquadComparisonCardProps {
    data: Record<string, unknown>;
}

type TableRow = Record<string, unknown>;

const METRIC_LABELS: Record<keyof SquadMetrics, string> = {
    caps: "Caps",
    runs: "Runs",
    wickets: "Wkts",
    centuries: "100s",
    fifties: "50s",
    five_wkt_hauls: "5WH",
    avg_caps: "Avg Caps",
};

const METRIC_KEYS = Object.keys(METRIC_LABELS) as Array<keyof SquadMetrics>;

function toSquadMetrics(raw: Record<string, unknown> | null): SquadMetrics | null {
    if (!raw) {
        return null;
    }

    const safeRaw = raw;
    function toMetricValue(key: keyof SquadMetrics): number {
        const value = Number(safeRaw[key]);
        return Number.isNaN(value) ? 0 : value;
    }

    return {
        caps: toMetricValue("caps"),
        runs: toMetricValue("runs"),
        wickets: toMetricValue("wickets"),
        centuries: toMetricValue("centuries"),
        fifties: toMetricValue("fifties"),
        five_wkt_hauls: toMetricValue("five_wkt_hauls"),
        avg_caps: toMetricValue("avg_caps"),
    };
}

export default function SquadComparisonCard({ data }: SquadComparisonCardProps) {
    const teamAName = String(data["team_a_name"] ?? "Team A");
    const teamBName = String(data["team_b_name"] ?? "Team B");
    const venueId = String(data["venue_id"] ?? "");
    const years = Number(data["years"] ?? 0);
    const rawMetricsA =
        typeof data["metrics_a"] === "object" && data["metrics_a"] !== null && !Array.isArray(data["metrics_a"])
            ? (data["metrics_a"] as Record<string, unknown>)
            : null;
    const rawMetricsB =
        typeof data["metrics_b"] === "object" && data["metrics_b"] !== null && !Array.isArray(data["metrics_b"])
            ? (data["metrics_b"] as Record<string, unknown>)
            : null;
    const metricsA = toSquadMetrics(rawMetricsA);
    const metricsB = toSquadMetrics(rawMetricsB);
    const statsA = Array.isArray(data["player_stats_a"]) ? (data["player_stats_a"] as TableRow[]) : [];
    const statsB = Array.isArray(data["player_stats_b"]) ? (data["player_stats_b"] as TableRow[]) : [];

    if (!metricsA || !metricsB || statsA.length === 0 || statsB.length === 0) {
        return <EmptyState message="No squad comparison data available." />;
    }

    return (
        <div className="animate-fade-in flex flex-col gap-6">
            <section className="glass-card flex flex-wrap items-start justify-between gap-4 p-5">
                <div className="flex flex-col gap-2">
                    <h2 className="[color:var(--text-primary)] text-2xl font-black tracking-tight">
                        {teamAName}
                        <span className="[color:var(--text-muted)] mx-3 text-lg font-semibold uppercase tracking-[0.18em]">
                            vs
                        </span>
                        {teamBName}
                    </h2>
                    <div className="flex flex-wrap gap-2 text-xs uppercase tracking-[0.14em]">
                        {venueId ? (
                            <span className="badge [color:var(--text-secondary)]">{venueId}</span>
                        ) : null}
                        {years > 0 ? (
                            <span className="badge [color:var(--text-secondary)]">{`${years} Years`}</span>
                        ) : null}
                    </div>
                </div>
            </section>

            <section className="glass-card flex flex-col gap-4 p-5">
                <div className="flex flex-col gap-1">
                    <span className="[color:var(--text-muted)] text-xs font-semibold uppercase tracking-[0.18em]">
                        Squad Strength
                    </span>
                    <p className="[color:var(--text-secondary)] text-sm">
                        Squad-level comparison across the selected XI inputs.
                    </p>
                </div>

                <div className="[overflow-x:auto]">
                    <div className="[display:grid] [grid-template-columns:180px_repeat(7,_minmax(88px,_1fr))] [min-width:860px] [border:1px_solid_var(--border-subtle)] [border-radius:var(--radius-lg)] [background:var(--bg-elevated)]">
                        <div className="[border-right:1px_solid_var(--border-subtle)] [border-bottom:1px_solid_var(--border-subtle)] [padding:14px_16px] [color:var(--text-muted)] text-[0.72rem] font-semibold uppercase tracking-[0.18em]">
                            Team
                        </div>
                        {METRIC_KEYS.map((metricKey) => (
                            <div
                                key={`label-${metricKey}`}
                                className="[border-bottom:1px_solid_var(--border-subtle)] [padding:14px_10px] text-center [color:var(--text-muted)] text-[0.72rem] font-semibold uppercase tracking-[0.18em]"
                            >
                                {METRIC_LABELS[metricKey]}
                            </div>
                        ))}

                        <div className="[border-right:1px_solid_var(--border-subtle)] [border-bottom:1px_solid_var(--border-subtle)] [padding:16px] [color:var(--accent-ui)] text-sm font-bold uppercase tracking-[0.14em]">
                            {teamAName}
                        </div>
                        {METRIC_KEYS.map((metricKey) => (
                            <div
                                key={`a-${metricKey}`}
                                className="[border-bottom:1px_solid_var(--border-subtle)] [padding:16px_10px] text-center [color:var(--accent-ui)] text-lg font-black font-numeric"
                            >
                                {String(metricsA[metricKey])}
                            </div>
                        ))}

                        <div className="[border-right:1px_solid_var(--border-subtle)] [padding:16px] [color:var(--accent-data)] text-sm font-bold uppercase tracking-[0.14em]">
                            {teamBName}
                        </div>
                        {METRIC_KEYS.map((metricKey) => (
                            <div
                                key={`b-${metricKey}`}
                                className="[padding:16px_10px] text-center [color:var(--accent-data)] text-lg font-black font-numeric"
                            >
                                {String(metricsB[metricKey])}
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            <section className="glass-card flex flex-col gap-4 p-5">
                <div className="flex flex-col gap-3">
                    <h3 className="[color:var(--text-primary)] text-lg font-bold">{teamAName} XI</h3>
                    <div className="[background:var(--bg-surface)] [border:1px_solid_var(--border-subtle)] [border-radius:var(--radius-lg)] p-4">
                        <DataTable data={statsA} />
                    </div>
                </div>
            </section>

            <section className="glass-card flex flex-col gap-4 p-5">
                <div className="flex flex-col gap-3">
                    <h3 className="[color:var(--text-primary)] text-lg font-bold">{teamBName} XI</h3>
                    <div className="[background:var(--bg-surface)] [border:1px_solid_var(--border-subtle)] [border-radius:var(--radius-lg)] p-4">
                        <DataTable data={statsB} />
                    </div>
                </div>
            </section>
        </div>
    );
}
