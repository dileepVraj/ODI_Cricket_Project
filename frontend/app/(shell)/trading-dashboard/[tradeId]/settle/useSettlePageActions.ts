"use client";

import { useRef, useState } from "react";
import { useRouter } from "next/navigation";
import type { SettleTradeRequest, TradeStateResponse } from "@/components/cockpit/cockpit-api";
import type { BetResponse } from "@/lib/cockpit/live-trade-bets-api";
import { calculateMissedOpportunityResult } from "@/lib/cockpit/live-trade-calcs";
import { calculateStrategyTargetPnl } from "@/lib/cockpit/live-trade-strategy";
import { parseIntegerOdds } from "@/components/cockpit/cockpit-form-helpers";
import { resettleTrade, settleTrade, voidTrade } from "@/components/cockpit/cockpit-api";

interface UseSettlePageActionsArgs {
    format: string;
    tradeId: number;
    isEditMode: boolean;
    tradeState: TradeStateResponse | null;
    bets: BetResponse[];
    winner: SettleTradeRequest["winner"] | null;
    sentiment: SettleTradeRequest["sentiment"];
    favSub30Loss: boolean;
    hasMissedSwing: boolean;
    missedSwingTeam: string;
    missedSwingBackOddsPaise: string;
    missedSwingLayOddsPaise: string;
    missedSwingBetIndex: number | null;
    missedSwingType: string | null;
    mistakeTags: string[];
    mistakeNote: string;
    resetDraftState: () => void;
}

interface UseSettlePageActionsResult {
    targetedPnl: number;
    settledPnl: number;
    achievedYield: number;
    missedOpportunityResult: ReturnType<typeof calculateMissedOpportunityResult>;
    isBusy: boolean;
    canSubmit: boolean;
    isSubmitting: boolean;
    isVoiding: boolean;
    voidConfirmPending: boolean;
    error: string | null;
    clearVoidConfirmPending: () => void;
    handleBack: () => void;
    handleConfirm: () => Promise<void>;
    handleVoidMatch: () => Promise<void>;
}

function normalizeOdds(value: string): number | null {
    const parsed = parseIntegerOdds(value);
    return parsed !== null && parsed > 0 ? parsed : null;
}

export function useSettlePageActions({
    format,
    tradeId,
    isEditMode,
    tradeState,
    bets,
    winner,
    sentiment,
    favSub30Loss,
    hasMissedSwing,
    missedSwingTeam,
    missedSwingBackOddsPaise,
    missedSwingLayOddsPaise,
    missedSwingBetIndex,
    missedSwingType,
    mistakeTags,
    mistakeNote,
    resetDraftState,
}: UseSettlePageActionsArgs): UseSettlePageActionsResult {
    const router = useRouter();
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [isVoiding, setIsVoiding] = useState(false);
    const [voidConfirmPending, setVoidConfirmPending] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const isSubmittingRef = useRef(false);
    const isVoidingRef = useRef(false);

    const dashboardPath = `/trading-dashboard?format=${encodeURIComponent(format)}&action=new`;
    const tradePath = `/trading-dashboard/${tradeId}?format=${encodeURIComponent(format)}`;
    const historyPath = `/history?format=${encodeURIComponent(format)}`;

    const targetProjection = tradeState
        ? calculateStrategyTargetPnl(
            tradeState.bankroll,
            tradeState.back_odds_after_toss,
        )
        : null;
    const targetedPnl = tradeState && isEditMode && tradeState.targeted_pnl !== null && tradeState.targeted_pnl !== undefined
        ? tradeState.targeted_pnl
        : (targetProjection?.targetPnl ?? 0);
    const normalizedMissedSwingLayOdds = normalizeOdds(missedSwingLayOddsPaise);
    const missedOpportunityResult = tradeState && hasMissedSwing
        ? calculateMissedOpportunityResult(
            bets,
            missedSwingTeam,
            missedSwingBetIndex,
            normalizedMissedSwingLayOdds,
        )
        : null;
    const settledPnl = tradeState
        ? winner === "team_1"
            ? tradeState.net_pnl_team_1
            : winner === "team_2"
                ? tradeState.net_pnl_team_2
                : 0
        : 0;
    const achievedYield = targetedPnl > 0
        ? Math.round((settledPnl / targetedPnl) * 10000) / 100
        : 0;
    const isBusy = isSubmitting || isVoiding;
    const canSubmit = winner !== null && !isBusy;

    function handleBack(): void {
        if (isEditMode) {
            router.push(historyPath);
            return;
        }
        router.push(tradePath);
    }

    async function handleConfirm(): Promise<void> {
        if (tradeState === null || isSubmittingRef.current || isVoidingRef.current || winner === null) return;

        isSubmittingRef.current = true;
        setIsSubmitting(true);
        setError(null);

        const payload: SettleTradeRequest = {
            winner,
            sentiment,
            fav_sub_30_loss: favSub30Loss,
            missed_swing_team: hasMissedSwing ? missedSwingTeam || null : null,
            missed_swing_back_odds: hasMissedSwing ? normalizeOdds(missedSwingBackOddsPaise) : null,
            missed_swing_lay_odds: hasMissedSwing ? normalizedMissedSwingLayOdds : null,
            missed_swing_bet_index: hasMissedSwing ? missedSwingBetIndex : null,
            missed_swing_cumulative_stake: hasMissedSwing && missedOpportunityResult
                ? missedOpportunityResult.cumulativeStake
                : null,
            missed_swing_net_pnl: hasMissedSwing && missedOpportunityResult
                ? missedOpportunityResult.netPnl
                : null,
            missed_swing_type: hasMissedSwing ? missedSwingType : null,
            targeted_pnl: targetedPnl,
            achieved_yield: achievedYield,
            trade_mistakes: mistakeTags.length > 0 || mistakeNote.trim() !== ""
                ? { tags: mistakeTags, note: mistakeNote.trim() || null }
                : null,
        };

        try {
            if (isEditMode) {
                await resettleTrade(tradeId, payload, format);
            } else {
                await settleTrade(tradeId, payload, format);
            }
        } catch (err: unknown) {
            const msg = err instanceof Error && err.message.trim() !== ""
                ? err.message
                : isEditMode ? "Could not save the changes." : "Could not settle the trade.";
            setError(msg);
            isSubmittingRef.current = false;
            setIsSubmitting(false);
            return;
        }

        isSubmittingRef.current = false;
        setIsSubmitting(false);
        if (isEditMode) {
            router.replace(historyPath);
        } else {
            resetDraftState();
            router.replace(dashboardPath);
        }
    }

    async function handleVoidMatch(): Promise<void> {
        if (tradeState === null) return;
        if (!voidConfirmPending) {
            setVoidConfirmPending(true);
            return;
        }

        if (isSubmittingRef.current || isVoidingRef.current) return;

        isVoidingRef.current = true;
        setIsVoiding(true);
        setError(null);

        try {
            await voidTrade(tradeId, format);
        } catch (err: unknown) {
            const msg = err instanceof Error && err.message.trim() !== ""
                ? err.message
                : "Could not void the trade.";
            setError(msg);
            isVoidingRef.current = false;
            setIsVoiding(false);
            return;
        }

        isVoidingRef.current = false;
        setIsVoiding(false);
        resetDraftState();
        router.replace(dashboardPath);
    }

    return {
        targetedPnl,
        settledPnl,
        achievedYield,
        missedOpportunityResult,
        isBusy,
        canSubmit,
        isSubmitting,
        isVoiding,
        voidConfirmPending,
        error,
        clearVoidConfirmPending: () => {
            setVoidConfirmPending(false);
        },
        handleBack,
        handleConfirm,
        handleVoidMatch,
    };
}
