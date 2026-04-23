"use client";

import { useEffect, useState } from "react";
import {
    deleteTrade,
    fetchCockpitTeams,
    fetchCockpitVenues,
    listTrades,
    type TradeResponse,
    type VenueOption,
} from "../../components/cockpit/cockpit-api";

type UseActiveTradeOptionsStateArgs = {
    formatKey: string;
};

export type ActiveTradeOptionsState = {
    teamOptions: string[];
    venueOptions: VenueOption[];
    isLoadingTeams: boolean;
    isLoadingVenues: boolean;
    isLoadingPending: boolean;
    pendingError: string | null;
    pendingDeleteError: string | null;
    deletingTradeId: number | null;
    pendingTrades: TradeResponse[];
    refreshPendingTrades: () => Promise<void>;
    deletePendingTrade: (tradeId: number) => Promise<void>;
};

export function useActiveTradeOptionsState({ formatKey }: UseActiveTradeOptionsStateArgs): ActiveTradeOptionsState {
    const selectedFormat = formatKey || "ipl";

    const [teamOptions, setTeamOptions] = useState<string[]>([]);
    const [venueOptions, setVenueOptions] = useState<VenueOption[]>([]);
    const [isLoadingTeams, setIsLoadingTeams] = useState(false);
    const [isLoadingVenues, setIsLoadingVenues] = useState(false);
    const [isLoadingPending, setIsLoadingPending] = useState(false);
    const [pendingError, setPendingError] = useState<string | null>(null);
    const [pendingDeleteError, setPendingDeleteError] = useState<string | null>(null);
    const [deletingTradeId, setDeletingTradeId] = useState<number | null>(null);
    const [pendingTrades, setPendingTrades] = useState<TradeResponse[]>([]);

    useEffect(() => {
        let cancelled = false;

        if (!selectedFormat) {
            setTeamOptions([]);
            setIsLoadingTeams(false);
            return () => {
                cancelled = true;
            };
        }

        setTeamOptions([]);
        setIsLoadingTeams(true);
        fetchCockpitTeams(selectedFormat)
            .then((loadedTeams) => {
                if (!cancelled) {
                    setTeamOptions(loadedTeams);
                }
            })
            .catch(() => {
                if (!cancelled) {
                    setTeamOptions([]);
                }
            })
            .finally(() => {
                if (!cancelled) {
                    setIsLoadingTeams(false);
                }
            });

        return () => {
            cancelled = true;
        };
    }, [selectedFormat]);

    useEffect(() => {
        let cancelled = false;

        if (!selectedFormat) {
            setVenueOptions([]);
            setIsLoadingVenues(false);
            return () => {
                cancelled = true;
            };
        }

        setVenueOptions([]);
        setIsLoadingVenues(true);
        fetchCockpitVenues(selectedFormat)
            .then((loadedVenues) => {
                if (!cancelled) {
                    setVenueOptions(loadedVenues);
                }
            })
            .catch(() => {
                if (!cancelled) {
                    setVenueOptions([]);
                }
            })
            .finally(() => {
                if (!cancelled) {
                    setIsLoadingVenues(false);
                }
            });

        return () => {
            cancelled = true;
        };
    }, [selectedFormat]);

    useEffect(() => {
        let cancelled = false;

        if (!selectedFormat) {
            setPendingTrades([]);
            setPendingError(null);
            setIsLoadingPending(false);
            return () => {
                cancelled = true;
            };
        }

        setIsLoadingPending(true);
        setPendingError(null);
        listTrades({ format: selectedFormat, status: "DRAFT" })
            .then((loadedTrades) => {
                if (!cancelled) {
                    setPendingTrades(loadedTrades);
                }
            })
            .catch(() => {
                if (!cancelled) {
                    setPendingTrades([]);
                    setPendingError("Could not load pending drafts.");
                }
            })
            .finally(() => {
                if (!cancelled) {
                    setIsLoadingPending(false);
                }
            });

        return () => {
            cancelled = true;
        };
    }, [selectedFormat]);

    async function refreshPendingTrades(): Promise<void> {
        try {
            const loadedTrades = await listTrades({ format: selectedFormat, status: "DRAFT" });
            setPendingTrades(loadedTrades);
            setPendingError(null);
        } catch {
            setPendingTrades([]);
            setPendingError("Could not load pending drafts.");
        }
    }

    async function deletePendingTrade(tradeId: number): Promise<void> {
        setDeletingTradeId(tradeId);
        setPendingDeleteError(null);

        try {
            await deleteTrade(tradeId);
            setPendingTrades((current) => current.filter((trade) => trade.id !== tradeId));
        } catch {
            setPendingDeleteError("Could not delete the draft. Please try again.");
        } finally {
            setDeletingTradeId(null);
        }
    }

    return {
        teamOptions,
        venueOptions,
        isLoadingTeams,
        isLoadingVenues,
        isLoadingPending,
        pendingError,
        pendingDeleteError,
        deletingTradeId,
        pendingTrades,
        refreshPendingTrades,
        deletePendingTrade,
    };
}
