"use client";

import { ChevronRight, Loader2, Trash2 } from "lucide-react";
import type { TradeResponse } from "./cockpit-api";
import {
    formatPreTossOddsLabel,
    formatVenueDisplayName,
} from "./cockpit-form-helpers";

interface PendingPreTossTradesProps {
    trades: TradeResponse[];
    isLoading: boolean;
    error: string | null;
    selectedTradeId: number | null;
    isSidebarOpen: boolean;
    onToggleSidebar: () => void;
    onSelectTrade: (trade: TradeResponse) => void;
    onClearSelection: () => void;
    onDeleteTrade: (tradeId: number) => Promise<void>;
    deletingTradeId: number | null;
    deleteError: string | null;
}

function formatMatchDate(matchDate: string | null): string {
    if (!matchDate) {
        return "N/A";
    }

    const value = matchDate.split("T")[0] ?? "";
    return value || "N/A";
}

export default function PendingPreTossTrades({
    trades,
    isLoading,
    error,
    selectedTradeId,
    isSidebarOpen,
    onToggleSidebar,
    onSelectTrade,
    onClearSelection,
    onDeleteTrade,
    deletingTradeId,
    deleteError,
}: PendingPreTossTradesProps) {
    const toggleLabel = isSidebarOpen ? "Collapse pending trades" : "Expand pending trades";

    return (
        <aside className="glass-card cockpit-pending-trades">
            <div className="flex items-start justify-between gap-3">
                <div className="min-w-0">
                    <h3 className="text-sm font-bold uppercase tracking-[0.1em] text-[var(--text-primary)]">
                        Pending Pre-Toss Trades
                    </h3>
                    <p className="mt-1 text-xs leading-5 text-[var(--text-secondary)]">
                        Saved drafts waiting for toss details and post-toss odds.
                    </p>
                </div>
                <div className="flex shrink-0 items-start gap-2">
                    {selectedTradeId !== null && (
                        <button
                            type="button"
                            className="btn-ghost shrink-0 px-2 py-1 text-xs"
                            onClick={onClearSelection}
                        >
                            New trade
                        </button>
                    )}
                    <button
                        type="button"
                        className="cockpit-pending-trades-toggle"
                        aria-label={toggleLabel}
                        title={toggleLabel}
                        onClick={onToggleSidebar}
                    >
                        <ChevronRight size={14} />
                    </button>
                </div>
            </div>

            {isLoading ? (
                <p className="py-6 text-sm text-[var(--text-secondary)]">Loading drafts...</p>
            ) : error ? (
                <p className="py-6 text-sm text-[var(--tier-danger)]" role="alert">
                    {error}
                </p>
            ) : (
                <>
                    {deleteError && (
                        <p className="rounded-md border border-[var(--border-danger)] bg-[var(--bg-danger)] px-4 py-3 text-sm text-[var(--tier-danger)]" role="alert">
                            {deleteError}
                        </p>
                    )}

                    {trades.length === 0 ? (
                        <div className="rounded-md border border-dashed border-[var(--border-default)] bg-[var(--bg-base)] px-4 py-6 text-sm text-[var(--text-secondary)]">
                            No pending pre-toss trades yet.
                        </div>
                    ) : (
                        <div className="flex flex-col gap-2">
                            {trades.map((trade) => {
                                const isSelected = trade.id === selectedTradeId;
                                const isDeleting = deletingTradeId === trade.id;
                                const venueLabel = formatVenueDisplayName(trade.stadium);
                                const preTossOddsLabel = formatPreTossOddsLabel(trade);
                                return (
                                    <div
                                        key={trade.id}
                                        className={`relative overflow-hidden rounded-md border transition ${isSelected
                                            ? "border-[var(--border-accent)] bg-[var(--bg-hover)]"
                                            : "border-[var(--border-subtle)] bg-[var(--bg-base)] hover:bg-[var(--bg-hover)]"
                                            }`}
                                    >
                                        <button
                                            type="button"
                                            className="cockpit-pending-trade-card-body"
                                            disabled={isDeleting}
                                            onClick={() => onSelectTrade(trade)}
                                        >
                                            <div className="flex items-start justify-between gap-3 pr-8">
                                                <div className="min-w-0">
                                                    <p className="truncate text-sm font-semibold text-[var(--text-primary)]">
                                                        {trade.team_1} vs {trade.team_2}
                                                    </p>
                                                    <p className="cockpit-pending-trade-secondary mt-1 text-xs">
                                                        {formatMatchDate(trade.match_date)} | {venueLabel}
                                                    </p>
                                                </div>
                                                <span className="rounded-full border border-[var(--border-default)] px-2 py-0.5 text-[10px] font-bold uppercase tracking-[0.08em] text-[var(--text-secondary)]">
                                                    Draft
                                                </span>
                                            </div>

                                            <div className="mt-3 flex flex-wrap gap-2 text-xs">
                                                <span className="cockpit-pending-trade-chip rounded-full border border-[var(--border-subtle)] px-2 py-1">
                                                    {preTossOddsLabel}
                                                </span>
                                                <span className="cockpit-pending-trade-chip rounded-full border border-[var(--border-subtle)] px-2 py-1">
                                                    Bankroll {trade.bankroll.toFixed(2)}
                                                </span>
                                            </div>
                                        </button>

                                        <button
                                            type="button"
                                            className="cockpit-pending-trade-delete"
                                            aria-label={`Delete draft ${trade.team_1} vs ${trade.team_2}`}
                                            title="Delete draft"
                                            disabled={isDeleting}
                                            onClick={() => {
                                                void onDeleteTrade(trade.id);
                                            }}
                                        >
                                            {isDeleting ? <Loader2 size={12} className="animate-spin" /> : <Trash2 size={12} />}
                                        </button>
                                    </div>
                                );
                            })}
                        </div>
                    )}
                </>
            )}
        </aside>
    );
}
