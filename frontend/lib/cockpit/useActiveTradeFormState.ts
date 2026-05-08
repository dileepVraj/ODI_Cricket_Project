"use client";

import { useEffect, useState } from "react";
import { ApiClientError } from "@/lib/api";
import {
    createTrade,
    updateTrade,
    type TradeResponse,
    type VenueOption,
} from "../../components/cockpit/cockpit-api";
import {
    buildCreateTradeRequest,
    buildOddsTeamOptions,
    buildTossOptions,
    isOddsPhaseComplete,
    isTradeBasicsReady,
} from "../../components/cockpit/cockpit-form-helpers";
import type { HomeGround, OddsPhaseInput, TossSelection } from "../../components/cockpit/cockpit-types";
import { useCockpitTradeDraft } from "./CockpitTradeDraftContext";

type UseActiveTradeFormStateArgs = {
    formatKey: string;
    teamOptions: string[];
    venueOptions: VenueOption[];
    onTradeSaved: () => Promise<void>;
    onTradeExecuted?: (tradeId: number) => void;
};
export type ActiveTradeFormState = {
    selectedTradeId: number | null;
    homeTeam: string;
    awayTeam: string;
    tossSelection: TossSelection;
    season: number;
    venue: string;
    bankroll: string;
    matchDate: string;
    homeGround: HomeGround;
    oddsBeforeToss: OddsPhaseInput;
    oddsAfterToss: OddsPhaseInput;
    isSaving: boolean;
    submitError: string | null;
    submitMessage: string | null;
    awayTeamOptions: string[];
    oddsTeamOptions: string[];
    canCreateTrade: boolean;
    submitLabel: string;
    resetDraftState: () => void;
    clearFormState: () => void;
    hydrateTrade: (trade: TradeResponse) => void;
    handleCreateTrade: () => Promise<void>;
    setHomeTeam: (value: string) => void;
    setAwayTeam: (value: string) => void;
    setTossSelection: (value: TossSelection) => void;
    setVenue: (value: string) => void;
    setBankroll: (value: string) => void;
    setMatchDate: (value: string) => void;
    setHomeGround: (value: HomeGround) => void;
    setOddsBeforeTossSelectedTeam: (value: string) => void;
    setOddsBeforeTossBackOdds: (value: string) => void;
    setOddsBeforeTossLayOdds: (value: string) => void;
    setOddsAfterTossSelectedTeam: (value: string) => void;
    setOddsAfterTossBackOdds: (value: string) => void;
    setOddsAfterTossLayOdds: (value: string) => void;
};

export function useActiveTradeFormState({
    formatKey,
    teamOptions,
    venueOptions,
    onTradeSaved,
    onTradeExecuted,
}: UseActiveTradeFormStateArgs): ActiveTradeFormState {
    const selectedFormat = formatKey || "ipl";
    const {
        selectedTradeId,
        homeTeam,
        awayTeam,
        tossSelection,
        season,
        venue,
        bankroll,
        matchDate,
        homeGround,
        oddsBeforeToss,
        oddsAfterToss,
        resetDraftState,
        clearFormState,
        hydrateTrade,
        setSelectedTradeId,
        setHomeTeam,
        setAwayTeam,
        setTossSelection,
        setVenue,
        setBankroll,
        setMatchDate,
        setHomeGround,
        setOddsBeforeTossSelectedTeam,
        setOddsBeforeTossBackOdds,
        setOddsBeforeTossLayOdds,
        setOddsAfterTossSelectedTeam,
        setOddsAfterTossBackOdds,
        setOddsAfterTossLayOdds,
    } = useCockpitTradeDraft();
    const [isSaving, setIsSaving] = useState(false);
    const [submitError, setSubmitError] = useState<string | null>(null);
    const [submitMessage, setSubmitMessage] = useState<string | null>(null);

    useEffect(() => {
        setIsSaving(false);
        setSubmitError(null);
        setSubmitMessage(null);
    }, [selectedFormat]);

    useEffect(() => {
        if (teamOptions.length === 0) {
            return;
        }

        if (homeTeam !== "" && !teamOptions.includes(homeTeam)) {
            setHomeTeam("");
        }
        if (awayTeam !== "" && !teamOptions.includes(awayTeam)) {
            setAwayTeam("");
        }
    }, [awayTeam, homeTeam, setAwayTeam, setHomeTeam, teamOptions]);

    useEffect(() => {
        if (venue !== "" && !venueOptions.some((option) => option.id === venue)) {
            setVenue("");
        }
    }, [setVenue, venue, venueOptions]);

    useEffect(() => {
        if (homeTeam !== "" && awayTeam === homeTeam) {
            setAwayTeam("");
        }

        const tossOptions = buildTossOptions(homeTeam, awayTeam);
        if (tossSelection !== "" && !tossOptions.includes(tossSelection)) {
            setTossSelection("");
        }
    }, [awayTeam, homeTeam, setAwayTeam, setTossSelection, tossSelection]);

    useEffect(() => {
        const oddsTeamOptions = buildOddsTeamOptions(homeTeam, awayTeam);
        const firstTeam = oddsTeamOptions[0] ?? "";

        if (firstTeam !== "" && oddsBeforeToss.selectedTeam === "") {
            setOddsBeforeTossSelectedTeam(firstTeam);
        } else if (oddsBeforeToss.selectedTeam !== "" && !oddsTeamOptions.includes(oddsBeforeToss.selectedTeam)) {
            setOddsBeforeTossSelectedTeam(firstTeam);
        }

        if (firstTeam !== "" && oddsAfterToss.selectedTeam === "") {
            setOddsAfterTossSelectedTeam(firstTeam);
        } else if (oddsAfterToss.selectedTeam !== "" && !oddsTeamOptions.includes(oddsAfterToss.selectedTeam)) {
            setOddsAfterTossSelectedTeam(firstTeam);
        }
    }, [
        awayTeam,
        homeTeam,
        oddsAfterToss.selectedTeam,
        oddsBeforeToss.selectedTeam,
        setOddsAfterTossSelectedTeam,
        setOddsBeforeTossSelectedTeam,
    ]);

    async function handleCreateTrade(): Promise<void> {
        const tradePayload = buildCreateTradeRequest({
            bankroll,
            awayTeam,
            homeTeam,
            homeGround,
            matchDate,
            oddsBeforeToss,
            oddsAfterToss,
            season,
            tossSelection,
            venue,
        });

        if (tradePayload === null) {
            setSubmitError("Enter a valid bankroll amount before saving.");
            return;
        }

        if (!isTradeBasicsReady(homeTeam, awayTeam, venue, bankroll, oddsBeforeToss)) {
            setSubmitError("Fill in the pre-toss details before saving the trade.");
            return;
        }

        setIsSaving(true);
        setSubmitError(null);
        setSubmitMessage(null);

        try {
            const savedTrade = selectedTradeId === null
                ? await createTrade(tradePayload, selectedFormat)
                : await updateTrade(selectedTradeId, tradePayload, selectedFormat);

            setSelectedTradeId(savedTrade.id);
            await onTradeSaved();
            const executeReady = tossSelection !== "" && isOddsPhaseComplete(oddsAfterToss);
            if (executeReady && onTradeExecuted) {
                onTradeExecuted(savedTrade.id);
                return;
            }
            setSubmitMessage(
                savedTrade.status === "ACTIVE"
                    ? `Trade ${savedTrade.id} is active now.`
                    : `Draft ${savedTrade.id} saved.`
            );
        } catch (err) {
            if (err instanceof ApiClientError && err.message.includes("Insufficient Wallet Funds")) {
                setSubmitError("Wallet balance too low. Top up your wallet first.");
            } else {
                setSubmitError("Failed to save the trade. Please try again.");
            }
        } finally {
            setIsSaving(false);
        }
    }

    const awayTeamOptions = homeTeam === "" ? teamOptions : teamOptions.filter((team) => team !== homeTeam);
    const oddsTeamOptions = buildOddsTeamOptions(homeTeam, awayTeam);
    const hasBaseTradeInfo = isTradeBasicsReady(homeTeam, awayTeam, venue, bankroll, oddsBeforeToss);
    const canCreateTrade = hasBaseTradeInfo && !isSaving;
    const isExecuteReady = tossSelection !== "" && isOddsPhaseComplete(oddsAfterToss);
    const submitLabel = isExecuteReady ? "Execute Trade" : "Save Pre-Toss";

    return {
        selectedTradeId,
        homeTeam,
        awayTeam,
        tossSelection,
        season,
        venue,
        bankroll,
        matchDate,
        homeGround,
        oddsBeforeToss,
        oddsAfterToss,
        isSaving,
        submitError,
        submitMessage,
        awayTeamOptions,
        oddsTeamOptions,
        canCreateTrade,
        submitLabel,
        resetDraftState,
        clearFormState,
        hydrateTrade,
        handleCreateTrade,
        setHomeTeam,
        setAwayTeam,
        setTossSelection,
        setVenue,
        setBankroll,
        setMatchDate,
        setHomeGround,
        setOddsBeforeTossSelectedTeam,
        setOddsBeforeTossBackOdds,
        setOddsBeforeTossLayOdds,
        setOddsAfterTossSelectedTeam,
        setOddsAfterTossBackOdds,
        setOddsAfterTossLayOdds,
    };
}
