"use client";

import type { ReactNode } from "react";
import { Shield, Target, TrendingUp, TrendingDown, Minus, AlertTriangle, Info } from "lucide-react";
import CountUp from "@/components/common/CountUp";
import EmptyState from "@/components/common/EmptyState";
import { getVenueBiasData } from "@/lib/venue-bias-types";
import type { VenueBiasData } from "@/lib/types";

interface VenueBiasCardProps {
    data: Record<string, unknown>;
}

const RELIABILITY_BADGE: Record<string, string> = {
    LOW_SAMPLE: "badge badge-danger",
    MODERATE:   "badge badge-caution",
    RELIABLE:   "badge badge-elite",
};

const RELIABILITY_LABELS: Record<string, string> = {
    LOW_SAMPLE: "Low sample",
    MODERATE:   "Moderate sample",
    RELIABLE:   "Reliable sample",
};

const TREND_ICON: Record<string, ReactNode> = {
    STRENGTHENING:     <TrendingUp size={14} />,
    WEAKENING:         <TrendingDown size={14} />,
    STABLE:            <Minus size={14} />,
    INSUFFICIENT_DATA: <Minus size={14} />,
};

const TREND_LABEL: Record<string, string> = {
    STRENGTHENING:     "Strengthening",
    WEAKENING:         "Weakening",
    STABLE:            "Stable",
    INSUFFICIENT_DATA: "Insufficient data",
};

const TREND_COLOR: Record<string, string> = {
    STRENGTHENING:     "[color:var(--tier-elite)]",
    WEAKENING:         "[color:var(--tier-caution)]",
    STABLE:            "[color:var(--text-secondary)]",
    INSUFFICIENT_DATA: "[color:var(--text-disabled)]",
};

function StatCell({ label, value, sub }: { label: string; value: string | number | null; sub?: string }) {
    return (
        <div className="flex flex-col gap-1.5 rounded-md p-4 [background:var(--bg-hover)] [border:1px_solid_var(--border-default)]">
            <span className="text-[0.62rem] font-bold uppercase tracking-[0.1em] [color:var(--text-muted)]">
                {label}
            </span>
            <span className="text-[1.75rem] font-black leading-none [color:var(--text-primary)] font-data">
                {value === null || value === undefined ? (
                    <span className="text-2xl [color:var(--text-disabled)]">—</span>
                ) : typeof value === "number" ? (
                    <CountUp end={value} decimals={0} duration={1.0} />
                ) : (
                    value
                )}
            </span>
            {sub && (
                <span className="text-[0.62rem] leading-tight [color:var(--text-muted)] font-data">{sub}</span>
            )}
        </div>
    );
}

export default function VenueBiasCard({ data }: VenueBiasCardProps) {
    const payload: VenueBiasData | null = getVenueBiasData(data);
    if (!payload) {
        return <EmptyState message="No bias data available." />;
    }

    const {
        venue_id,
        total_matches,
        period,
        bat1_win_pct,
        chase_win_pct,
        bias_verdict,
        sample_reliability,
        confidence_interval,
        score_distribution,
        score_extremes,
        bias_trend,
        toss_intelligence,
        percent_breakdown,
    } = payload;

    const tieNrPct = percent_breakdown?.tie_nr ?? 0;

    const verdictLabel =
        bias_verdict === "bat_first"  ? "Bat First Venue"  :
        bias_verdict === "bowl_first" ? "Bowl First Venue" :
        "Neutral Venue";

    const verdictStyle =
        bias_verdict === "bat_first"
            ? "[background:var(--bg-info)] [border-color:var(--border-info)] [color:var(--accent-ui)]"
            : bias_verdict === "bowl_first"
            ? "[background:var(--bg-caution)] [border-color:var(--border-caution)] [color:var(--tier-caution)]"
            : "[background:var(--bg-elevated)] [border-color:var(--border-default)] [color:var(--text-secondary)]";

    return (
        <div className="group mx-auto w-full max-w-2xl animate-fade-in flex flex-col gap-4">

            {/* ── 1. HERO ROW ─────────────────────────────── */}
            <div className="rounded-lg p-5 [background:var(--bg-elevated)] [border:1px_solid_var(--border-default)] [box-shadow:var(--shadow-md)]">
                <div className="flex items-start justify-between gap-4">
                    <div className="flex min-w-0 flex-col gap-1">
                        <span className="text-[0.62rem] font-bold uppercase tracking-[0.12em] [color:var(--text-muted)]">
                            Venue
                        </span>
                        <h2 className="truncate text-2xl font-black leading-tight tracking-tight [color:var(--text-primary)]">
                            {venue_id}
                        </h2>
                        <span className="text-xs [color:var(--text-secondary)]">
                            <span className="font-data font-bold">{total_matches}</span> matches ·{" "}
                            <span className="font-data font-bold">{period}</span> years
                        </span>
                    </div>
                    <div className="flex shrink-0 flex-col items-end gap-2">
                        <div className="flex items-center gap-1.5">
                            <div className={`inline-flex items-center gap-1.5 rounded border px-3 py-1.5 text-sm font-bold tracking-wide ${verdictStyle}`}>
                                {bias_verdict === "bat_first"  ? <Shield size={13} /> :
                                 bias_verdict === "bowl_first" ? <Target size={13} /> :
                                 <Minus size={13} />}
                                {verdictLabel}
                            </div>
                            <a
                                href="/docs/venue-bias"
                                target="_blank"
                                rel="noopener noreferrer"
                                aria-label="Learn about venue bias analysis"
                                className="rounded p-1 opacity-0 transition-opacity group-hover:opacity-100 [color:var(--text-muted)] hover:[color:var(--text-secondary)]"
                            >
                                <Info size={13} />
                            </a>
                        </div>
                        {sample_reliability && (
                            <span className={RELIABILITY_BADGE[sample_reliability] ?? "badge"}>
                                {RELIABILITY_LABELS[sample_reliability] ?? sample_reliability}
                            </span>
                        )}
                    </div>
                </div>
            </div>

            {/* ── 2. WIN SPLIT BAR ─────────────────────────── */}
            <div className="rounded-lg p-5 [background:var(--bg-elevated)] [border:1px_solid_var(--border-default)] [box-shadow:var(--shadow-md)]">
                <div className="mb-3 flex items-center justify-between">
                    <div className="flex items-center gap-2">
                        <Shield size={14} className="shrink-0 [color:var(--accent-ui)]" />
                        <span className="text-sm font-bold [color:var(--accent-ui)]">
                            Bat First{" "}
                            <span className="font-data text-base">{bat1_win_pct}%</span>
                        </span>
                    </div>
                    {tieNrPct > 0 && (
                        <span className="text-xs [color:var(--text-muted)]">
                            Tie/NR <span className="font-data">{tieNrPct}%</span>
                        </span>
                    )}
                    <div className="flex items-center gap-2">
                        <span className="text-sm font-bold [color:var(--accent-data)]">
                            Chase{" "}
                            <span className="font-data text-base">{chase_win_pct}%</span>
                        </span>
                        <Target size={14} className="shrink-0 [color:var(--accent-data)]" />
                    </div>
                </div>
                <div className="flex h-3 overflow-hidden rounded-full [background:var(--bg-hover)]">
                    <div
                        className="transition-all duration-500 ease-out [background:var(--accent-ui)]"
                        style={{ width: `${bat1_win_pct}%` }}
                    />
                    {tieNrPct > 0 && (
                        <div
                            className="opacity-30 transition-all duration-500 ease-out [background:var(--text-secondary)]"
                            style={{ width: `${tieNrPct}%` }}
                        />
                    )}
                    <div
                        className="transition-all duration-500 ease-out [background:var(--accent-data)]"
                        style={{ width: `${chase_win_pct}%` }}
                    />
                </div>
                {confidence_interval && (
                    <p className="mt-3 text-center text-xs [color:var(--text-secondary)]">
                        95% confidence:{" "}
                        <span className="font-data font-bold [color:var(--text-primary)]">{confidence_interval.lower}%</span>
                        <span className="mx-1.5 [color:var(--text-muted)]">–</span>
                        <span className="font-data font-bold [color:var(--text-primary)]">{confidence_interval.upper}%</span>
                        <span className="ml-1.5 [color:var(--text-muted)]">bat-first</span>
                    </p>
                )}
            </div>

            {/* ── 3. SCORE INTEL GRID ──────────────────────── */}
            <div className="grid grid-cols-2 gap-3">
                <StatCell
                    label="Avg 1st Inn"
                    value={score_distribution?.inn1.median ?? null}
                    sub={score_distribution
                        ? `min ${score_distribution.inn1.min} · max ${score_distribution.inn1.max} · σ${score_distribution.inn1.std}`
                        : undefined}
                />
                <StatCell
                    label="Avg 2nd Inn"
                    value={score_distribution?.inn2.median ?? null}
                    sub={score_distribution
                        ? `min ${score_distribution.inn2.min} · max ${score_distribution.inn2.max} · σ${score_distribution.inn2.std}`
                        : undefined}
                />
                <StatCell
                    label="Lowest Defended"
                    value={score_extremes?.lowest_defended ?? null}
                />
                <StatCell
                    label="Highest Chased"
                    value={score_extremes?.highest_chased ?? null}
                />
            </div>

            {/* ── 4. BIAS TREND STRIP ──────────────────────── */}
            {bias_trend && bias_trend.direction !== "INSUFFICIENT_DATA" && (
                <div className="flex flex-wrap items-center gap-3 rounded-lg px-5 py-4 [background:var(--bg-elevated)] [border:1px_solid_var(--border-default)] [box-shadow:var(--shadow-sm)]">
                    <span className="min-w-[72px] text-[0.62rem] font-bold uppercase tracking-[0.1em] [color:var(--text-muted)]">
                        Bias Trend
                    </span>
                    <span className="font-data text-sm [color:var(--text-secondary)]">
                        Historical{" "}
                        <span className="text-base font-bold [color:var(--text-primary)]">{bias_trend.historical_pct}%</span>
                        <span className="mx-2 [color:var(--text-muted)]">→</span>
                        Recent{" "}
                        <span className="text-base font-bold [color:var(--text-primary)]">{bias_trend.recent_pct}%</span>
                    </span>
                    <div className={`ml-auto flex items-center gap-1.5 text-sm font-bold ${TREND_COLOR[bias_trend.direction] ?? "[color:var(--text-muted)]"}`}>
                        {TREND_ICON[bias_trend.direction]}
                        <span>{TREND_LABEL[bias_trend.direction]}</span>
                    </div>
                </div>
            )}

            {/* ── 5. TOSS INTELLIGENCE PANEL ───────────────── */}
            {toss_intelligence?.data_available && (
                <div className="rounded-lg p-5 [background:var(--bg-elevated)] [border:1px_solid_var(--border-default)] [box-shadow:var(--shadow-md)]">
                    <p className="mb-4 text-[0.62rem] font-bold uppercase tracking-[0.1em] [color:var(--text-muted)]">
                        Toss Intelligence ·{" "}
                        <span className="font-data">{toss_intelligence.toss_match_count}</span> matches with toss data
                    </p>
                    <div className="flex gap-8">
                        <div className="flex flex-col gap-1">
                            <span className="text-xs font-medium [color:var(--text-secondary)]">Chose to Bat</span>
                            <span className="font-data text-[2rem] font-black leading-none [color:var(--accent-ui)]">
                                {toss_intelligence.chose_bat_win_pct !== null
                                    ? `${toss_intelligence.chose_bat_win_pct}%`
                                    : "—"}
                            </span>
                            <span className="text-[0.62rem] [color:var(--text-muted)]">toss winner win rate</span>
                        </div>
                        <div className="w-px self-stretch [background:var(--border-default)]" />
                        <div className="flex flex-col gap-1">
                            <span className="text-xs font-medium [color:var(--text-secondary)]">Chose to Bowl</span>
                            <span className="font-data text-[2rem] font-black leading-none [color:var(--accent-data)]">
                                {toss_intelligence.chose_bowl_win_pct !== null
                                    ? `${toss_intelligence.chose_bowl_win_pct}%`
                                    : "—"}
                            </span>
                            <span className="text-[0.62rem] [color:var(--text-muted)]">toss winner win rate</span>
                        </div>
                    </div>
                </div>
            )}

            {/* ── LOW SAMPLE WARNING ───────────────────────── */}
            {sample_reliability === "LOW_SAMPLE" && (
                <div className="flex items-center gap-2.5 rounded-lg px-4 py-3 text-sm [background:var(--bg-caution)] [border:1px_solid_var(--border-caution)] [color:var(--tier-caution)]">
                    <AlertTriangle size={14} className="shrink-0" />
                    Fewer than 10 matches — treat all percentages as indicative only.
                </div>
            )}

        </div>
    );
}
