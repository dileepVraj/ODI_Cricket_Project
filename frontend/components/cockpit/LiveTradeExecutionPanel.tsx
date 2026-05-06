"use client";

import { useEffect, useState } from "react";
import type { AddBetPayload } from "@/lib/cockpit/live-trade-bets-api";
import type { TradeStateResponse } from "./cockpit-api";
import { useLiveTradeMarketOdds } from "@/lib/cockpit/LiveTradeMarketOddsContext";
import LiveTradeToast from "./LiveTradeToast";
import {
    buildTradeBetPreview,
    parsePositiveAmount,
    type BetType,
} from "@/lib/cockpit/live-trade-market-odds";
import { getTeamColor } from "@/lib/cockpit/team-colors";
import CockpitTeamText from "./CockpitTeamText";
import LiveTradeBookPanel from "./LiveTradeBookPanel";
import { formatMoney, parseOddsInput, toneClass } from "./live-trade-execution-utils";
import { useLiveTradeToast } from "@/lib/cockpit/useLiveTradeToast";

interface LiveTradeExecutionPanelProps {
    team1: string;
    team2: string;
    tradeState: TradeStateResponse;
    onPlaceBet: (payload: AddBetPayload) => Promise<void>;
    onExecuteCashOut: (payload: AddBetPayload) => Promise<void>;
    onSettleClick: () => void;
    onCancelClick: () => void;
    isReadOnly?: boolean;
}

export default function LiveTradeExecutionPanel({
    team1,
    team2,
    tradeState,
    onPlaceBet,
    onExecuteCashOut,
    onSettleClick,
    onCancelClick,
    isReadOnly = false,
}: LiveTradeExecutionPanelProps) {
    const { currentMarketOdds, setFavoriteTeam, setBackOddsPaise, setLayOddsPaise } = useLiveTradeMarketOdds();
    const [betType, setBetType] = useState<BetType>("BACK");
    const [stakeInput, setStakeInput] = useState("");
    const [isSubmitting, setIsSubmitting] = useState(false);
    const { clearToast, showToast, toast } = useLiveTradeToast();
    const teamOptions = team1 === team2 ? [team1] : [team1, team2];

    useEffect(() => {
        setBetType("BACK");
        setStakeInput("");
        clearToast();
    }, [clearToast, tradeState.id, team1, team2]);

    const stakeValue = parsePositiveAmount(stakeInput);
    const betPreview = stakeValue !== null
        ? buildTradeBetPreview(team1, team2, currentMarketOdds, betType, stakeValue)
        : null;

    const projectedTeam1Net = betPreview
        ? tradeState.net_pnl_team_1 + betPreview.team1Pnl
        : null;
    const projectedTeam2Net = betPreview
        ? tradeState.net_pnl_team_2 + betPreview.team2Pnl
        : null;

    async function handlePlaceBet(): Promise<void> {
        if (isSubmitting || isReadOnly) {
            return;
        }

        if (!betPreview) {
            showToast({
                kind: "error",
                message: "Enter valid odds and a stake before placing the bet.",
            });
            return;
        }

        setIsSubmitting(true);

        try {
            await onPlaceBet(betPreview.payload);
            setBackOddsPaise(null);
            setLayOddsPaise(null);
            setBetType("BACK");
            setStakeInput("");
            showToast({
                kind: "success",
                message: "Bet placed.",
            });
        } catch (submitError: unknown) {
            showToast({
                kind: "error",
                message: submitError instanceof Error ? submitError.message : "Could not place the bet.",
            });
        } finally {
            setIsSubmitting(false);
        }
    }

    return (
        <section className="glass-card live-trade-execution-panel">
            <div className="live-trade-execution-panel__header">
                <div className="min-w-0">
                    <p className="live-trade-execution-panel__eyebrow">Live execution</p>
                </div>
                {!isReadOnly && (
                    <div className="live-trade-execution-panel__header-actions">
                        <button
                            type="button"
                            className="btn-ghost live-trade-execution-panel__cancel-btn"
                            onClick={onCancelClick}
                            aria-label="Cancel the current trade and return to match setup"
                            title="Cancel this trade"
                        >
                            Cancel Trade
                        </button>
                        <button
                            type="button"
                            className="btn-primary live-trade-execution-panel__settle-btn"
                            onClick={onSettleClick}
                            aria-label="Settle the current trade"
                            title="Settle the current trade"
                        >
                            Settle Match
                        </button>
                    </div>
                )}
            </div>

            <div className="live-trade-execution-panel__board">
                <section className="live-trade-execution-panel__column live-trade-execution-panel__column--market">
                    <div className="live-trade-execution-panel__field">
                        <label className="live-trade-execution-panel__label cockpit-trade-summary-label">
                            Favorite team
                        </label>
                        <div className="fav-team-toggle" role="radiogroup" aria-label="Favorite team">
                            {teamOptions.map((team) => {
                                const isActive = currentMarketOdds.favoriteTeam === team;
                                return (
                                    <button
                                        key={team}
                                        type="button"
                                        role="radio"
                                        aria-checked={isActive}
                                        aria-label={`Select ${team} as favorite`}
                                        disabled={isReadOnly}
                                        className={`fav-team-toggle__btn${isActive ? " fav-team-toggle__btn--active" : ""}`}
                                        style={isActive ? { "--team-accent": getTeamColor(team) } as React.CSSProperties : undefined}
                                        onClick={() => setFavoriteTeam(team)}
                                    >
                                        {team}
                                    </button>
                                );
                            })}
                        </div>
                    </div>

                    <div className="live-trade-execution-panel__odds-grid">
                        <div className="live-trade-execution-panel__field live-trade-execution-panel__field--odds live-trade-execution-panel__field--back">
                            <label className="live-trade-execution-panel__label cockpit-trade-summary-label" htmlFor="live-market-back">
                                Back odds (p)
                            </label>
                            <input
                                id="live-market-back"
                                type="text"
                                inputMode="numeric"
                                pattern="[0-9]*"
                                autoComplete="off"
                                className="context-input live-trade-execution-panel__odds-input"
                                placeholder="60"
                                value={currentMarketOdds.backOddsPaise === null ? "" : String(currentMarketOdds.backOddsPaise)}
                                onChange={(event) => {
                                    setBackOddsPaise(parseOddsInput(event.currentTarget.value));
                                }}
                                disabled={isReadOnly}
                            />
                        </div>

                        <div className="live-trade-execution-panel__field live-trade-execution-panel__field--odds live-trade-execution-panel__field--lay">
                            <label className="live-trade-execution-panel__label cockpit-trade-summary-label" htmlFor="live-market-lay">
                                Lay odds (p)
                            </label>
                            <input
                                id="live-market-lay"
                                type="text"
                                inputMode="numeric"
                                pattern="[0-9]*"
                                autoComplete="off"
                                className="context-input live-trade-execution-panel__odds-input"
                                placeholder="62"
                                value={currentMarketOdds.layOddsPaise === null ? "" : String(currentMarketOdds.layOddsPaise)}
                                onChange={(event) => {
                                    setLayOddsPaise(parseOddsInput(event.currentTarget.value));
                                }}
                                disabled={isReadOnly}
                            />
                        </div>
                    </div>

                </section>

                <section className="live-trade-execution-panel__column live-trade-execution-panel__column--slip">
                    <div className="live-trade-execution-panel__toggle-row" role="group" aria-label="Bet type selection">
                        <button
                            type="button"
                            className={`live-trade-execution-panel__mode-button live-trade-execution-panel__mode-button--back ${betType === "BACK" ? "is-active" : ""}`}
                            aria-pressed={betType === "BACK"}
                            onClick={() => setBetType("BACK")}
                            disabled={isReadOnly}
                        >
                            BACK
                        </button>
                        <button
                            type="button"
                            className={`live-trade-execution-panel__mode-button live-trade-execution-panel__mode-button--lay ${betType === "LAY" ? "is-active" : ""}`}
                            aria-pressed={betType === "LAY"}
                            onClick={() => setBetType("LAY")}
                            disabled={isReadOnly}
                        >
                            LAY
                        </button>
                    </div>

                    <div className="live-trade-execution-panel__field">
                        <label className="live-trade-execution-panel__label cockpit-trade-summary-label" htmlFor="live-trade-stake">
                            Stake
                        </label>
                        <input
                            id="live-trade-stake"
                            type="number"
                            min={1}
                            step={0.01}
                            inputMode="decimal"
                            autoComplete="off"
                            className="context-input live-trade-execution-panel__stake-input"
                            placeholder="500"
                            value={stakeInput}
                            onChange={(event) => setStakeInput(event.currentTarget.value)}
                            disabled={isReadOnly}
                        />
                    </div>

                    <div className="live-trade-execution-panel__preview-grid" aria-live="polite">
                        <div className="live-trade-execution-panel__tile">
                            <div className="live-trade-execution-panel__tile-label">
                                Net if <CockpitTeamText team={team1} /> wins
                            </div>
                            <div className={`live-trade-execution-panel__tile-value font-numeric font-semibold ${projectedTeam1Net !== null ? toneClass(projectedTeam1Net) : ""}`}>
                                {projectedTeam1Net !== null ? formatMoney(projectedTeam1Net) : "--"}
                            </div>
                        </div>
                        <div className="live-trade-execution-panel__tile">
                            <div className="live-trade-execution-panel__tile-label">
                                Net if <CockpitTeamText team={team2} /> wins
                            </div>
                            <div className={`live-trade-execution-panel__tile-value font-numeric font-semibold ${projectedTeam2Net !== null ? toneClass(projectedTeam2Net) : ""}`}>
                                {projectedTeam2Net !== null ? formatMoney(projectedTeam2Net) : "--"}
                            </div>
                        </div>
                    </div>

                    <button
                        type="button"
                        className="btn-primary live-trade-execution-panel__submit"
                        onClick={() => {
                            void handlePlaceBet();
                        }}
                        disabled={isSubmitting || betPreview === null || isReadOnly}
                    >
                        {isSubmitting ? "Placing..." : "Place bet"}
                    </button>
                </section>

                <LiveTradeBookPanel
                    className="live-trade-execution-panel__column live-trade-execution-panel__column--book"
                    compact
                    team1={team1}
                    team2={team2}
                    tradeState={tradeState}
                    onExecuteCashOut={onExecuteCashOut}
                    isReadOnly={isReadOnly}
                />
            </div>

            {toast !== null ? <LiveTradeToast toast={toast} /> : null}
        </section>
    );
}
