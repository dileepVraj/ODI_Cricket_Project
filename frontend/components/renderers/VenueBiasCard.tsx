"use client";

import type { ReactNode } from "react";
import { TrendingUp, TrendingDown, Minus, AlertTriangle, Info } from "lucide-react";
import CountUp from "@/components/common/CountUp";
import EmptyState from "@/components/common/EmptyState";
import { getVenueBiasData } from "@/lib/venue-bias-types";
import type { VenueBiasData } from "@/lib/types";

interface VenueBiasCardProps {
    data: Record<string, unknown>;
    onScoreClick?: (score: number, type: "lowest_defended" | "highest_chased") => void;
}

const TREND_ICON: Record<string, ReactNode> = { STRENGTHENING: <TrendingUp size={13} />, WEAKENING: <TrendingDown size={13} />, STABLE: <Minus size={13} />, INSUFFICIENT_DATA: <Minus size={13} /> };
const TREND_LABEL: Record<string, string> = { STRENGTHENING: "Strengthening", WEAKENING: "Weakening", STABLE: "Stable", INSUFFICIENT_DATA: "Insufficient data" };
const TREND_COLOR: Record<string, string> = { STRENGTHENING: "[color:var(--tier-elite)]", WEAKENING: "[color:var(--tier-caution)]", STABLE: "[color:var(--text-secondary)]", INSUFFICIENT_DATA: "[color:var(--text-disabled)]" };

export default function VenueBiasCard({ data, onScoreClick }: VenueBiasCardProps) {
    const payload: VenueBiasData | null = getVenueBiasData(data);
    if (!payload) {
        return <EmptyState message="No bias data available." />;
    }

    const { venue_id, total_matches, period, bat1_win_pct, chase_win_pct, bias_verdict, sample_reliability, confidence_interval, percent_breakdown, score_distribution, score_extremes, bias_trend, toss_intelligence, toss_loss_recovery, score_banding } = payload;

    const excludedMatches = percent_breakdown?.tie_nr ?? 0;

    const verdictLabel = bias_verdict === "bat_first" ? "Bat First Venue" : bias_verdict === "bowl_first" ? "Bowl First Venue" : "Neutral Venue";

    const verdictBadgeStyle = bias_verdict === "bat_first"
        ? "[background:var(--bg-info)] [border-color:var(--border-info)] [color:var(--accent-ui)]"
        : bias_verdict === "bowl_first"
        ? "[background:var(--bg-caution)] [border-color:var(--border-caution)] [color:var(--tier-caution)]"
        : "[background:var(--bg-elevated)] [border-color:var(--border-default)] [color:var(--text-secondary)]";

    const reliabilityStyle = sample_reliability === "RELIABLE"
        ? "[background:var(--bg-elite)] [border-color:var(--border-elite)] [color:var(--tier-elite)]"
        : sample_reliability === "MODERATE"
        ? "[background:var(--bg-caution)] [border-color:var(--border-caution)] [color:var(--tier-caution)]"
        : "[background:var(--bg-danger)] [border-color:var(--border-danger)] [color:var(--tier-danger)]";

    const reliabilityLabel = sample_reliability === "RELIABLE" ? "Reliable sample" : sample_reliability === "MODERATE" ? "Moderate sample" : sample_reliability === "LOW_SAMPLE" ? "Low sample" : sample_reliability ?? "";

    const scoreGrid: Array<{
        label: string;
        value: number | null;
        sub: string | undefined;
        cls: string;
        type?: "lowest_defended" | "highest_chased";
    }> = [
        {
            label: "AVG 1ST INN",
            value: score_distribution?.inn1.median ?? null,
            sub:   score_distribution ? `min ${score_distribution.inn1.min} · max ${score_distribution.inn1.max} · σ${score_distribution.inn1.std}` : undefined,
            cls:   "[border-right:1px_solid_var(--border-subtle)] [border-bottom:1px_solid_var(--border-subtle)]",
        },
        {
            label: "AVG 2ND INN",
            value: score_distribution?.inn2.median ?? null,
            sub:   score_distribution ? `min ${score_distribution.inn2.min} · max ${score_distribution.inn2.max} · σ${score_distribution.inn2.std}` : undefined,
            cls:   "[border-bottom:1px_solid_var(--border-subtle)]",
        },
        {
            label: "LOWEST DEFENDED",
            value: score_extremes?.lowest_defended ?? null,
            sub:   undefined,
            cls:   "[border-right:1px_solid_var(--border-subtle)]",
            type:  "lowest_defended",
        },
        {
            label: "HIGHEST CHASED",
            value: score_extremes?.highest_chased ?? null,
            sub:   undefined,
            cls:   "",
            type:  "highest_chased",
        },
    ];

    return (
        <section className="group w-full animate-fade-in [background:var(--bg-elevated)] [border:1px_solid_var(--border-default)] rounded-xl shadow-sm overflow-hidden flex flex-col">

            {/* ── 1. HERO ROW ───────────────────────────────── */}
            <div className="px-6 pt-6 pb-5 flex justify-between items-start [border-bottom:1px_solid_var(--border-subtle)]">
                <div className="space-y-1 min-w-0">
                    <span className="text-[10px] font-bold uppercase tracking-[0.1em] [color:var(--text-muted)] block">VENUE</span>
                    <h3 className="text-2xl font-bold tracking-tight [color:var(--text-primary)] truncate">{venue_id}</h3>
                    <p className="text-xs [color:var(--text-muted)]">
                        <span className="font-data">{total_matches}</span> matches ·{" "}
                        <span className="font-data">{period}</span> years
                    </p>
                </div>
                <div className="flex shrink-0 flex-col items-end gap-2 ml-4">
                    <div className={`flex items-center gap-1.5 px-3.5 py-1.5 border rounded-full text-[10px] font-bold uppercase tracking-[0.05em] ${verdictBadgeStyle}`}>
                        {verdictLabel}
                    </div>
                    {sample_reliability && (
                        <div className={`px-2.5 py-1 border rounded-full ${reliabilityStyle}`}>
                            <span className="text-[9px] font-medium uppercase tracking-[0.05em]">{reliabilityLabel}</span>
                        </div>
                    )}
                    <a
                        href="/docs/venue-bias"
                        target="_blank"
                        rel="noopener noreferrer"
                        aria-label="Learn about venue bias analysis"
                        className="opacity-0 group-hover:opacity-100 transition-opacity [color:var(--text-muted)] hover:[color:var(--text-secondary)]"
                    >
                        <Info size={13} />
                    </a>
                </div>
            </div>

            {/* ── 2. WIN SPLIT BAR ──────────────────────────── */}
            <div className="px-6 py-5 [background:var(--bg-hover)] [border-bottom:1px_solid_var(--border-subtle)]">
                <div className="flex justify-between items-end mb-3">
                    <span className="font-data text-lg font-black [color:var(--accent-ui)]">
                        BAT FIRST <CountUp end={bat1_win_pct} decimals={0} duration={1.0} />%
                    </span>
                    <span className="font-data text-lg font-black [color:var(--accent-data)]">
                        CHASE <CountUp end={chase_win_pct} decimals={0} duration={1.0} />%
                    </span>
                </div>
                <div className="w-full h-[10px] rounded-full overflow-hidden flex [background:var(--bg-elevated)]">
                    <div className="h-full [background:var(--accent-ui)] transition-all duration-500 ease-out" style={{ width: `${bat1_win_pct}%` }} />
                    <div className="h-full flex-1 [background:var(--accent-data)] transition-all duration-500 ease-out" />
                </div>
                {confidence_interval && (
                    <p className="mt-3 text-center text-[10px] uppercase tracking-[0.05em] [color:var(--text-muted)]">
                        95% confidence:{" "}
                        <span className="font-data font-bold [color:var(--text-primary)]">{confidence_interval.lower}%</span>
                        <span className="mx-1 [color:var(--text-muted)]">–</span>
                        <span className="font-data font-bold [color:var(--text-primary)]">{confidence_interval.upper}%</span>
                        <span className="ml-1">{" "}bat-first</span>
                    </p>
                )}
                {excludedMatches > 0 && (
                    <p className="mt-1 text-center text-[10px] uppercase tracking-[0.05em] [color:var(--text-disabled)]">
                        <span className="font-data">{excludedMatches}</span> match{excludedMatches !== 1 ? "es" : ""} excluded — ties / no result
                    </p>
                )}
            </div>

            {/* ── 3. SCORE INTEL GRID ───────────────────────── */}
            <div className="grid grid-cols-2">
                {scoreGrid.map(({ label, value, sub, cls, type }) => {
                    const isClickable = !!type && !!onScoreClick && value !== null && value !== undefined;
                    const Cell = isClickable ? "button" : "div";
                    return (
                        <Cell
                            key={label}
                            {...(isClickable ? {
                                onClick: () => onScoreClick!(value!, type!),
                                title: `Jump to match in audit`,
                                type: "button",
                            } : {})}
                            className={`p-5 flex flex-col items-center justify-center text-center hover:[background:var(--bg-hover)] transition-colors ${cls} ${isClickable ? "cursor-pointer w-full border-0 bg-transparent" : ""}`}
                        >
                            <span className="text-[9px] font-bold uppercase tracking-[0.05em] [color:var(--text-muted)] mb-2">{label}</span>
                            <span className="text-3xl font-bold font-data [color:var(--text-primary)]">
                                {value === null || value === undefined
                                    ? <span className="[color:var(--text-disabled)]">—</span>
                                    : <CountUp end={value} decimals={0} duration={1.0} />}
                            </span>
                            {sub && <span className="text-[10px] [color:var(--text-muted)] mt-2 font-data">{sub}</span>}
                            {isClickable && (
                                <span className="text-[9px] [color:var(--text-disabled)] mt-1.5 uppercase tracking-[0.05em]">↓ view match</span>
                            )}
                        </Cell>
                    );
                })}
            </div>

            {/* ── 4. BIAS TREND STRIP ───────────────────────── */}
            {bias_trend && bias_trend.direction !== "INSUFFICIENT_DATA" && (
                <div className="px-6 py-3 [background:var(--bg-hover)] [border-top:1px_solid_var(--border-subtle)] [border-bottom:1px_solid_var(--border-subtle)] flex items-center justify-between gap-4">
                    <span className="text-[9px] font-bold uppercase tracking-[0.05em] [color:var(--text-muted)] shrink-0">BIAS TREND</span>
                    <span className="text-xs font-bold font-data">
                        Historical <span className="[color:var(--text-muted)]">{bias_trend.historical_pct}%</span>
                        {" → "}
                        Recent <span className="[color:var(--accent-ui)]">{bias_trend.recent_pct}%</span>
                    </span>
                    <div className={`flex items-center gap-1 text-[10px] font-bold uppercase tracking-[0.05em] shrink-0 ${TREND_COLOR[bias_trend.direction] ?? "[color:var(--text-muted)]"}`}>
                        {TREND_ICON[bias_trend.direction]}
                        <span>{TREND_LABEL[bias_trend.direction]}</span>
                    </div>
                </div>
            )}

            {/* ── SCORE BANDING ────────────────────────────── */}
            {score_banding && (
                <div className="px-6 py-5 [border-top:1px_solid_var(--border-subtle)]">
                    <p className="text-[9px] font-bold uppercase tracking-[0.05em] [color:var(--text-secondary)] mb-4">SCORE BANDING · 1ST INNINGS</p>
                    {score_banding.inn1_bands.map((band, index) => (
                        <div key={`${band.label}-${index}`} className={`flex items-center gap-3 ${index < score_banding.inn1_bands.length - 1 ? "mb-2" : ""}`}>
                            <span className="w-16 text-[10px] font-data [color:var(--text-muted)] text-right shrink-0">{band.label}</span>
                            <div className="flex-1 h-[6px] rounded-full [background:var(--bg-hover)] overflow-hidden relative">
                                <div className="absolute inset-y-0 left-0 [background:var(--accent-ui)] rounded-full" style={{ width: `${band.pct}%` }} />
                            </div>
                            <span className="w-9 text-[10px] font-data font-bold [color:var(--text-primary)] text-right shrink-0">{band.pct}%</span>
                        </div>
                    ))}
                </div>
            )}

            {/* ── 5. TOSS INTELLIGENCE PANEL ────────────────── */}
            {toss_intelligence?.data_available && (
                <div className="p-6">
                    <p className="text-[10px] font-bold uppercase tracking-[0.05em] [color:var(--text-secondary)] mb-6">
                        TOSS INTELLIGENCE ·{" "}
                        <span className="font-data">{toss_intelligence.toss_match_count}</span> matches with toss data
                    </p>
                    <div className="grid grid-cols-2 relative">
                        <div className="absolute left-1/2 top-0 bottom-0 w-px [background:var(--border-subtle)]" aria-hidden="true" />
                        <div className="flex flex-col items-center pr-6">
                            <span className="text-xs [color:var(--text-secondary)] mb-1">Chose to Bat</span>
                            <span className="text-4xl font-black font-data [color:var(--accent-ui)]">
                                {toss_intelligence.chose_bat_win_pct !== null
                                    ? <><CountUp end={toss_intelligence.chose_bat_win_pct} decimals={0} duration={1.0} />%</>
                                    : "—"}
                            </span>
                            <span className="text-[9px] uppercase tracking-[0.05em] [color:var(--text-muted)] mt-2">toss winner win rate</span>
                            <span className="text-[9px] font-data [color:var(--text-disabled)] mt-1">
                                {toss_intelligence.chose_bat_win_pct === null
                                    ? `n=${toss_intelligence.chose_bat_count} — insufficient`
                                    : `n=${toss_intelligence.chose_bat_count}`}
                            </span>
                        </div>
                        <div className="flex flex-col items-center pl-6">
                            <span className="text-xs [color:var(--text-secondary)] mb-1">Chose to Bowl</span>
                            <span className="text-4xl font-black font-data [color:var(--accent-data)]">
                                {toss_intelligence.chose_bowl_win_pct !== null
                                    ? <><CountUp end={toss_intelligence.chose_bowl_win_pct} decimals={0} duration={1.0} />%</>
                                    : "—"}
                            </span>
                            <span className="text-[9px] uppercase tracking-[0.05em] [color:var(--text-muted)] mt-2">toss winner win rate</span>
                            <span className="text-[9px] font-data [color:var(--text-disabled)] mt-1">
                                {toss_intelligence.chose_bowl_win_pct === null
                                    ? `n=${toss_intelligence.chose_bowl_count} — insufficient`
                                    : `n=${toss_intelligence.chose_bowl_count}`}
                            </span>
                        </div>
                    </div>
                </div>
            )}

            {/* ── TOSS LOSS RECOVERY ───────────────────────── */}
            {toss_loss_recovery?.data_available && (
                <div className="p-6 [border-top:1px_solid_var(--border-subtle)]">
                    <p className="text-[10px] font-bold uppercase tracking-[0.05em] [color:var(--text-secondary)] mb-6">TOSS LOSS RECOVERY · <span className="font-data">{toss_loss_recovery.forced_bat_count + toss_loss_recovery.forced_bowl_count}</span> matches forced</p>
                    <div className="grid grid-cols-2 relative">
                        <div className="absolute left-1/2 top-0 bottom-0 w-px [background:var(--border-subtle)]" aria-hidden="true" />
                        <div className="flex flex-col items-center pr-6">
                            <span className="text-xs [color:var(--text-secondary)] mb-1">Forced to Bat</span>
                            {toss_loss_recovery.forced_bat_win_pct !== null ? (
                                <span className="text-4xl font-black font-data [color:var(--accent-ui)]"><CountUp end={toss_loss_recovery.forced_bat_win_pct} decimals={0} duration={1.0} />%</span>
                            ) : (
                                <span className="text-4xl font-black font-data [color:var(--text-disabled)]">—</span>
                            )}
                            <span className="text-[9px] uppercase tracking-[0.05em] [color:var(--text-muted)] mt-2">toss loser win rate</span>
                            <span className="text-[9px] font-data [color:var(--text-disabled)] mt-1">{toss_loss_recovery.forced_bat_win_pct === null ? `n=${toss_loss_recovery.forced_bat_count} — insufficient` : `n=${toss_loss_recovery.forced_bat_count}`}</span>
                        </div>
                        <div className="flex flex-col items-center pl-6">
                            <span className="text-xs [color:var(--text-secondary)] mb-1">Forced to Bowl</span>
                            {toss_loss_recovery.forced_bowl_win_pct !== null ? (
                                <span className="text-4xl font-black font-data [color:var(--accent-data)]"><CountUp end={toss_loss_recovery.forced_bowl_win_pct} decimals={0} duration={1.0} />%</span>
                            ) : (
                                <span className="text-4xl font-black font-data [color:var(--text-disabled)]">—</span>
                            )}
                            <span className="text-[9px] uppercase tracking-[0.05em] [color:var(--text-muted)] mt-2">toss loser win rate</span>
                            <span className="text-[9px] font-data [color:var(--text-disabled)] mt-1">{toss_loss_recovery.forced_bowl_win_pct === null ? `n=${toss_loss_recovery.forced_bowl_count} — insufficient` : `n=${toss_loss_recovery.forced_bowl_count}`}</span>
                        </div>
                    </div>
                </div>
            )}

            {/* ── LOW SAMPLE WARNING ────────────────────────── */}
            {sample_reliability === "LOW_SAMPLE" && (
                <div className="px-6 py-2 flex items-center gap-2 [background:var(--bg-caution)] [border-top:1px_solid_var(--border-caution)] [color:var(--tier-caution)]">
                    <AlertTriangle size={14} className="shrink-0" />
                    <span className="text-[10px] font-medium uppercase tracking-[0.05em]">
                        Fewer than 10 matches — treat all percentages as indicative only.
                    </span>
                </div>
            )}

        </section>
    );
}
