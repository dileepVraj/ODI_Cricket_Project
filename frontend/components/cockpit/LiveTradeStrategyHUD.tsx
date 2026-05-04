"use client";

import type { ReactNode } from "react";
import type { TradeStateResponse } from "./cockpit-api";
import CockpitTeamText from "./CockpitTeamText";
import { useLiveTradeMarketOdds } from "@/lib/cockpit/LiveTradeMarketOddsContext";
import { buildCashOutQuote, type CashOutQuote } from "@/lib/cockpit/live-trade-market-odds";
import {
    calculateStrategyBreakEven,
    calculateStrategyTargetPnl,
    calculateTargetExitOdds,
    formatStrategyBreakEvenDisplay,
} from "@/lib/cockpit/live-trade-strategy";

interface LiveTradeStrategyHUDProps {
    team1: string;
    team2: string;
    tradeState: TradeStateResponse;
}

function formatMoney(value: number): string {
    const sign = value > 0 ? "+" : value < 0 ? "-" : "";
    return `Rs ${sign}${new Intl.NumberFormat("en-IN", {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
    }).format(Math.abs(value))}`;
}

function formatPercent(value: number): string {
    return `${new Intl.NumberFormat("en-IN", {
        minimumFractionDigits: 0,
        maximumFractionDigits: 2,
    }).format(value)}%`;
}

function formatOddsPaise(oddsPaise: number): string {
    return `${oddsPaise}p`;
}

function toneClass(value: number | null): string {
    if (value === null) {
        return "text-tier-neutral";
    }

    if (value > 0) {
        return "text-tier-positive";
    }

    if (value < 0) {
        return "text-tier-negative";
    }

    return "text-tier-neutral";
}

function StrategyField({
    label,
    value,
    labelClassName,
    valueClassName,
}: {
    label: string;
    value: ReactNode;
    labelClassName?: string;
    valueClassName?: string;
}) {
    return (
        <div className="live-trade-strategy-hud__item">
            <span className={`live-trade-strategy-hud__label ${labelClassName ?? ""}`}>{label}</span>
            <span className={`live-trade-strategy-hud__value font-numeric ${valueClassName ?? ""}`}>
                {value}
            </span>
        </div>
    );
}

function formatCashOutLine(cashOut: CashOutQuote | null, targetPnl: number | null): ReactNode {
    if (!cashOut || targetPnl === null || targetPnl <= 0) {
        return "--";
    }

    const yieldPercent = (cashOut.guaranteedPnl / targetPnl) * 100;
    return (
        <>
            {formatMoney(cashOut.guaranteedPnl)} ({formatPercent(yieldPercent)})
        </>
    );
}

function formatLockedProfitLine(lockedProfit: number, targetPnl: number | null): ReactNode {
    if (targetPnl === null || targetPnl <= 0) {
        return (
            <>
                {formatMoney(lockedProfit)} (--%)
            </>
        );
    }

    const yieldPercent = (lockedProfit / targetPnl) * 100;

    return (
        <>
            {formatMoney(lockedProfit)} ({formatPercent(yieldPercent)})
        </>
    );
}

function formatBreakEvenLine(
    team1: string,
    team2: string,
    netPnlTeam1: number,
    netPnlTeam2: number,
    result: ReturnType<typeof calculateStrategyBreakEven>,
): ReactNode {
    const display = formatStrategyBreakEvenDisplay(team1, team2, netPnlTeam1, netPnlTeam2, result);

    if (result.mode === "risk-free") {
        return "Risk-Free";
    }

    if (display !== null) {
        return (
            <>
                <CockpitTeamText team={display.team} /> @ {formatOddsPaise(display.oddsPaise)}
            </>
        );
    }

    return "No break-even";
}

function formatTargetExitOddsLine(
    result: ReturnType<typeof calculateTargetExitOdds>,
): ReactNode {
    if (result.mode === "achieved") {
        return "Achieved";
    }

    if (result.mode === "not-reachable") {
        return "Not reachable";
    }

    if (result.mode === "reachable" && result.layTeam !== null && result.requiredOddsPaise !== null) {
        return (
            <>
                LAY <CockpitTeamText team={result.layTeam} /> @ {formatOddsPaise(result.requiredOddsPaise)}
            </>
        );
    }

    return "--";
}

function targetExitOddsToneClass(mode: string): string {
    if (mode === "achieved" || mode === "reachable") {
        return "text-tier-positive";
    }

    if (mode === "not-reachable") {
        return "text-tier-negative";
    }

    return "text-tier-neutral";
}

export default function LiveTradeStrategyHUD({
    team1,
    team2,
    tradeState,
}: LiveTradeStrategyHUDProps) {
    const { currentMarketOdds } = useLiveTradeMarketOdds();
    const targetProjection = calculateStrategyTargetPnl(tradeState.bankroll, tradeState.back_odds_after_toss);
    const isGreenBooked = tradeState.net_pnl_team_1 > 0 && tradeState.net_pnl_team_2 > 0;
    const lockedProfit = Math.min(tradeState.net_pnl_team_1, tradeState.net_pnl_team_2);
    const cashOutQuote = isGreenBooked ? null : buildCashOutQuote(team1, team2, currentMarketOdds, {
        team1,
        team2,
        netPnlTeam1: tradeState.net_pnl_team_1,
        netPnlTeam2: tradeState.net_pnl_team_2,
    });
    const breakEven = calculateStrategyBreakEven(
        team1,
        team2,
        tradeState.net_pnl_team_1,
        tradeState.net_pnl_team_2,
    );
    const targetExitOdds = calculateTargetExitOdds(
        team1,
        team2,
        tradeState.net_pnl_team_1,
        tradeState.net_pnl_team_2,
        targetProjection?.targetPnl ?? null,
    );
    const projectionToneClassName = isGreenBooked
        ? "live-trade-strategy-hud__value--locked text-tier-positive"
        : targetProjection !== null && targetProjection.targetPnl > 0
        ? toneClass(cashOutQuote?.guaranteedPnl ?? null)
        : "text-tier-neutral";
    const projectionLabelClassName = isGreenBooked ? "live-trade-strategy-hud__label--locked" : undefined;
    const projectionValue = isGreenBooked
        ? formatLockedProfitLine(lockedProfit, targetProjection?.targetPnl ?? null)
        : formatCashOutLine(cashOutQuote, targetProjection?.targetPnl ?? null);

    return (
        <section className="live-trade-strategy-hud animate-fade-in" aria-label="Strategy HUD">
            <div className="live-trade-strategy-hud__layout">
                <StrategyField
                    label="TARGET PNL (30P EXIT)"
                    value={targetProjection ? formatMoney(targetProjection.targetPnl) : "--"}
                    valueClassName={toneClass(targetProjection?.targetPnl ?? null)}
                />
                <StrategyField
                    label="LIVE PROJECTION (YIELD)"
                    labelClassName={projectionLabelClassName}
                    value={projectionValue}
                    valueClassName={projectionToneClassName}
                />
                <StrategyField
                    label="BREAK-EVEN (COVER ODDS)"
                    value={formatBreakEvenLine(team1, team2, tradeState.net_pnl_team_1, tradeState.net_pnl_team_2, breakEven)}
                    valueClassName={breakEven.mode === "unavailable" ? "text-tier-negative" : "text-tier-positive"}
                />
                <StrategyField
                    label="TARGET EXIT ODDS"
                    value={formatTargetExitOddsLine(targetExitOdds)}
                    valueClassName={targetExitOddsToneClass(targetExitOdds.mode)}
                />
            </div>
        </section>
    );
}
