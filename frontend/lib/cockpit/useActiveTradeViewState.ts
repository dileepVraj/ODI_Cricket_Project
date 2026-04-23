"use client";

import { useState } from "react";
import { useActiveTradeOptionsState } from "./useActiveTradeOptionsState";
import { useActiveTradeFormState } from "./useActiveTradeFormState";

type UseActiveTradeViewStateArgs = {
    formatKey: string;
};

export function useActiveTradeViewState({ formatKey }: UseActiveTradeViewStateArgs) {
    const optionsState = useActiveTradeOptionsState({ formatKey });
    const formState = useActiveTradeFormState({
        formatKey,
        teamOptions: optionsState.teamOptions,
        venueOptions: optionsState.venueOptions,
        onTradeSaved: optionsState.refreshPendingTrades,
    });
    const [isSidebarOpen, setIsSidebarOpen] = useState(true);

    async function handleDeletePendingTrade(tradeId: number): Promise<void> {
        if (!window.confirm("Delete this draft?")) {
            return;
        }

        await optionsState.deletePendingTrade(tradeId);
        if (formState.selectedTradeId === tradeId) {
            formState.clearFormState();
        }
    }

    return {
        isSidebarOpen,
        toggleSidebar: () => setIsSidebarOpen((current) => !current),
        openSidebar: () => setIsSidebarOpen(true),
        matchSetupProps: {
            teamOptions: optionsState.teamOptions,
            awayTeamOptions: formState.awayTeamOptions,
            oddsTeamOptions: formState.oddsTeamOptions,
            venueOptions: optionsState.venueOptions,
            isLoadingTeams: optionsState.isLoadingTeams,
            isLoadingVenues: optionsState.isLoadingVenues,
            homeTeam: formState.homeTeam,
            awayTeam: formState.awayTeam,
            tossSelection: formState.tossSelection,
            venue: formState.venue,
            bankroll: formState.bankroll,
            matchDate: formState.matchDate,
            homeGround: formState.homeGround,
            oddsBeforeToss: formState.oddsBeforeToss,
            oddsAfterToss: formState.oddsAfterToss,
            canCreateTrade: formState.canCreateTrade,
            isCreating: formState.isSaving,
            createError: formState.submitError,
            createMessage: formState.submitMessage,
            submitLabel: formState.submitLabel,
            onHomeTeamChange: formState.setHomeTeam,
            onAwayTeamChange: formState.setAwayTeam,
            onTossSelectionChange: formState.setTossSelection,
            onVenueChange: formState.setVenue,
            onBankrollChange: formState.setBankroll,
            onMatchDateChange: formState.setMatchDate,
            onHomeGroundChange: formState.setHomeGround,
            onOddsBeforeTossSelectedTeamChange: formState.setOddsBeforeTossSelectedTeam,
            onOddsBeforeTossBackOddsChange: formState.setOddsBeforeTossBackOdds,
            onOddsBeforeTossLayOddsChange: formState.setOddsBeforeTossLayOdds,
            onOddsAfterTossSelectedTeamChange: formState.setOddsAfterTossSelectedTeam,
            onOddsAfterTossBackOddsChange: formState.setOddsAfterTossBackOdds,
            onOddsAfterTossLayOddsChange: formState.setOddsAfterTossLayOdds,
            onCreateTrade: formState.handleCreateTrade,
        },
        pendingTradesProps: {
            trades: optionsState.pendingTrades,
            isLoading: optionsState.isLoadingPending,
            error: optionsState.pendingError,
            selectedTradeId: formState.selectedTradeId,
            isSidebarOpen,
            onToggleSidebar: () => setIsSidebarOpen((current) => !current),
            onSelectTrade: formState.hydrateTrade,
            onClearSelection: formState.clearFormState,
            onDeleteTrade: handleDeletePendingTrade,
            deletingTradeId: optionsState.deletingTradeId,
            deleteError: optionsState.pendingDeleteError,
        },
    };
}
