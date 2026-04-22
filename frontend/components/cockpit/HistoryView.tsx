"use client";

import { useEffect, useState } from "react";
import { deleteTrade, getSummary, listTrades } from "./cockpit-api";
import { formatExecuteError } from "@/lib/executeHelpers";
import {
    HistoryErrorState,
    HistoryFiltersBar,
    HistoryLoadingState,
    HistorySummaryGrid,
    HistoryTradeTable,
    type HistoryFilterResult,
    type TradeRowRenderer,
} from "./HistoryViewSections";
import { HistoryPnlChart } from "./HistoryViewChart";
import { HistoryTradeRow } from "./HistoryTradeRow";
import type { TradeFilters, TradeResponse, TradeSummaryResponse } from "./cockpit-api";

interface HistoryViewProps {
    onViewOpenTrade: () => void;
    refreshKey?: number;
    activeFormat: string;
}

export default function HistoryView({ onViewOpenTrade, refreshKey, activeFormat }: HistoryViewProps) {
    const selectedFormat = activeFormat || undefined;
    const [trades, setTrades] = useState<TradeResponse[]>([]);
    const [summary, setSummary] = useState<TradeSummaryResponse | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [deletingId, setDeletingId] = useState<number | null>(null);

    const [filterResult, setFilterResult] = useState<HistoryFilterResult>("ALL");
    const [filterFakeF, setFilterFakeF] = useState<string>("ALL");
    const [filterSeason, setFilterSeason] = useState<string>("ALL");
    const summarySeason = filterSeason === "ALL" ? undefined : Number(filterSeason);

    async function refreshSummary(): Promise<void> {
        try {
            const summaryData = await getSummary(summarySeason, selectedFormat);
            setSummary(summaryData);
        } catch (err) {
            setError(formatExecuteError(err));
        }
    }

    useEffect(() => {
        let cancelled = false;

        setLoading(true);
        setError(null);

        const filters: TradeFilters = {};
        if (filterResult !== "ALL") {
            filters.result = filterResult;
        }
        if (filterFakeF === "YES") {
            filters.is_fake_favourite = true;
        }
        if (filterFakeF === "NO") {
            filters.is_fake_favourite = false;
        }
        if (filterSeason !== "ALL") {
            filters.season = Number(filterSeason);
        }
        if (selectedFormat) {
            filters.format = selectedFormat;
        }
        filters.status = "ACTIVE";

        Promise.all([listTrades(filters), getSummary(summarySeason, selectedFormat)])
            .then(([tradeList, summaryData]) => {
                if (cancelled) {
                    return;
                }
                setTrades(tradeList);
                setSummary(summaryData);
            })
            .catch((err) => {
                if (cancelled) {
                    return;
                }
                setError(formatExecuteError(err));
            })
            .finally(() => {
                if (cancelled) {
                    return;
                }
                setLoading(false);
            });

        return () => {
            cancelled = true;
        };
    }, [activeFormat, filterResult, filterFakeF, filterSeason, refreshKey, selectedFormat, summarySeason]);

    async function handleDelete(tradeId: number): Promise<void> {
        if (!window.confirm("Delete this trade? This cannot be undone.")) {
            return;
        }

        setDeletingId(tradeId);
        setError(null);

        try {
            await deleteTrade(tradeId);
            setTrades((prev) => prev.filter((trade) => trade.id !== tradeId));
            await refreshSummary();
        } catch (err) {
            setError(formatExecuteError(err));
        } finally {
            setDeletingId(null);
        }
    }

    const hasFilters = filterResult !== "ALL" || filterFakeF !== "ALL" || filterSeason !== "ALL";
    const renderTradeRow: TradeRowRenderer = (trade, rowNumber, isDeleting) => (
        <HistoryTradeRow
            key={trade.id}
            trade={trade}
            rowNumber={rowNumber}
            isDeleting={isDeleting}
            onView={() => onViewOpenTrade()}
            onDelete={() => handleDelete(trade.id)}
        />
    );

    if (loading) {
        return <HistoryLoadingState />;
    }

    if (error) {
        return <HistoryErrorState error={error} />;
    }

    return (
        <div className="p-4 space-y-6">
            {summary && (
                <HistorySummaryGrid summary={summary} chart={<HistoryPnlChart data={summary.running_pnl} />} />
            )}
            <HistoryFiltersBar
                filterResult={filterResult}
                filterFakeF={filterFakeF}
                filterSeason={filterSeason}
                hasFilters={hasFilters}
                onResultChange={setFilterResult}
                onFakeFChange={setFilterFakeF}
                onSeasonChange={setFilterSeason}
                onClearFilters={() => {
                    setFilterResult("ALL");
                    setFilterFakeF("ALL");
                    setFilterSeason("ALL");
                }}
            />
            <HistoryTradeTable
                trades={trades}
                deletingId={deletingId}
                renderTradeRow={renderTradeRow}
            />
        </div>
    );
}
