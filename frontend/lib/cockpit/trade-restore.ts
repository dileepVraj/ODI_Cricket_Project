import {
    createTrade,
    deleteTrade,
    fetchTradeById,
    settleTrade,
    voidTrade,
    type CreateTradeRequest,
    type SettleTradeRequest,
    type TradeResponse,
} from "@/components/cockpit/cockpit-api";
import {
    closeLiveTradeBet,
    createLiveTradeBet,
    type AddBetPayload,
    type BetResponse,
} from "@/lib/cockpit/live-trade-bets-api";

/** @schema none -- frontend-only composite for trade restore */
export interface TradeRestoreSnapshot {
    bets: BetResponse[];
    format: string;
    trade: TradeResponse;
}

export function buildTradeCreateRequest(trade: TradeResponse): CreateTradeRequest {
    return {
        season: trade.season,
        match_date: trade.match_date,
        team_1: trade.team_1,
        team_2: trade.team_2,
        favourite_team: trade.favourite_team,
        home_ground: trade.home_ground,
        stadium: trade.stadium,
        toss_winner: trade.toss_winner,
        toss_decision: trade.toss_decision,
        bankroll: trade.bankroll,
        opening_odds: trade.opening_odds,
        selected_team_before_toss: trade.selected_team_before_toss,
        back_odds_before_toss: trade.back_odds_before_toss,
        lay_odds_before_toss: trade.lay_odds_before_toss,
        selected_team_after_toss: trade.selected_team_after_toss,
        back_odds_after_toss: trade.back_odds_after_toss,
        lay_odds_after_toss: trade.lay_odds_after_toss,
    };
}

function buildSettleTradeRequest(trade: TradeResponse): SettleTradeRequest {
    if (
        trade.winner === null ||
        trade.trade_sentiment === null ||
        trade.targeted_pnl === null ||
        trade.achieved_yield_percentage === null
    ) {
        throw new Error("The deleted settled trade did not include enough data to restore it.");
    }

    return {
        winner: trade.winner,
        sentiment: trade.trade_sentiment,
        fav_sub_30_loss: trade.fav_sub_30_loss,
        targeted_pnl: trade.targeted_pnl,
        achieved_yield: trade.achieved_yield_percentage,
    };
}

function buildBetRestorePayload(bet: BetResponse): AddBetPayload {
    return {
        team: bet.team,
        bet_type: bet.bet_type,
        odds_paise: bet.odds_paise,
        stake: bet.stake,
    };
}

function normalizeBetResponse(value: BetResponse | BetResponse[] | null): BetResponse | null {
    if (value === null) {
        return null;
    }

    if (Array.isArray(value)) {
        return value[0] ?? null;
    }

    return value;
}

export async function restoreDeletedTrade(snapshot: TradeRestoreSnapshot): Promise<TradeResponse> {
    let restoredTradeId: number | null = null;

    try {
        const createdTrade = await createTrade(buildTradeCreateRequest(snapshot.trade), snapshot.format);
        restoredTradeId = createdTrade.id;

        const recreatedBets: BetResponse[] = [];
        for (const bet of snapshot.bets) {
            const createdBet = normalizeBetResponse(
                await createLiveTradeBet(createdTrade.id, buildBetRestorePayload(bet), snapshot.format),
            );

            if (createdBet === null) {
                throw new Error("The server did not return the restored bet.");
            }

            recreatedBets.push(createdBet);
        }

        for (let index = 0; index < snapshot.bets.length; index += 1) {
            const originalBet = snapshot.bets[index];
            const recreatedBet = recreatedBets[index];

            if (originalBet !== undefined && recreatedBet !== undefined && !originalBet.is_open) {
                await closeLiveTradeBet(createdTrade.id, recreatedBet.id, snapshot.format);
            }
        }

        if (snapshot.trade.status === "SETTLED") {
            return await settleTrade(createdTrade.id, buildSettleTradeRequest(snapshot.trade), snapshot.format);
        }

        if (snapshot.trade.status === "VOID") {
            return await voidTrade(createdTrade.id, snapshot.format);
        }

        return await fetchTradeById(createdTrade.id, snapshot.format);
    } catch (err) {
        if (restoredTradeId !== null) {
            try {
                await deleteTrade(restoredTradeId, snapshot.format);
            } catch {
                // If cleanup fails, the original error is still the one the UI should show.
            }
        }

        throw err;
    }
}
