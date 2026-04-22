import type { CreateTradeRequest } from "./cockpit-api";
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

export function getDefaultSeason(formatKey: string): number {
    return formatKey === "ipl" ? 2025 : new Date().getFullYear();
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
