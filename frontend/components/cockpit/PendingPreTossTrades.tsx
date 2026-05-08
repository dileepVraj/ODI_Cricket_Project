"use client";

import { useMemo } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { ChevronLeft, ChevronRight, Loader2, Trash2 } from "lucide-react";
import type { TradeResponse } from "./cockpit-api";
import { formatVenueDisplayName } from "./cockpit-form-helpers";
import CockpitTeamText from "./CockpitTeamText";

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

function PreTossOddsLabel({ trade }: { trade: TradeResponse }) {
    const selectedTeam = trade.selected_team_before_toss?.trim() ?? "";
    if (
        selectedTeam !== ""
        && trade.back_odds_before_toss !== null
        && trade.lay_odds_before_toss !== null
    ) {
        return (
            <>
                Pre-toss: <CockpitTeamText team={selectedTeam} /> {trade.back_odds_before_toss}/{trade.lay_odds_before_toss}
            </>
        );
    }

    if (trade.opening_odds !== null) {
        return <>Pre-toss {trade.opening_odds.toFixed(2)}</>;
    }

    return <>Pre-toss: Pending</>;
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
    const router = useRouter();
    const searchParams = useSearchParams();
    const formatKey = searchParams.get("format") ?? "ipl";
    const tradeBody = useMemo(() => {
        if (isLoading) {
            return <p className="py-6 text-sm text-[var(--text-secondary)]">Loading drafts...</p>;
        }

        if (error) {
            return (
                <p className="py-6 text-sm text-[var(--tier-danger)]" role="alert">
                    {error}
                </p>
            );
        }

        return (
            <>
                {deleteError && (
                    <p
                        className="rounded-md border border-[var(--border-danger)] bg-[var(--bg-danger)] px-4 py-3 text-sm text-[var(--tier-danger)]"
                        role="alert"
                    >
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
                            const isActive = trade.status === "ACTIVE";
                            const venueLabel = formatVenueDisplayName(trade.stadium);

                            return (
                                <div
                                    key={trade.id}
                                    className={`relative overflow-hidden rounded-md border transition ${isActive
                                        ? "border-[var(--border-elite)] bg-[var(--bg-elevated)]"
                                        : isSelected
                                            ? "border-[var(--border-accent)] bg-[var(--bg-hover)]"
                                            : "border-[var(--border-subtle)] bg-[var(--bg-base)] hover:bg-[var(--bg-hover)]"
                                        }`}
                                >
                                    <button
                                        type="button"
                                        className="cockpit-pending-trade-card-body"
                                        disabled={isDeleting}
                                        onClick={() => {
                                            if (isActive) {
                                                router.push(`/trading-dashboard/${trade.id}?format=${encodeURIComponent(formatKey)}`);
                                                return;
                                            }

                                            onSelectTrade(trade);
                                        }}
                                    >
                                        <div className="flex items-start justify-between gap-3 pr-8">
                                            <div className="min-w-0">
                                                <p className="truncate text-sm font-semibold text-[var(--text-primary)]">
                                                    <CockpitTeamText team={trade.team_1} /> vs <CockpitTeamText team={trade.team_2} />
                                                </p>
                                                <p className="cockpit-pending-trade-secondary mt-1 text-xs">
                                                    {formatMatchDate(trade.match_date)} | {venueLabel}
                                                </p>
                                            </div>
                                            <span
                                                className={`rounded-full border px-2 py-0.5 text-[10px] font-bold uppercase tracking-[0.08em] ${isActive
                                                    ? "border-[var(--border-elite)] text-[var(--tier-elite)]"
                                                    : "border-[var(--border-default)] text-[var(--text-secondary)]"
                                                    }`}
                                            >
                                                {isActive ? "LIVE" : "Draft"}
                                            </span>
                                        </div>

                                        <div className="mt-3 flex flex-wrap gap-2 text-xs">
                                            <span className="cockpit-pending-trade-chip rounded-full border border-[var(--border-subtle)] px-2 py-1">
                                                <PreTossOddsLabel trade={trade} />
                                            </span>
                                            <span className="cockpit-pending-trade-chip rounded-full border border-[var(--border-subtle)] px-2 py-1">
                                                Bankroll {trade.bankroll.toFixed(2)}
                                            </span>
                                            {isActive && (
                                                <span className="inline-flex items-center gap-1 rounded-full border border-[var(--border-elite)] px-2 py-1 text-[10px] font-bold uppercase tracking-[0.08em] text-[var(--tier-elite)]">
                                                    <span
                                                        className="inline-block h-2 w-2 rounded-full bg-[var(--tier-elite)] animate-pulse-dot"
                                                        aria-hidden="true"
                                                    />
                                                    LIVE
                                                </span>
                                            )}
                                        </div>
                                    </button>

                                    <button
                                        type="button"
                                        className="cockpit-pending-trade-delete"
                                        aria-label={`${isActive ? "Delete live trade" : "Delete draft"} ${trade.team_1} vs ${trade.team_2}`}
                                        title={isActive ? "Delete live trade" : "Delete draft"}
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
        );
    }, [
        deletingTradeId,
        deleteError,
        error,
        formatKey,
        isLoading,
        onDeleteTrade,
        onSelectTrade,
        router,
        selectedTradeId,
        trades,
    ]);

    return (
        <aside className={`glass-card cockpit-pending-trades${isSidebarOpen ? "" : " cockpit-pending-trades--collapsed"}`}>
            <div className="cockpit-pending-trades__chrome">
                <div className={`min-w-0 ${isSidebarOpen ? "cockpit-pending-trades__chrome-meta" : "cockpit-pending-trades__chrome-meta cockpit-pending-trades__chrome-meta--hidden"}`}>
                    <h3 className="text-sm font-bold uppercase tracking-[0.1em] text-[var(--text-primary)]">
                        Pending Pre-Toss Trades
                    </h3>
                    <p className="mt-1 text-xs leading-5 text-[var(--text-secondary)]">
                        Saved drafts waiting for toss details and post-toss odds.
                    </p>
                </div>

                <div className="flex shrink-0 items-start gap-2">
                    {isSidebarOpen && selectedTradeId !== null && (
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
                        aria-label={isSidebarOpen ? "Collapse pending trades" : "Expand pending trades"}
                        title={isSidebarOpen ? "Collapse pending trades" : "Expand pending trades"}
                        onClick={onToggleSidebar}
                    >
                        {isSidebarOpen ? <ChevronLeft size={14} /> : <ChevronRight size={14} />}
                    </button>
                </div>
            </div>

            <div className="cockpit-pending-trades__content" hidden={!isSidebarOpen} aria-hidden={!isSidebarOpen}>
                {tradeBody}
            </div>
        </aside>
    );
}
