"use client";

import { useRouter } from "next/navigation";
import { ChevronRight, Pencil, Trash2 } from "lucide-react";
import EmptyState from "@/components/common/EmptyState";
import CockpitTeamText from "./CockpitTeamText";
import type { HistoryTradeResponse } from "@/lib/cockpit/history-api";
import {
    formatDate,
    formatProfit,
    formatSentimentLabel,
    formatVolume,
    formatYield,
    getProfitClass,
    getSentimentClass,
    getTradeSortStamp,
    getWinnerAcronym,
} from "./history-dashboard-utils";
import {
    HistoryTradeTableErrorRow,
    HistoryTradeTableExpandedRow,
    HistoryTradeTableLoadingRows,
} from "./HistoryTradeTableParts";
import type { BetResponse } from "@/lib/cockpit/live-trade-bets-api";

interface HistoryTradeTableProps {
    trades: HistoryTradeResponse[];
    isLoadingTrades: boolean;
    error: string | null;
    expandedTradeId: number | null;
    betsByTradeId: Record<number, BetResponse[]>;
    betErrorByTradeId: Record<number, string | null>;
    loadingBetTradeId: number | null;
    deletingTradeId: number | null;
    showFormatLabel: boolean;
    hasFilters: boolean;
    onTradeClick: (tradeId: number) => void;
    onDeleteTrade: (trade: HistoryTradeResponse) => Promise<void>;
}

export default function HistoryTradeTable({
    trades,
    isLoadingTrades,
    error,
    expandedTradeId,
    betsByTradeId,
    betErrorByTradeId,
    loadingBetTradeId,
    deletingTradeId,
    showFormatLabel,
    hasFilters,
    onTradeClick,
    onDeleteTrade,
}: HistoryTradeTableProps) {
    const router = useRouter();
    const orderedTrades = [...trades].sort((left, right) => {
        const rightStamp = getTradeSortStamp(right);
        const leftStamp = getTradeSortStamp(left);
        if (rightStamp !== leftStamp) {
            return rightStamp - leftStamp;
        }
        return right.id - left.id;
    });

    return (
        <div className="mx-auto overflow-hidden rounded-none bg-slate-950 shadow-2xl shadow-black/20 ring-1 ring-slate-800/80">
            <div className="flex items-center justify-between gap-4 border-b border-slate-800 bg-slate-900/90 px-6 py-4">
                <div>
                    <p className="text-[9px] font-black uppercase tracking-[0.24em] dashboard-hero-rainbow">Trade History</p>
                    <p className="mt-1 text-sm text-slate-300">
                        Click a row to inspect the settled bets behind each result.
                    </p>
                </div>
                <div className="flex items-center gap-3">
                    {showFormatLabel ? <span className="badge badge-format">Mixed formats</span> : null}
                    <div className="flex items-center gap-4">
                        <div className="flex items-center gap-1.5">
                            <span className="h-2 w-2 rounded-full bg-emerald-400" />
                            <span className="text-[10px] font-bold uppercase tracking-[0.2em] text-emerald-300">Profit</span>
                        </div>
                        <div className="flex items-center gap-1.5">
                            <span className="h-2 w-2 rounded-full bg-rose-400" />
                            <span className="text-[10px] font-bold uppercase tracking-[0.2em] text-rose-300">Loss</span>
                        </div>
                    </div>
                </div>
            </div>

            <div className="overflow-x-auto">
                <table className="min-w-[860px] w-full border-collapse text-left">
                    <colgroup>
                        <col style={{ width: "10%" }} />
                        <col style={{ width: "13%" }} />
                        <col style={{ width: "8%" }} />
                        <col style={{ width: "12%" }} />
                        <col style={{ width: "12%" }} />
                        <col style={{ width: "12%" }} />
                        <col style={{ width: "7%" }} />
                        <col style={{ width: "10%" }} />
                        {showFormatLabel ? <col style={{ width: "7%" }} /> : null}
                        <col style={{ width: "9%" }} />
                    </colgroup>
                    <thead className="bg-slate-950/95">
                        <tr className="border-b border-slate-800 text-[9px] font-black uppercase tracking-[0.18em]">
                            <th className="whitespace-nowrap py-3.5 pl-6 pr-5 text-slate-400">Date</th>
                            <th className="whitespace-nowrap px-5 py-3.5 text-cyan-300">Match</th>
                            <th className="whitespace-nowrap px-5 py-3.5 text-amber-300">Winner</th>
                            <th className="whitespace-nowrap px-5 py-3.5 text-right text-sky-300">Volume</th>
                            <th className="whitespace-nowrap px-5 py-3.5 text-right text-emerald-300">Net Profit</th>
                            <th className="whitespace-nowrap px-5 py-3.5 text-right text-teal-300">Target Profit</th>
                            <th className="whitespace-nowrap px-5 py-3.5 text-right text-violet-300">Yield</th>
                            <th className="whitespace-nowrap px-5 py-3.5 text-center text-fuchsia-300">Sentiment</th>
                            {showFormatLabel ? <th className="whitespace-nowrap px-5 py-3.5 text-center text-cyan-300">Format</th> : null}
                            <th className="px-5 py-3.5" />
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800/60">
                        {isLoadingTrades ? (
                            <HistoryTradeTableLoadingRows showFormatLabel={showFormatLabel} />
                        ) : error ? (
                            <HistoryTradeTableErrorRow message={error} showFormatLabel={showFormatLabel} />
                        ) : orderedTrades.length === 0 ? (
                            <tr>
                                <td colSpan={showFormatLabel ? 10 : 9} className="px-4 py-12">
                                    <EmptyState
                                        title={hasFilters ? "No matches found" : "No settled trades yet"}
                                        message={hasFilters ? "No settled trades match your current filters." : "Completed matches will appear here after they are settled."}
                                    />
                                </td>
                            </tr>
                        ) : (
                            orderedTrades.flatMap((trade) => {
                                const isExpanded = expandedTradeId === trade.id;
                                const isLoadingBets = loadingBetTradeId === trade.id && !betsByTradeId[trade.id];
                                const tradeError = betErrorByTradeId[trade.id] ?? null;
                                const bets = betsByTradeId[trade.id] ?? [];
                                const isVoided = trade.status === "VOID";
                                const isDeleting = deletingTradeId === trade.id;
                                const winner = getWinnerAcronym(trade);
                                const team1 = trade.team_1.trim() || "--";
                                const team2 = trade.team_2.trim() || "--";

                                return [
                                    <tr
                                        key={trade.id}
                                        role="button"
                                        tabIndex={0}
                                        aria-expanded={isExpanded}
                                        aria-controls={`history-bets-${trade.id}`}
                                        onClick={() => onTradeClick(trade.id)}
                                        onKeyDown={(event) => {
                                            if (event.key === "Enter" || event.key === " ") {
                                                event.preventDefault();
                                                onTradeClick(trade.id);
                                            }
                                        }}
                                        className={`group cursor-pointer transition-colors hover:bg-slate-900/70 ${
                                            isExpanded ? "bg-slate-900/80" : ""
                                        }`}
                                    >
                                        <td className="whitespace-nowrap py-4 pl-6 pr-5 text-xs font-medium text-slate-400">
                                            {formatDate(trade.match_date ?? trade.updated_at)}
                                        </td>
                                        <td className="px-5 py-4">
                                            <div className="flex min-w-0 items-center gap-2 text-sm font-bold tracking-tight">
                                                <CockpitTeamText team={team1} className="text-sm font-bold tracking-tight" />
                                                <span className="text-slate-600">v</span>
                                                <CockpitTeamText team={team2} className="text-sm font-bold tracking-tight" />
                                            </div>
                                        </td>
                                        <td className="whitespace-nowrap px-5 py-4 text-xs font-bold">
                                            {trade.winner === "team_1" ? (
                                                <CockpitTeamText team={trade.team_1} className="text-xs font-bold tracking-tight" />
                                            ) : trade.winner === "team_2" ? (
                                                <CockpitTeamText team={trade.team_2} className="text-xs font-bold tracking-tight" />
                                            ) : (
                                                <span className="text-slate-400">{winner}</span>
                                            )}
                                        </td>
                                        <td className="whitespace-nowrap px-5 py-4 text-right text-sm font-medium tracking-tight text-slate-100">
                                            {formatVolume(trade.total_volume_wagered)}
                                        </td>
                                        <td className={`whitespace-nowrap px-5 py-4 text-right text-sm font-black tracking-tight ${getProfitClass(trade.actual_profit)}`}>
                                            {formatProfit(trade.actual_profit)}
                                        </td>
                                        <td className={`whitespace-nowrap px-5 py-4 text-right text-sm font-black tracking-tight ${getProfitClass(trade.targeted_pnl)}`}>
                                            {formatProfit(trade.targeted_pnl)}
                                        </td>
                                        {isVoided ? (
                                            <>
                                                <td className="px-5 py-4" />
                                                <td className="px-5 py-4 text-center">
                                                    <span className="inline-flex rounded-full border border-slate-700 bg-slate-800 px-2.5 py-1 text-[10px] font-black uppercase tracking-tighter text-slate-400">
                                                        VOID
                                                    </span>
                                                </td>
                                            </>
                                        ) : (
                                            <>
                                                <td className="whitespace-nowrap px-5 py-4 text-right text-xs font-bold tracking-tight text-slate-100">
                                                    {formatYield(trade.achieved_yield_percentage)}
                                                </td>
                                                <td className="px-5 py-4 text-center">
                                                    <span
                                                        className={`inline-flex rounded-full px-2.5 py-1 text-[10px] font-black uppercase tracking-tighter ${getSentimentClass(
                                                            trade.trade_sentiment,
                                                        )}`}
                                                    >
                                                        {formatSentimentLabel(trade.trade_sentiment)}
                                                    </span>
                                                </td>
                                            </>
                                        )}
                                        {showFormatLabel ? (
                                            <td className="px-5 py-4 text-center">
                                                <span className="badge badge-format px-2.5 py-0.5 text-[10px]">
                                                    {trade.format_label}
                                                </span>
                                            </td>
                                        ) : null}
                                        <td className="px-5 py-4 text-right text-slate-500 transition-colors group-hover:text-slate-100">
                                            <div className="flex items-center justify-end gap-2">
                                                {!isVoided && (
                                                    <button
                                                        type="button"
                                                        className="inline-flex h-8 w-8 items-center justify-center rounded-full bg-slate-900/80 ring-1 ring-slate-700/80 transition hover:bg-cyan-500/10 hover:text-cyan-300 hover:ring-cyan-500/30"
                                                        aria-label={`Edit settlement for ${team1} vs ${team2}`}
                                                        title="Edit settlement"
                                                        onClick={(event) => {
                                                            event.stopPropagation();
                                                            router.push(`/trading-dashboard/${trade.id}/settle?format=${encodeURIComponent(trade.format_key)}&edit=1`);
                                                        }}
                                                    >
                                                        <Pencil size={14} aria-hidden="true" />
                                                    </button>
                                                )}
                                                <button
                                                    type="button"
                                                    className="inline-flex h-8 w-8 items-center justify-center rounded-full bg-slate-900/80 ring-1 ring-slate-700/80 transition hover:bg-rose-500/10 hover:text-rose-300 hover:ring-rose-500/30 disabled:cursor-not-allowed disabled:opacity-50"
                                                    aria-label={`Delete trade for ${team1} vs ${team2}`}
                                                    title="Delete trade"
                                                    disabled={isDeleting}
                                                    onClick={(event) => {
                                                        event.stopPropagation();
                                                        void onDeleteTrade(trade);
                                                    }}
                                                >
                                                    <Trash2 size={16} aria-hidden="true" />
                                                </button>
                                                <span className="inline-flex h-8 w-8 items-center justify-center rounded-full bg-slate-900/80 ring-1 ring-slate-700/80">
                                                    <ChevronRight
                                                        size={18}
                                                        className={`transition-transform ${isExpanded ? "rotate-90" : ""}`}
                                                        aria-hidden="true"
                                                    />
                                                </span>
                                            </div>
                                        </td>
                                    </tr>,
                                    isExpanded ? (
                                        <HistoryTradeTableExpandedRow
                                            key={`${trade.id}-expanded`}
                                            trade={trade}
                                            bets={bets}
                                            tradeError={tradeError}
                                            isLoadingBets={isLoadingBets}
                                            showFormatLabel={showFormatLabel}
                                        />
                                    ) : null,
                                ];
                            })
                        )}
                    </tbody>
                </table>
            </div>
            <div className="flex items-center justify-between gap-4 bg-slate-900/80 px-6 py-3.5">
                <div className="text-[10px] font-bold uppercase tracking-[0.22em] text-slate-400">
                    {isLoadingTrades
                        ? "Loading settled trades..."
                        : orderedTrades.length > 0
                            ? `Showing 1-${orderedTrades.length} of ${orderedTrades.length} trades`
                            : "No settled trades yet"}
                </div>
                <div className="text-[10px] font-bold uppercase tracking-[0.22em] dashboard-hero-rainbow">
                    Newest first
                </div>
            </div>
        </div>
    );
}
