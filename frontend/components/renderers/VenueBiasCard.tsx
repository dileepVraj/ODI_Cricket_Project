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
    MODERATE: "badge badge-caution",
    RELIABLE:  "badge badge-elite",
};

const RELIABILITY_LABELS: Record<string, string> = {
    LOW_SAMPLE: "Low sample",
    MODERATE:   "Moderate sample",
    RELIABLE:   "Reliable sample",
};

const TREND_ICON: Record<string, ReactNode> = {
    STRENGTHENING:    <TrendingUp size={14} />,
    WEAKENING:        <TrendingDown size={14} />,
    STABLE:           <Minus size={14} />,
    INSUFFICIENT_DATA: <Minus size={14} />,
};

const TREND_LABEL: Record<string, string> = {
    STRENGTHENING:    "Strengthening",
    WEAKENING:        "Weakening",
    STABLE:           "Stable",
    INSUFFICIENT_DATA: "Insufficient data",
};

const TREND_COLOR: Record<string, string> = {
    STRENGTHENING:    "[color:var(--tier-elite)]",
    WEAKENING:        "[color:var(--tier-caution)]",
    STABLE:           "[color:var(--text-secondary)]",
    INSUFFICIENT_DATA: "[color:var(--text-disabled)]",
};

function StatCell({ label, value, sub }: { label: string; value: string | number | null; sub?: string }) {
    return (
        <div className="px-4 py-3.5 [background:var(--bg-elevated)] [border-radius:var(--radius-md)] [border:1px_solid_var(--border-subtle)]">
            <div className="mb-1 text-[0.7rem] font-semibold uppercase tracking-[0.05em] [color:var(--text-disabled)]">
                {label}
            </div>
            <div className="text-[1.15rem] font-extrabold [color:var(--text-primary)] font-data">
                {value === null || value === undefined ? (
                    <span className="[color:var(--text-disabled)]">—</span>
                ) : typeof value === "number" ? (
                    <CountUp end={value} decimals={0} duration={1.0} />
                ) : (
                    value
                )}
            </div>
            {sub && (
                <div className="mt-0.5 text-[0.7rem] [color:var(--text-disabled)] font-data">{sub}</div>
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
        <div className="group relative flex flex-col gap-5 animate-fade-in">

            {/* 1. HERO ROW */}
            <div className="flex flex-wrap items-start justify-between gap-3">
                <div>
                    <div className="mb-1 text-[0.7rem] font-semibold uppercase tracking-[0.06em] [color:var(--text-disabled)]">
                        Venue
                    </div>
                    <div className="text-xl font-bold [color:var(--text-primary)]">{venue_id}</div>
                    <div className="mt-1 text-[0.78rem] [color:var(--text-disabled)]">
                        <span className="font-data">{total_matches}</span> matches ·{" "}
                        <span className="font-data">{period}</span> years
                    </div>
                </div>
                <div className="flex flex-col items-end gap-2">
                    <div className="flex items-center gap-2">
                        <div className={`inline-flex items-center gap-1.5 border px-3.5 py-1.5 text-[0.82rem] font-bold tracking-[0.03em] [border-radius:var(--radius-lg)] ${verdictStyle}`}>
                            {bias_verdict === "bat_first"  ? <Shield size={14} /> :
                             bias_verdict === "bowl_first" ? <Target size={14} /> :
                             <Minus size={14} />}
                            {verdictLabel}
                        </div>
                        <a
                            href="/docs/venue-bias"
                            target="_blank"
                            rel="noopener noreferrer"
                            aria-label="Learn about venue bias analysis"
                            className="rounded p-1 opacity-0 transition-opacity group-hover:opacity-100 [color:var(--text-disabled)] hover:[color:var(--text-secondary)]"
                        >
                            <Info size={14} />
                        </a>
                    </div>
                    {sample_reliability && (
                        <span className={RELIABILITY_BADGE[sample_reliability] ?? "badge"}>
                            {RELIABILITY_LABELS[sample_reliability] ?? sample_reliability}
                        </span>
                    )}
                </div>
            </div>

            {/* 2. WIN SPLIT BAR */}
            <div className="px-5 py-4 [background:var(--bg-elevated)] [border-radius:var(--radius-lg)] [border:1px_solid_var(--border-subtle)]">
                <div className="mb-2.5 flex justify-between text-[0.82rem] font-bold">
                    <span className="[color:var(--accent-ui)]">
                        <Shield size={13} className="mr-1 inline align-middle" />
                        Bat First <span className="font-data">{bat1_win_pct}%</span>
                    </span>
                    {tieNrPct > 0 && (
                        <span className="text-[0.75rem] [color:var(--text-disabled)]">
                            Tie/NR <span className="font-data">{tieNrPct}%</span>
                        </span>
                    )}
                    <span className="[color:var(--accent-data)]">
                        Chase <span className="font-data">{chase_win_pct}%</span>
                        <Target size={13} className="ml-1 inline align-middle" />
                    </span>
                </div>
                <div className="flex h-2.5 overflow-hidden rounded-full [background:var(--bg-hover)]">
                    <div
                        className="transition-all duration-500 ease-out [background:var(--accent-ui)]"
                        style={{ width: `${bat1_win_pct}%` }}
                    />
                    {tieNrPct > 0 && (
                        <div
                            className="opacity-40 transition-all duration-500 ease-out [background:var(--text-disabled)]"
                            style={{ width: `${tieNrPct}%` }}
                        />
                    )}
                    <div
                        className="transition-all duration-500 ease-out [background:var(--accent-data)]"
                        style={{ width: `${chase_win_pct}%` }}
                    />
                </div>
                {confidence_interval && (
                    <div className="mt-2 text-center text-[0.72rem] [color:var(--text-disabled)]">
                        95% confidence:{" "}
                        <span className="font-data [color:var(--text-secondary)]">{confidence_interval.lower}%</span>
                        {" – "}
                        <span className="font-data [color:var(--text-secondary)]">{confidence_interval.upper}%</span>
                        {" "}bat-first
                    </div>
                )}
            </div>

            {/* 3. SCORE INTEL GRID */}
            <div className="grid grid-cols-2 gap-2.5 sm:grid-cols-4">
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

            {/* 4. BIAS TREND STRIP */}
            {bias_trend && bias_trend.direction !== "INSUFFICIENT_DATA" && (
                <div className="flex items-center gap-2.5 px-4 py-3 [background:var(--bg-elevated)] [border-radius:var(--radius-md)] [border:1px_solid_var(--border-subtle)]">
                    <div className="min-w-[80px] text-[0.7rem] font-semibold uppercase tracking-[0.05em] [color:var(--text-disabled)]">
                        Bias Trend
                    </div>
                    <div className="text-[0.82rem] [color:var(--text-secondary)] font-data">
                        Historical{" "}
                        <span className="font-bold [color:var(--text-primary)]">{bias_trend.historical_pct}%</span>
                        {" → "}
                        Recent{" "}
                        <span className="font-bold [color:var(--text-primary)]">{bias_trend.recent_pct}%</span>
                    </div>
                    <div className={`ml-auto inline-flex items-center gap-1 text-[0.78rem] font-bold ${TREND_COLOR[bias_trend.direction] ?? "[color:var(--text-disabled)]"}`}>
                        {TREND_ICON[bias_trend.direction]}
                        {TREND_LABEL[bias_trend.direction]}
                    </div>
                </div>
            )}

            {/* 5. TOSS INTELLIGENCE PANEL */}
            {toss_intelligence?.data_available && (
                <div className="px-4 py-3.5 [background:var(--bg-elevated)] [border-radius:var(--radius-md)] [border:1px_solid_var(--border-subtle)]">
                    <div className="mb-2.5 text-[0.7rem] font-semibold uppercase tracking-[0.05em] [color:var(--text-disabled)]">
                        Toss Intelligence ·{" "}
                        <span className="font-data">{toss_intelligence.toss_match_count}</span> matches with toss data
                    </div>
                    <div className="flex flex-wrap gap-6">
                        <div>
                            <div className="text-[0.72rem] [color:var(--text-disabled)]">Chose to Bat</div>
                            <div className="text-[1.1rem] font-extrabold [color:var(--accent-ui)] font-data">
                                {toss_intelligence.chose_bat_win_pct !== null
                                    ? `${toss_intelligence.chose_bat_win_pct}%`
                                    : "—"}
                            </div>
                            <div className="text-[0.68rem] [color:var(--text-disabled)]">toss winner win rate</div>
                        </div>
                        <div className="w-px self-stretch [background:var(--border-subtle)]" />
                        <div>
                            <div className="text-[0.72rem] [color:var(--text-disabled)]">Chose to Bowl</div>
                            <div className="text-[1.1rem] font-extrabold [color:var(--accent-data)] font-data">
                                {toss_intelligence.chose_bowl_win_pct !== null
                                    ? `${toss_intelligence.chose_bowl_win_pct}%`
                                    : "—"}
                            </div>
                            <div className="text-[0.68rem] [color:var(--text-disabled)]">toss winner win rate</div>
                        </div>
                    </div>
                </div>
            )}

            {/* Low sample warning */}
            {sample_reliability === "LOW_SAMPLE" && (
                <div className="flex items-center gap-2 px-3.5 py-2.5 text-[0.78rem] [background:var(--bg-caution)] [border-radius:var(--radius-md)] [border:1px_solid_var(--border-caution)] [color:var(--tier-caution)]">
                    <AlertTriangle size={14} />
                    Fewer than 10 matches — treat all percentages as indicative only.
                </div>
            )}
        </div>
    );
}
