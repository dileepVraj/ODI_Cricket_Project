"use client";

import { useEffect, useState } from "react";
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
    EMPTY_ODDS_PHASE_INPUT,
    formatMatchDateInput,
    getDefaultSeason,
    isOddsPhaseComplete,
    parsePositiveAmount,
    resolveTossSelection,
} from "../../components/cockpit/cockpit-form-helpers";
import type { HomeGround, OddsPhaseInput, TossSelection } from "../../components/cockpit/cockpit-types";
const DEFAULT_BANKROLL = "100";

type UseActiveTradeFormStateArgs = {
    formatKey: string;
    teamOptions: string[];
    venueOptions: VenueOption[];
    onTradeSaved: () => Promise<void>;
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
function isTradeBasicsReady(
    homeTeam: string,
    awayTeam: string,
    venue: string,
    bankroll: string,
    oddsBeforeToss: OddsPhaseInput
): boolean {
    return homeTeam !== ""
        && awayTeam !== ""
        && venue !== ""
        && parsePositiveAmount(bankroll) !== null
        && isOddsPhaseComplete(oddsBeforeToss);
}
export function useActiveTradeFormState({
    formatKey,
    teamOptions,
    venueOptions,
    onTradeSaved,
}: UseActiveTradeFormStateArgs): ActiveTradeFormState {
    const selectedFormat = formatKey || "ipl";
    const defaultSeason = getDefaultSeason(selectedFormat);

    const [selectedTradeId, setSelectedTradeId] = useState<number | null>(null);
    const [homeTeam, setHomeTeam] = useState("");
    const [awayTeam, setAwayTeam] = useState("");
    const [tossSelection, setTossSelection] = useState<TossSelection>("");
    const [season, setSeason] = useState(() => defaultSeason);
    const [venue, setVenue] = useState("");
    const [bankroll, setBankroll] = useState(DEFAULT_BANKROLL);
    const [matchDate, setMatchDate] = useState("");
    const [oddsBeforeToss, setOddsBeforeToss] = useState<OddsPhaseInput>(EMPTY_ODDS_PHASE_INPUT);
    const [oddsAfterToss, setOddsAfterToss] = useState<OddsPhaseInput>(EMPTY_ODDS_PHASE_INPUT);
    const [homeGround, setHomeGround] = useState<HomeGround>("NEU");
    const [isSaving, setIsSaving] = useState(false);
    const [submitError, setSubmitError] = useState<string | null>(null);
    const [submitMessage, setSubmitMessage] = useState<string | null>(null);

    useEffect(() => {
        setSelectedTradeId(null);
        setHomeTeam("");
        setAwayTeam("");
        setTossSelection("");
        setSeason(defaultSeason);
        setVenue("");
        setBankroll(DEFAULT_BANKROLL);
        setMatchDate("");
        setOddsBeforeToss(EMPTY_ODDS_PHASE_INPUT);
        setOddsAfterToss(EMPTY_ODDS_PHASE_INPUT);
        setHomeGround("NEU");
        setIsSaving(false);
        setSubmitError(null);
        setSubmitMessage(null);
    }, [defaultSeason, selectedFormat]);

    useEffect(() => {
        if (homeTeam !== "" && !teamOptions.includes(homeTeam)) {
            setHomeTeam("");
        }
        if (awayTeam !== "" && !teamOptions.includes(awayTeam)) {
            setAwayTeam("");
        }
    }, [awayTeam, homeTeam, teamOptions]);

    useEffect(() => {
        if (venue !== "" && !venueOptions.some((option) => option.id === venue)) {
            setVenue("");
        }
    }, [venue, venueOptions]);

    useEffect(() => {
        if (homeTeam !== "" && awayTeam === homeTeam) {
            setAwayTeam("");
        }

        const tossOptions = buildTossOptions(homeTeam, awayTeam);
        if (tossSelection !== "" && !tossOptions.includes(tossSelection)) {
            setTossSelection("");
        }
    }, [awayTeam, homeTeam, tossSelection]);

    useEffect(() => {
        const oddsTeamOptions = buildOddsTeamOptions(homeTeam, awayTeam);

        setOddsBeforeToss((current) => {
            if (current.selectedTeam === "" || oddsTeamOptions.includes(current.selectedTeam)) {
                return current;
            }
            return { ...current, selectedTeam: "" };
        });

        setOddsAfterToss((current) => {
            if (current.selectedTeam === "" || oddsTeamOptions.includes(current.selectedTeam)) {
                return current;
            }
            return { ...current, selectedTeam: "" };
        });
    }, [awayTeam, homeTeam]);

    function clearFormState(): void {
        setSelectedTradeId(null);
        setHomeTeam("");
        setAwayTeam("");
        setTossSelection("");
        setSeason(defaultSeason);
        setVenue("");
        setBankroll(DEFAULT_BANKROLL);
        setMatchDate("");
        setOddsBeforeToss(EMPTY_ODDS_PHASE_INPUT);
        setOddsAfterToss(EMPTY_ODDS_PHASE_INPUT);
        setHomeGround("NEU");
        setSubmitError(null);
        setSubmitMessage(null);
    }

    function hydrateTrade(trade: TradeResponse): void {
        setSelectedTradeId(trade.id);
        setSeason(trade.season);
        setMatchDate(formatMatchDateInput(trade.match_date));
        setHomeTeam(trade.team_1);
        setAwayTeam(trade.team_2);
        setVenue(trade.stadium);
        setBankroll(trade.bankroll.toString());
        setHomeGround(trade.home_ground);
        setTossSelection(resolveTossSelection(trade.toss_winner, trade.toss_decision, trade.team_1, trade.team_2));
        setOddsBeforeToss({
            selectedTeam: trade.selected_team_before_toss ?? "",
            backOdds: trade.back_odds_before_toss === null ? "" : trade.back_odds_before_toss.toString(),
            layOdds: trade.lay_odds_before_toss === null ? "" : trade.lay_odds_before_toss.toString(),
        });
        setOddsAfterToss({
            selectedTeam: trade.selected_team_after_toss ?? "",
            backOdds: trade.back_odds_after_toss === null ? "" : trade.back_odds_after_toss.toString(),
            layOdds: trade.lay_odds_after_toss === null ? "" : trade.lay_odds_after_toss.toString(),
        });
        setSubmitError(null);
        setSubmitMessage(null);
    }

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
            setSubmitMessage(
                savedTrade.status === "ACTIVE"
                    ? `Trade ${savedTrade.id} is active now.`
                    : `Draft ${savedTrade.id} saved.`
            );
            await onTradeSaved();
        } catch {
            setSubmitError("Failed to save the trade. Please try again.");
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
        setOddsBeforeTossSelectedTeam: (value: string) =>
            setOddsBeforeToss((current) => ({ ...current, selectedTeam: value })),
        setOddsBeforeTossBackOdds: (value: string) =>
            setOddsBeforeToss((current) => ({ ...current, backOdds: value })),
        setOddsBeforeTossLayOdds: (value: string) =>
            setOddsBeforeToss((current) => ({ ...current, layOdds: value })),
        setOddsAfterTossSelectedTeam: (value: string) =>
            setOddsAfterToss((current) => ({ ...current, selectedTeam: value })),
        setOddsAfterTossBackOdds: (value: string) =>
            setOddsAfterToss((current) => ({ ...current, backOdds: value })),
        setOddsAfterTossLayOdds: (value: string) =>
            setOddsAfterToss((current) => ({ ...current, layOdds: value })),
    };
}
