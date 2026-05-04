import { oddsDecimalFromPaise } from "./live-trade-market-odds";

const STRATEGY_EXIT_ODDS_PAISE = 30;

function roundMoney(value: number): number {
    return Math.round(value * 100) / 100;
}

/** @schema StrategyTargetPnlResult */
export interface StrategyTargetPnlResult {
    targetPnl: number;
    hedgeStake: number;
    exitOddsPaise: number;
    postTossOddsPaise: number;
}

/** @schema StrategyBreakEvenResult */
export interface StrategyBreakEvenResult {
    mode: "risk-free" | "hedge" | "unavailable";
    teamWithProfit: string | null;
    requiredOddsPaise: number | null;
}

export interface StrategyBreakEvenDisplay {
    team: string;
    oddsPaise: number;
}

/** @schema frontend-only -- no backend Pydantic equivalent */
export interface StrategyTargetExitOddsResult {
    mode: "reachable" | "achieved" | "not-reachable" | "unavailable";
    layTeam: string | null;
    requiredOddsPaise: number | null;
}

export function calculateStrategyTargetPnl(
    bankroll: number,
    postTossOddsPaise: number | null,
    exitOddsPaise: number = STRATEGY_EXIT_ODDS_PAISE,
): StrategyTargetPnlResult | null {
    if (
        !Number.isFinite(bankroll) ||
        bankroll <= 0 ||
        postTossOddsPaise === null ||
        postTossOddsPaise <= 0 ||
        exitOddsPaise <= 0
    ) {
        return null;
    }

    const postTossOddsDecimal = oddsDecimalFromPaise(postTossOddsPaise);
    const exitOddsDecimal = oddsDecimalFromPaise(exitOddsPaise);
    const hedgeStake = roundMoney((bankroll * postTossOddsDecimal) / exitOddsDecimal);

    return {
        targetPnl: roundMoney(hedgeStake - bankroll),
        hedgeStake,
        exitOddsPaise,
        postTossOddsPaise,
    };
}

export function calculateStrategyBreakEven(
    team1: string,
    team2: string,
    netPnlTeam1: number,
    netPnlTeam2: number,
): StrategyBreakEvenResult {
    if (netPnlTeam1 >= 0 && netPnlTeam2 >= 0) {
        return {
            mode: "risk-free",
            teamWithProfit: null,
            requiredOddsPaise: null,
        };
    }

    if (netPnlTeam1 > 0 && netPnlTeam2 < 0) {
        return {
            mode: "hedge",
            teamWithProfit: team1,
            requiredOddsPaise: Math.round((netPnlTeam1 / Math.abs(netPnlTeam2)) * 100),
        };
    }

    if (netPnlTeam2 > 0 && netPnlTeam1 < 0) {
        return {
            mode: "hedge",
            teamWithProfit: team2,
            requiredOddsPaise: Math.round((netPnlTeam2 / Math.abs(netPnlTeam1)) * 100),
        };
    }

    return {
        mode: "unavailable",
        teamWithProfit: null,
        requiredOddsPaise: null,
    };
}

export function formatStrategyBreakEvenDisplay(
    team1: string,
    team2: string,
    netPnlTeam1: number,
    netPnlTeam2: number,
    result: StrategyBreakEvenResult,
): StrategyBreakEvenDisplay | null {
    if (result.mode !== "hedge" || result.teamWithProfit === null || result.requiredOddsPaise === null) {
        return null;
    }

    if (result.teamWithProfit === team1) {
        if (netPnlTeam1 <= 0 || netPnlTeam2 >= 0) {
            return null;
        }

        return {
            team: team2,
            oddsPaise: Math.max(1, Math.round((Math.abs(netPnlTeam2) / netPnlTeam1) * 100)),
        };
    }

    if (netPnlTeam2 <= 0 || netPnlTeam1 >= 0) {
        return null;
    }

    return {
        team: team1,
        oddsPaise: Math.max(1, Math.round((Math.abs(netPnlTeam1) / netPnlTeam2) * 100)),
    };
}

export function calculateTargetExitOdds(
    team1: string,
    team2: string,
    netPnlTeam1: number,
    netPnlTeam2: number,
    targetPnl: number | null,
): StrategyTargetExitOddsResult {
    if (targetPnl === null || targetPnl <= 0) {
        return { mode: "unavailable", layTeam: null, requiredOddsPaise: null };
    }

    if (netPnlTeam1 >= targetPnl && netPnlTeam2 >= targetPnl) {
        return { mode: "achieved", layTeam: null, requiredOddsPaise: null };
    }

    const team1HasProfit = netPnlTeam1 > netPnlTeam2;
    const profitSidePnl = team1HasProfit ? netPnlTeam1 : netPnlTeam2;
    const lossSidePnl = team1HasProfit ? netPnlTeam2 : netPnlTeam1;
    const profitTeam = team1HasProfit ? team1 : team2;

    if (profitSidePnl <= targetPnl) {
        return { mode: "not-reachable", layTeam: null, requiredOddsPaise: null };
    }

    if (lossSidePnl >= targetPnl) {
        return { mode: "achieved", layTeam: null, requiredOddsPaise: null };
    }

    const numerator = profitSidePnl - targetPnl;
    const denominator = targetPnl - lossSidePnl;
    const oddsPaise = Math.round((numerator / denominator) * 100);

    if (oddsPaise < 1) {
        return { mode: "not-reachable", layTeam: null, requiredOddsPaise: null };
    }

    return {
        mode: "reachable",
        layTeam: profitTeam,
        requiredOddsPaise: oddsPaise,
    };
}
