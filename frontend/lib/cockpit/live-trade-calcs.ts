/** @schema-exempt - frontend-only calculation shape derived from BetResponse */
export interface BetRecord {
    team: string;
    bet_type: "BACK" | "LAY";
    odds_decimal: number;
    stake: number;
    is_open: boolean;
}

/** @schema-exempt - frontend-only calculation result */
export interface GreenBookResult {
    closingStake: number;
    guaranteedProfit: number;
}

/** @schema-exempt - frontend-only calculation result */
export interface MissedOpportunityResult {
    cumulativeStake: number;
    potentialPayout: number;
    idealLayStake: number;
    netPnl: number;
    layOddsDecimal: number;
}

type ClosingType = "BACK" | "LAY";

export function oddsDecimalFromPaise(paise: number): number {
    return paise / 100 + 1;
}

export function betLiability(stake: number, oddsDecimal: number): number {
    return stake * (oddsDecimal - 1);
}

function getOpenBets(bets: BetRecord[]): BetRecord[] {
    return bets.filter((bet) => bet.is_open);
}

function getPositionOutcomes(bets: BetRecord[]): { ifWin: number; ifLose: number } {
    let ifWin = 0;
    let ifLose = 0;

    for (const bet of bets) {
        if (bet.bet_type === "BACK") {
            ifWin += bet.stake * (bet.odds_decimal - 1);
            ifLose -= bet.stake;
            continue;
        }

        ifWin -= bet.stake * (bet.odds_decimal - 1);
        ifLose += bet.stake;
    }

    return { ifWin, ifLose };
}

export function netPnl(bets: BetRecord[], teamWins: string): number {
    let pnl = 0;

    for (const bet of getOpenBets(bets)) {
        const betWins = bet.team === teamWins;

        if (betWins) {
            pnl += bet.bet_type === "BACK"
                ? bet.stake * (bet.odds_decimal - 1)
                : -bet.stake * (bet.odds_decimal - 1);
            continue;
        }

        pnl += bet.bet_type === "BACK" ? -bet.stake : bet.stake;
    }

    return pnl;
}

export function greenBookClosingStake(
    openBets: BetRecord[],
    closingOddsDecimal: number,
    closingType: ClosingType
): GreenBookResult {
    const openPosition = getPositionOutcomes(getOpenBets(openBets));

    if (closingOddsDecimal <= 0) {
        return { closingStake: 0, guaranteedProfit: 0 };
    }

    if (closingType === "LAY") {
        const closingStake = (openPosition.ifWin - openPosition.ifLose) / closingOddsDecimal;
        return {
            closingStake,
            guaranteedProfit: openPosition.ifLose + closingStake,
        };
    }

    const closingStake = (openPosition.ifLose - openPosition.ifWin) / closingOddsDecimal;
    return {
        closingStake,
        guaranteedProfit: openPosition.ifWin + closingStake * (closingOddsDecimal - 1),
    };
}

export function calculateMissedOpportunityResult(
    bets: BetRecord[],
    selectedTeam: string,
    betIndex: number | null,
    layOddsPaise: number | null,
): MissedOpportunityResult | null {
    const trimmedTeam = selectedTeam.trim();
    if (trimmedTeam === "" || betIndex === null || layOddsPaise === null || layOddsPaise <= 0) {
        return null;
    }

    const upperBound = Math.min(Math.max(betIndex, 0), bets.length - 1);
    if (upperBound < 0) {
        return null;
    }

    const betWindow = bets.slice(0, upperBound + 1);
    const cumulativeStake = betWindow.reduce((total, bet) => total + bet.stake, 0);
    const potentialPayout = betWindow.reduce((total, bet) => {
        if (bet.team !== trimmedTeam || bet.bet_type !== "BACK") {
            return total;
        }
        return total + (bet.stake * bet.odds_decimal);
    }, 0);
    const layOddsDecimal = oddsDecimalFromPaise(layOddsPaise);
    if (layOddsDecimal <= 0) {
        return null;
    }

    const idealLayStake = potentialPayout / layOddsDecimal;
    const netPnl = idealLayStake - cumulativeStake;

    return {
        cumulativeStake,
        potentialPayout,
        idealLayStake,
        netPnl,
        layOddsDecimal,
    };
}
