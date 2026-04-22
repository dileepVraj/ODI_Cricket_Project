"use client";

import type { TradeResponse } from "./cockpit-api";

export interface CloseTradePreview {
    actualProfit: number;
    pctOfTarget: number | null;
    result: string;
    aboveBreakeven: boolean;
}

export function computePreview(trade: TradeResponse, exitOdds: number): CloseTradePreview {
    const totalStake = trade.total_stake ?? 0;

    const bullet05 = (trade.bullet_05_odds ?? 0) * (trade.bullet_05_stake ?? 0);
    const bullet1 = (trade.bullet_1_odds ?? 0) * (trade.bullet_1_stake ?? 0);
    const bullet2 = (trade.bullet_2_odds ?? 0) * (trade.bullet_2_stake ?? 0);
    const bullet3 = (trade.bullet_3_odds ?? 0) * (trade.bullet_3_stake ?? 0);
    const liability = bullet05 + bullet1 + bullet2 + bullet3;

    const actualProfit = exitOdds === 0 ? -totalStake : liability / exitOdds - totalStake;

    const targetProfit = trade.target_profit;
    const pctOfTarget = targetProfit !== null && targetProfit !== 0 ? actualProfit / targetProfit : null;

    let result: string;
    if (exitOdds === 0) {
        result = "LOST";
    } else if (targetProfit !== null && actualProfit >= targetProfit * 0.30) {
        result = "SAT";
    } else if (actualProfit >= 0) {
        result = "SAV+";
    } else {
        result = "SAV-";
    }

    const aboveBreakeven =
        exitOdds > 0 &&
        trade.breakeven_odds !== null &&
        exitOdds > trade.breakeven_odds;

    return { actualProfit, pctOfTarget, result, aboveBreakeven };
}

export function resultColor(result: string): string {
    if (result === "SAT") {
        return "var(--tier-elite)";
    }
    if (result === "SAV+") {
        return "var(--tier-caution)";
    }
    if (result === "SAV-") {
        return "var(--tier-danger)";
    }
    if (result === "LOST") {
        return "var(--tier-danger)";
    }
    return "var(--text-secondary)";
}

export function formatTossSummary(winner: string | null, decision: string | null): string {
    const normalizedDecision =
        decision?.toLowerCase() === "bw"
            ? "field"
            : decision?.toLowerCase() === "bt"
                ? "bat"
                : decision ?? "";

    if (!winner && !normalizedDecision) {
        return "N/A";
    }

    if (!winner) {
        return normalizedDecision || "N/A";
    }

    if (!normalizedDecision) {
        return winner;
    }

    return `${winner} choose to ${normalizedDecision}`;
}
