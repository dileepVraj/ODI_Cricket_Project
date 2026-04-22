"use client";

import { useEffect, useState } from "react";
import {
    createTrade,
    fetchCockpitTeams,
    fetchCockpitVenues,
    listTrades,
    updateTrade,
    type TradeResponse,
    type VenueOption,
} from "./cockpit-api";
import CockpitMatchSetup from "./CockpitMatchSetup";
import PendingPreTossTrades from "./PendingPreTossTrades";
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
} from "./cockpit-form-helpers";
import type { HomeGround, OddsPhaseInput, TossSelection } from "./cockpit-types";

const DEFAULT_BANKROLL = "100";

interface ActiveTradeViewProps {
    formatKey: string;
}

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

export default function ActiveTradeView({ formatKey }: ActiveTradeViewProps) {
    const selectedFormat = formatKey || "ipl";
    const defaultSeason = getDefaultSeason(selectedFormat);

    const [teamOptions, setTeamOptions] = useState<string[]>([]);
    const [venueOptions, setVenueOptions] = useState<VenueOption[]>([]);
    const [isLoadingTeams, setIsLoadingTeams] = useState(false);
    const [isLoadingVenues, setIsLoadingVenues] = useState(false);
    const [isLoadingPending, setIsLoadingPending] = useState(false);
    const [pendingError, setPendingError] = useState<string | null>(null);
    const [pendingTrades, setPendingTrades] = useState<TradeResponse[]>([]);
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
        setSeason(defaultSeason);
    }, [defaultSeason]);

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
            await refreshPendingTrades();
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

    return (
        <div className="cockpit-trade-layout cockpit-trade-layout--split">
            <CockpitMatchSetup
                teamOptions={teamOptions}
                awayTeamOptions={awayTeamOptions}
                oddsTeamOptions={oddsTeamOptions}
                venueOptions={venueOptions}
                isLoadingTeams={isLoadingTeams}
                isLoadingVenues={isLoadingVenues}
                homeTeam={homeTeam}
                awayTeam={awayTeam}
                tossSelection={tossSelection}
                venue={venue}
                bankroll={bankroll}
                matchDate={matchDate}
                homeGround={homeGround}
                oddsBeforeToss={oddsBeforeToss}
                oddsAfterToss={oddsAfterToss}
                canCreateTrade={canCreateTrade}
                isCreating={isSaving}
                createError={submitError}
                createMessage={submitMessage}
                submitLabel={submitLabel}
                onHomeTeamChange={setHomeTeam}
                onAwayTeamChange={setAwayTeam}
                onTossSelectionChange={setTossSelection}
                onVenueChange={setVenue}
                onBankrollChange={setBankroll}
                onMatchDateChange={setMatchDate}
                onHomeGroundChange={setHomeGround}
                onOddsBeforeTossSelectedTeamChange={(value) =>
                    setOddsBeforeToss((current) => ({ ...current, selectedTeam: value }))
                }
                onOddsBeforeTossBackOddsChange={(value) =>
                    setOddsBeforeToss((current) => ({ ...current, backOdds: value }))
                }
                onOddsBeforeTossLayOddsChange={(value) =>
                    setOddsBeforeToss((current) => ({ ...current, layOdds: value }))
                }
                onOddsAfterTossSelectedTeamChange={(value) =>
                    setOddsAfterToss((current) => ({ ...current, selectedTeam: value }))
                }
                onOddsAfterTossBackOddsChange={(value) =>
                    setOddsAfterToss((current) => ({ ...current, backOdds: value }))
                }
                onOddsAfterTossLayOddsChange={(value) =>
                    setOddsAfterToss((current) => ({ ...current, layOdds: value }))
                }
                onCreateTrade={handleCreateTrade}
            />

            <PendingPreTossTrades
                trades={pendingTrades}
                isLoading={isLoadingPending}
                error={pendingError}
                selectedTradeId={selectedTradeId}
                onSelectTrade={hydrateTrade}
                onClearSelection={clearFormState}
            />
        </div>
    );
}
