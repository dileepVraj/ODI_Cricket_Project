"use client";

import type { TradeResponse } from "./cockpit-api";

interface PendingPreTossTradesProps {
    trades: TradeResponse[];
    isLoading: boolean;
    error: string | null;
    selectedTradeId: number | null;
    onSelectTrade: (trade: TradeResponse) => void;
    onClearSelection: () => void;
}

function formatMatchDate(matchDate: string | null): string {
    if (!matchDate) {
        return "N/A";
    }

    const value = matchDate.split("T")[0] ?? "";
    return value || "N/A";
}

function formatOdds(value: number | null): string {
    if (value === null) {
        return "N/A";
    }
    return value.toFixed(2);
}

export default function PendingPreTossTrades({
    trades,
    isLoading,
    error,
    selectedTradeId,
    onSelectTrade,
    onClearSelection,
}: PendingPreTossTradesProps) {
    return (
        <aside className="glass-card flex flex-col gap-4 p-5">
            <div className="flex items-start justify-between gap-3">
                <div className="min-w-0">
                    <h3 className="text-sm font-bold uppercase tracking-[0.1em] text-[var(--text-primary)]">
                        Pending Pre-Toss Trades
                    </h3>
                    <p className="mt-1 text-xs leading-5 text-[var(--text-secondary)]">
                        Saved drafts waiting for toss details and post-toss odds.
                    </p>
                </div>
                {selectedTradeId !== null && (
                    <button
                        type="button"
                        className="btn-ghost shrink-0 px-2 py-1 text-xs"
                        onClick={onClearSelection}
                    >
                        New trade
                    </button>
                )}
            </div>

            {isLoading ? (
                <p className="py-6 text-sm text-[var(--text-secondary)]">Loading drafts...</p>
            ) : error ? (
                <p className="py-6 text-sm text-[var(--tier-danger)]" role="alert">
                    {error}
                </p>
            ) : trades.length === 0 ? (
                <div className="rounded-md border border-dashed border-[var(--border-default)] bg-[var(--bg-base)] px-4 py-6 text-sm text-[var(--text-secondary)]">
                    No pending pre-toss trades yet.
                </div>
            ) : (
                <div className="flex flex-col gap-2">
                    {trades.map((trade) => {
                        const isSelected = trade.id === selectedTradeId;
                        return (
                            <button
                                key={trade.id}
                                type="button"
                                className={`w-full rounded-md border px-3 py-3 text-left transition ${isSelected
                                    ? "border-[var(--border-accent)] bg-[var(--bg-hover)]"
                                    : "border-[var(--border-subtle)] bg-[var(--bg-base)] hover:bg-[var(--bg-hover)]"
                                    }`}
                                onClick={() => onSelectTrade(trade)}
                            >
                                <div className="flex items-start justify-between gap-3">
                                    <div className="min-w-0">
                                        <p className="truncate text-sm font-semibold text-[var(--text-primary)]">
                                            {trade.team_1} vs {trade.team_2}
                                        </p>
                                        <p className="mt-1 text-xs text-[var(--text-secondary)]">
                                            {formatMatchDate(trade.match_date)} | {trade.stadium}
                                        </p>
                                    </div>
                                    <span className="rounded-full border border-[var(--border-default)] px-2 py-0.5 text-[10px] font-bold uppercase tracking-[0.08em] text-[var(--text-secondary)]">
                                        Draft
                                    </span>
                                </div>

                                <div className="mt-3 flex flex-wrap gap-2 text-xs text-[var(--text-secondary)]">
                                    <span className="rounded-full border border-[var(--border-subtle)] px-2 py-1">
                                        Pre-toss {formatOdds(trade.opening_odds)}
                                    </span>
                                    <span className="rounded-full border border-[var(--border-subtle)] px-2 py-1">
                                        Bankroll {trade.bankroll.toFixed(2)}
                                    </span>
                                </div>
                            </button>
                        );
                    })}
                </div>
            )}
        </aside>
    );
}
