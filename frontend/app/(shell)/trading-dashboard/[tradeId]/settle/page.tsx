"use client";

import { Suspense, useRef, useState } from "react";
import { useParams, useRouter, useSearchParams } from "next/navigation";
import { ArrowLeft } from "lucide-react";
import { useCockpitTradeDraft } from "@/lib/cockpit/CockpitTradeDraftContext";
import { calculateStrategyTargetPnl } from "@/lib/cockpit/live-trade-strategy";
import { useLiveTradeBets } from "@/lib/cockpit/useLiveTradeBets";
import { useLiveTradeState } from "@/lib/cockpit/useLiveTradeState";
import CockpitTeamText from "@/components/cockpit/CockpitTeamText";
import LiveTradeSettlementPreview from "@/components/cockpit/LiveTradeSettlementPreview";
import SettlementResultSelector from "@/components/cockpit/SettlementResultSelector";
import SettlementTradeNotes from "@/components/cockpit/SettlementTradeNotes";
import { parseIntegerOdds } from "@/components/cockpit/cockpit-form-helpers";
import {
    resettleTrade,
    settleTrade,
    voidTrade,
    type SettleTradeRequest,
} from "@/components/cockpit/cockpit-api";

import {
    ERROR_GRID_STYLE,
    parseTradeId,
    SettlePageError,
    SettlePageFooter,
    SettlePageSkeleton,
    useSettleEditPrePopulate,
} from "./SettlePageParts";

/* -- main inner component --------------------------------------------------- */

function SettlePageInner() {
    const params = useParams<{ tradeId?: string | string[] }>();
    const searchParams = useSearchParams();
    const router = useRouter();
    const format = searchParams.get("format") ?? "ipl";
    const { resetDraftState } = useCockpitTradeDraft();

    const tradeId = parseTradeId(params.tradeId);
    const isValidTradeId = Number.isInteger(tradeId) && tradeId > 0;
    const isEditMode = searchParams.get("edit") === "1";

    /* -- data hooks --------------------------------------------------------- */

    const { tradeState, isLoading, error: loadError } = useLiveTradeState(
        isValidTradeId ? tradeId : 0,
        format,
    );
    const { bets } = useLiveTradeBets(isValidTradeId ? tradeId : 0, format);

    /* -- form state --------------------------------------------------------- */

    const [winner, setWinner] = useState<SettleTradeRequest["winner"] | null>(null);
    const [sentiment, setSentiment] = useState<SettleTradeRequest["sentiment"]>("saved");
    const [favSub30Loss, setFavSub30Loss] = useState(false);
    const [lowestFavOddsPaise, setLowestFavOddsPaise] = useState("");
    const [postLowBetNumber, setPostLowBetNumber] = useState<number | null>(null);
    const [postLowBetStake, setPostLowBetStake] = useState<number | null>(null);
    const [mistakeTags, setMistakeTags] = useState<string[]>([]);
    const [mistakeNote, setMistakeNote] = useState("");
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [isVoiding, setIsVoiding] = useState(false);
    const [voidConfirmPending, setVoidConfirmPending] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const isSubmittingRef = useRef(false);
    const isVoidingRef = useRef(false);

    useSettleEditPrePopulate(isEditMode, tradeState ?? null, {
        setWinner, setSentiment, setFavSub30Loss,
        setLowestFavOddsPaise, setMistakeTags, setMistakeNote,
    });

    if (isLoading) return <SettlePageSkeleton />;
    if (loadError || !tradeState) {
        return <SettlePageError message={loadError ?? "Trade not found."} />;
    }

    const dashboardPath = `/trading-dashboard?format=${encodeURIComponent(format)}&action=new`;
    const tradePath = `/trading-dashboard/${tradeId}?format=${encodeURIComponent(format)}`;
    const historyPath = `/history?format=${encodeURIComponent(format)}`;

    const targetProjection = calculateStrategyTargetPnl(
        tradeState.bankroll,
        tradeState.back_odds_after_toss,
    );
    const targetedPnl = isEditMode && tradeState.targeted_pnl !== null && tradeState.targeted_pnl !== undefined
        ? tradeState.targeted_pnl
        : (targetProjection?.targetPnl ?? 0);
    const settledPnl = winner === "team_1"
        ? tradeState.net_pnl_team_1
        : winner === "team_2"
            ? tradeState.net_pnl_team_2
            : 0;
    const achievedYield = targetedPnl > 0
        ? Math.round((settledPnl / targetedPnl) * 10000) / 100
        : 0;
    const isBusy = isSubmitting || isVoiding;
    const canSubmit = winner !== null && !isBusy;

    function handleBack(): void {
        if (isEditMode) {
            router.push(historyPath);
        } else {
            router.push(tradePath);
        }
    }

    async function handleConfirm(): Promise<void> {
        if (isSubmittingRef.current || isVoidingRef.current || winner === null) return;

        isSubmittingRef.current = true;
        setIsSubmitting(true);
        setError(null);

        const payload: SettleTradeRequest = {
            winner,
            sentiment,
            fav_sub_30_loss: favSub30Loss,
            lowest_fav_odds_paise: parseIntegerOdds(lowestFavOddsPaise),
            post_low_bet_number: postLowBetNumber,
            post_low_bet_stake: postLowBetStake,
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

    /* -- render ------------------------------------------------------------- */

    return (
        <div className="settle-page animate-fade-in">
            {/* -- Page Header (spans full width) ------------------------------ */}
            <div className="settle-page__header">
                <button
                    type="button"
                    className="settle-page__back-btn"
                    onClick={handleBack}
                    aria-label={isEditMode ? "Back to history" : "Back to trade"}
                >
                    <ArrowLeft size={16} aria-hidden="true" />
                    <span>{isEditMode ? "Back to History" : "Back to Trade"}</span>
                </button>
                <h1 className="dashboard-hero-title dashboard-hero-rainbow">
                    {isEditMode ? "Edit Settlement" : "Settle Match"}
                </h1>
            </div>

            {/* -- Left Column (sticky) ---------------------------------------- */}
            <div className="settle-page__left">
                <div className="settle-page__match-context">
                    <span className="settle-page__match-vs">
                        <CockpitTeamText team={tradeState.team_1} />
                        <span className="settle-page__match-divider">vs</span>
                        <CockpitTeamText team={tradeState.team_2} />
                    </span>
                    {tradeState.stadium && (
                        <span className="settle-page__match-venue">
                            {tradeState.stadium}
                        </span>
                    )}
                </div>

                <SettlementResultSelector
                    team1={tradeState.team_1}
                    team2={tradeState.team_2}
                    winner={winner}
                    onWinnerChange={(w) => {
                        setWinner(w);
                        setVoidConfirmPending(false);
                    }}
                />

                {winner !== null && (
                    <LiveTradeSettlementPreview
                        team1={tradeState.team_1}
                        team2={tradeState.team_2}
                        winner={winner}
                        targetedPnl={targetedPnl}
                        settledPnl={settledPnl}
                        achievedYield={achievedYield}
                    />
                )}
            </div>

            {/* -- Right Column ------------------------------------------------ */}
            <div className="settle-page__right">
                <div className="settle-page__right-card">
                    <h2 className="settle-page__card-title">Match Journal</h2>
                    <SettlementTradeNotes
                        sentiment={sentiment}
                        favSub30Loss={favSub30Loss}
                        lowestFavOddsPaise={lowestFavOddsPaise}
                        selectedBetNumber={postLowBetNumber}
                        bets={bets}
                        mistakeTags={mistakeTags}
                        mistakeNote={mistakeNote}
                        onSentimentChange={setSentiment}
                        onFavSub30LossChange={setFavSub30Loss}
                        onLowestFavOddsPaiseChange={setLowestFavOddsPaise}
                        onBetNumberChange={(num, stake) => {
                            setPostLowBetNumber(num);
                            setPostLowBetStake(stake);
                        }}
                        onMistakeTagsChange={setMistakeTags}
                        onMistakeNoteChange={setMistakeNote}
                    />
                </div>
            </div>

            {/* -- Error ------------------------------------------------------- */}
            {error && (
                <p className="settle-page__error" role="alert" style={ERROR_GRID_STYLE}>
                    {error}
                </p>
            )}

            {/* -- Footer (spans both columns) --------------------------------- */}
            <SettlePageFooter
                isEditMode={isEditMode}
                isBusy={isBusy}
                isSubmitting={isSubmitting}
                isVoiding={isVoiding}
                canSubmit={canSubmit}
                voidConfirmPending={voidConfirmPending}
                onBack={handleBack}
                onVoid={() => { void handleVoidMatch(); }}
                onConfirm={() => { void handleConfirm(); }}
            />
        </div>
    );
}

/* -- page export ------------------------------------------------------------ */

export default function SettlePage() {
    return (
        <Suspense fallback={<SettlePageSkeleton />}>
            <SettlePageInner />
        </Suspense>
    );
}
