"use client";

import { Suspense, useState } from "react";
import { useParams, useSearchParams } from "next/navigation";
import { ArrowLeft } from "lucide-react";
import { useCockpitTradeDraft } from "@/lib/cockpit/CockpitTradeDraftContext";
import { useLiveTradeBets } from "@/lib/cockpit/useLiveTradeBets";
import { useLiveTradeState } from "@/lib/cockpit/useLiveTradeState";
import CockpitTeamText from "@/components/cockpit/CockpitTeamText";
import LiveTradeSettlementPreview from "@/components/cockpit/LiveTradeSettlementPreview";
import SettlementResultSelector from "@/components/cockpit/SettlementResultSelector";
import SettlementTradeNotes from "@/components/cockpit/SettlementTradeNotes";
import { type SettleTradeRequest } from "@/components/cockpit/cockpit-api";

import {
    ERROR_GRID_STYLE,
    parseTradeId,
    SettlePageError,
    SettlePageFooter,
    SettlePageSkeleton,
    useSettleEditPrePopulate,
} from "./SettlePageParts";
import { useSettlePageActions } from "./useSettlePageActions";

/* -- main inner component --------------------------------------------------- */

function SettlePageInner() {
    const params = useParams<{ tradeId?: string | string[] }>();
    const searchParams = useSearchParams();
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
    const [hasMissedSwing, setHasMissedSwing] = useState(false);
    const [missedSwingTeam, setMissedSwingTeam] = useState("");
    const [missedSwingBackOddsPaise, setMissedSwingBackOddsPaise] = useState("");
    const [missedSwingLayOddsPaise, setMissedSwingLayOddsPaise] = useState("");
    const [missedSwingBetIndex, setMissedSwingBetIndex] = useState<number | null>(null);
    const [mistakeTags, setMistakeTags] = useState<string[]>([]);
    const [mistakeNote, setMistakeNote] = useState("");

    const {
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
        clearVoidConfirmPending,
        handleBack,
        handleConfirm,
        handleVoidMatch,
    } = useSettlePageActions({
        format,
        tradeId,
        isEditMode,
        tradeState: tradeState ?? null,
        bets,
        winner,
        sentiment,
        favSub30Loss,
        hasMissedSwing,
        missedSwingTeam,
        missedSwingBackOddsPaise,
        missedSwingLayOddsPaise,
        missedSwingBetIndex,
        mistakeTags,
        mistakeNote,
        resetDraftState,
    });

    useSettleEditPrePopulate(isEditMode, tradeState ?? null, {
        setWinner,
        setSentiment,
        setFavSub30Loss,
        setHasMissedSwing,
        setMissedSwingTeam,
        setMissedSwingBackOddsPaise,
        setMissedSwingLayOddsPaise,
        setMissedSwingBetIndex,
        setMistakeTags,
        setMistakeNote,
    });

    if (isLoading) return <SettlePageSkeleton />;
    if (loadError || !tradeState) {
        return <SettlePageError message={loadError ?? "Trade not found."} />;
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
                        clearVoidConfirmPending();
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
                    <h2 className="settle-page__card-title">Missed Opportunity / Cashout Simulator</h2>
                    <SettlementTradeNotes
                        sentiment={sentiment}
                        favSub30Loss={favSub30Loss}
                        hasMissedSwing={hasMissedSwing}
                        missedSwingTeam={missedSwingTeam}
                        missedSwingBackOddsPaise={missedSwingBackOddsPaise}
                        missedSwingLayOddsPaise={missedSwingLayOddsPaise}
                        missedSwingBetIndex={missedSwingBetIndex}
                        team1={tradeState.team_1}
                        team2={tradeState.team_2}
                        bets={bets}
                        missedOpportunityResult={missedOpportunityResult}
                        mistakeTags={mistakeTags}
                        mistakeNote={mistakeNote}
                        onSentimentChange={setSentiment}
                        onFavSub30LossChange={setFavSub30Loss}
                        onHasMissedSwingChange={(value) => {
                            setHasMissedSwing(value);
                            if (value && missedSwingTeam === "") {
                                setMissedSwingTeam(tradeState.team_1);
                            }
                        }}
                        onMissedSwingTeamChange={setMissedSwingTeam}
                        onMissedSwingBackOddsPaiseChange={setMissedSwingBackOddsPaise}
                        onMissedSwingLayOddsPaiseChange={setMissedSwingLayOddsPaise}
                        onMissedSwingBetIndexChange={setMissedSwingBetIndex}
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
