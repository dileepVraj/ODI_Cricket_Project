import type { CreateTradeRequest, TradeResponse } from "./cockpit-api";
import type { HomeGround, OddsPhaseInput, TossSelection } from "./cockpit-types";

export const EMPTY_ODDS_PHASE_INPUT: OddsPhaseInput = {
    selectedTeam: "",
    backOdds: "",
    layOdds: "",
};

export function parsePositiveAmount(value: string): number | null {
    const parsed = Number.parseFloat(value);
    return Number.isFinite(parsed) && parsed > 0 ? parsed : null;
}

export function isTradeBasicsReady(
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

export function getDefaultSeason(_formatKey: string): number {
    return new Date().getFullYear();
}

export function parseIntegerOdds(value: string): number | null {
    const trimmed = value.trim();
    if (trimmed === "") {
        return null;
    }

    const parsed = Number(trimmed);
    return Number.isInteger(parsed) ? parsed : null;
}

export function isOddsPhaseComplete(phase: OddsPhaseInput): boolean {
    return phase.selectedTeam !== ""
        && parseIntegerOdds(phase.backOdds) !== null
        && parseIntegerOdds(phase.layOdds) !== null;
}

export function formatMatchDateInput(matchDate: string | null): string {
    if (!matchDate) {
        return "";
    }
    return matchDate.split("T")[0] ?? "";
}

export function buildOddsTeamOptions(homeTeam: string, awayTeam: string): string[] {
    const options = [homeTeam, awayTeam].filter((team) => team !== "");
    return Array.from(new Set(options));
}

export function resolveTossPayload(
    tossSelection: TossSelection,
    homeTeam: string,
    awayTeam: string
): { toss_winner: string | null; toss_decision: string | null } {
    if (tossSelection === "HOME_FIELD") {
        return { toss_winner: homeTeam, toss_decision: "field" };
    }
    if (tossSelection === "HOME_BAT") {
        return { toss_winner: homeTeam, toss_decision: "bat" };
    }
    if (tossSelection === "AWAY_FIELD") {
        return { toss_winner: awayTeam, toss_decision: "field" };
    }
    if (tossSelection === "AWAY_BAT") {
        return { toss_winner: awayTeam, toss_decision: "bat" };
    }
    return { toss_winner: null, toss_decision: null };
}

export function resolveTossSelection(
    tossWinner: string | null,
    tossDecision: string | null,
    homeTeam: string,
    awayTeam: string
): TossSelection {
    if (!tossWinner || !tossDecision) {
        return "";
    }

    const normalizedDecision = tossDecision.toLowerCase();
    if (tossWinner === homeTeam && normalizedDecision === "field") {
        return "HOME_FIELD";
    }
    if (tossWinner === homeTeam && normalizedDecision === "bat") {
        return "HOME_BAT";
    }
    if (tossWinner === awayTeam && normalizedDecision === "field") {
        return "AWAY_FIELD";
    }
    if (tossWinner === awayTeam && normalizedDecision === "bat") {
        return "AWAY_BAT";
    }

    return "";
}

export function buildCreateTradeRequest(params: {
    bankroll: string;
    awayTeam: string;
    homeTeam: string;
    homeGround: HomeGround;
    matchDate: string;
    oddsBeforeToss: OddsPhaseInput;
    oddsAfterToss: OddsPhaseInput;
    season: number;
    tossSelection: TossSelection;
    venue: string;
}): CreateTradeRequest | null {
    const parsedBankroll = parsePositiveAmount(params.bankroll);
    if (parsedBankroll === null) {
        return null;
    }

    const tossPayload = resolveTossPayload(params.tossSelection, params.homeTeam, params.awayTeam);

    return {
        season: params.season,
        match_date: params.matchDate || null,
        team_1: params.homeTeam,
        team_2: params.awayTeam,
        favourite_team: params.homeTeam,
        home_ground: params.homeGround,
        stadium: params.venue,
        toss_winner: tossPayload.toss_winner,
        toss_decision: tossPayload.toss_decision,
        bankroll: parsedBankroll,
        selected_team_before_toss: params.oddsBeforeToss.selectedTeam || null,
        back_odds_before_toss: parseIntegerOdds(params.oddsBeforeToss.backOdds),
        lay_odds_before_toss: parseIntegerOdds(params.oddsBeforeToss.layOdds),
        selected_team_after_toss: params.oddsAfterToss.selectedTeam || null,
        back_odds_after_toss: parseIntegerOdds(params.oddsAfterToss.backOdds),
        lay_odds_after_toss: parseIntegerOdds(params.oddsAfterToss.layOdds),
    };
}

export function buildTossOptions(homeTeam: string, awayTeam: string): TossSelection[] {
    if (!homeTeam || !awayTeam) {
        return [];
    }

    return ["HOME_FIELD", "HOME_BAT", "AWAY_FIELD", "AWAY_BAT"];
}

function titleCase(value: string): string {
    return value
        .split(" ")
        .filter((part) => part !== "")
        .map((part) => part.charAt(0).toUpperCase() + part.slice(1).toLowerCase())
        .join(" ");
}

export function formatVenueDisplayName(stadium: string): string {
    const trimmedStadium = stadium.trim();
    if (trimmedStadium === "") {
        return "N/A";
    }

    if (trimmedStadium === "IND_MUMBAI_WANKHEDE") {
        return "Wankhede Stadium, Mumbai";
    }

    if (trimmedStadium === "IND_MUMBAI_BRABOURNE") {
        return "Brabourne Stadium, Mumbai";
    }

    if (trimmedStadium === "IND_AHMEDABAD_NARENDRA_MODI") {
        return "Narendra Modi Stadium, Ahmedabad";
    }

    if (!trimmedStadium.includes("_")) {
        return trimmedStadium;
    }

    const parts = trimmedStadium.split("_").filter((part) => part !== "");
    if (parts.length < 2) {
        return titleCase(trimmedStadium.replace(/-/g, " "));
    }

    const city = titleCase(parts[1].replace(/-/g, " "));
    const venueLabel = titleCase(parts.slice(2).join(" ").replace(/-/g, " "));
    const normalizedVenueLabel = venueLabel === "" ? titleCase(parts[parts.length - 1].replace(/-/g, " ")) : venueLabel;
    const hasVenueSuffix = /\b(stadium|ground|arena|park|club|oval|field|center|centre)\b/i.test(normalizedVenueLabel);

    return `${hasVenueSuffix ? normalizedVenueLabel : `${normalizedVenueLabel} Stadium`}, ${city}`;
}

export function formatPreTossOddsLabel(trade: TradeResponse): string {
    const selectedTeam = trade.selected_team_before_toss?.trim() ?? "";
    if (
        selectedTeam !== ""
        && trade.back_odds_before_toss !== null
        && trade.lay_odds_before_toss !== null
    ) {
        return `Pre-toss: ${selectedTeam} ${trade.back_odds_before_toss}/${trade.lay_odds_before_toss}`;
    }

    if (trade.opening_odds !== null) {
        return `Pre-toss ${trade.opening_odds.toFixed(2)}`;
    }

    return "Pre-toss: Pending";
}

export function formatTossResult(trade: TradeResponse): string {
    if (!trade.toss_winner || !trade.toss_decision) {
        return "Pending";
    }
    const decision = trade.toss_decision === "bat" ? "bat" : "bowl";
    return `${trade.toss_winner} opt to ${decision}`;
}
