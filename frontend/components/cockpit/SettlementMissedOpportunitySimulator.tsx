"use client";

import type { BetResponse } from "@/lib/cockpit/live-trade-bets-api";
import type { MissedOpportunityResult } from "@/lib/cockpit/live-trade-calcs";
import type { SettleTradeRequest } from "./cockpit-api";

interface SettlementMissedOpportunitySimulatorProps {
    hasMissedSwing: boolean;
    missedSwingTeam: string;
    missedSwingBackOddsPaise: string;
    missedSwingLayOddsPaise: string;
    missedSwingBetIndex: number | null;
    missedSwingType: SettleTradeRequest["missed_swing_type"];
    showMissedOpportunitySimulator: boolean;
    team1: string;
    team2: string;
    bets: BetResponse[];
    missedOpportunityResult: MissedOpportunityResult | null;
    settledPnl: number;
    onHasMissedSwingChange: (value: boolean) => void;
    onMissedSwingTypeChange: (value: SettleTradeRequest["missed_swing_type"]) => void;
    onMissedSwingTeamChange: (value: string) => void;
    onMissedSwingBackOddsPaiseChange: (value: string) => void;
    onMissedSwingLayOddsPaiseChange: (value: string) => void;
    onMissedSwingBetIndexChange: (value: number | null) => void;
}

function formatMoney(value: number): string {
    const formatted = new Intl.NumberFormat("en-IN", {
        minimumFractionDigits: 0,
        maximumFractionDigits: 2,
    }).format(Math.abs(value));
    return value < 0 ? `Rs -${formatted}` : `Rs ${formatted}`;
}

function formatBetLabel(bet: BetResponse, index: number): string {
    return `Bet #${index + 1}: ${bet.bet_type} ${bet.team} @ ${bet.odds_paise}p - ${formatMoney(bet.stake)}`;
}

function getResultToneClass(value: number): string {
    if (value > 0) return "settle-preview--tone-profit";
    if (value < 0) return "settle-preview--tone-loss";
    return "settle-preview--tone-neutral";
}

export default function SettlementMissedOpportunitySimulator({
    hasMissedSwing,
    missedSwingTeam,
    missedSwingBackOddsPaise,
    missedSwingLayOddsPaise,
    missedSwingBetIndex,
    missedSwingType,
    showMissedOpportunitySimulator,
    team1,
    team2,
    bets,
    missedOpportunityResult,
    settledPnl,
    onHasMissedSwingChange,
    onMissedSwingTypeChange,
    onMissedSwingTeamChange,
    onMissedSwingBackOddsPaiseChange,
    onMissedSwingLayOddsPaiseChange,
    onMissedSwingBetIndexChange,
}: SettlementMissedOpportunitySimulatorProps) {
    if (!showMissedOpportunitySimulator) {
        return null;
    }

    const isProfitType = missedSwingType === "PROFIT";
    const isScratchType = missedSwingType === "SCRATCH";
    const actualTradeLoss = Math.min(settledPnl, 0);
    const bottomLineDelta = missedOpportunityResult
        ? missedOpportunityResult.netPnl - actualTradeLoss
        : null;

    function handleBetSelect(value: string): void {
        if (value === "") {
            onMissedSwingBetIndexChange(null);
            return;
        }

        const betIndex = Number.parseInt(value, 10);
        if (Number.isInteger(betIndex) && betIndex >= 0) {
            onMissedSwingBetIndexChange(betIndex);
            return;
        }

        onMissedSwingBetIndexChange(null);
    }

    return (
        <div className="settle-modal__notes">
            <div className="settle-modal__notes-field">
                <p className="settle-result-selector__label">
                    Did you miss an opportunity to escape this loss?
                </p>
                <div className="settle-result-selector__teams" role="radiogroup" aria-label="Missed opportunity type">
                    <button
                        type="button"
                        className={`settle-result-selector__team-btn${hasMissedSwing && isProfitType ? " settle-result-selector__team-btn--active" : ""}`}
                        role="radio"
                        aria-checked={hasMissedSwing && isProfitType}
                        onClick={() => {
                            onHasMissedSwingChange(true);
                            onMissedSwingTypeChange("PROFIT");
                        }}
                    >
                        <span className="settle-result-selector__team-name">Missed Profitable Cashout</span>
                        <span className="settle-result-selector__team-hint">sets type to profit</span>
                    </button>
                    <button
                        type="button"
                        className={`settle-result-selector__team-btn${hasMissedSwing && isScratchType ? " settle-result-selector__team-btn--active" : ""}`}
                        role="radio"
                        aria-checked={hasMissedSwing && isScratchType}
                        onClick={() => {
                            onHasMissedSwingChange(true);
                            onMissedSwingTypeChange("SCRATCH");
                        }}
                    >
                        <span className="settle-result-selector__team-name">Refused Scratch / Breakeven</span>
                        <span className="settle-result-selector__team-hint">sets type to scratch</span>
                    </button>
                    <button
                        type="button"
                        className={`settle-result-selector__team-btn${!hasMissedSwing ? " settle-result-selector__team-btn--active" : ""}`}
                        role="radio"
                        aria-checked={!hasMissedSwing}
                        onClick={() => {
                            onHasMissedSwingChange(false);
                            onMissedSwingTypeChange(null);
                        }}
                    >
                        <span className="settle-result-selector__team-name">No Missed Opportunities</span>
                        <span className="settle-result-selector__team-hint">clears the simulator</span>
                    </button>
                </div>
            </div>

            {hasMissedSwing && (
                <>
                    <div className="settle-modal__notes-field">
                        <label className="settle-modal__field-label" htmlFor="missed-swing-team">
                            Team
                        </label>
                        <select
                            id="missed-swing-team"
                            className="context-input w-full"
                            value={missedSwingTeam}
                            onChange={(e) => onMissedSwingTeamChange(e.currentTarget.value)}
                        >
                            <option value="">Select team</option>
                            <option value={team1}>{team1}</option>
                            <option value={team2}>{team2}</option>
                        </select>
                    </div>

                    <div className="settle-modal__notes-row">
                        <div className="settle-modal__notes-field">
                            <label className="settle-modal__field-label" htmlFor="missed-swing-back-odds">
                                Shortened Odds - Back (paise)
                            </label>
                            <input
                                id="missed-swing-back-odds"
                                type="text"
                                inputMode="numeric"
                                className="context-input w-full"
                                placeholder="e.g. 56"
                                value={missedSwingBackOddsPaise}
                                onChange={(e) => onMissedSwingBackOddsPaiseChange(e.currentTarget.value)}
                            />
                        </div>
                        <div className="settle-modal__notes-field">
                            <label className="settle-modal__field-label" htmlFor="missed-swing-lay-odds">
                                Shortened Odds - Lay (paise)
                            </label>
                            <input
                                id="missed-swing-lay-odds"
                                type="text"
                                inputMode="numeric"
                                className="context-input w-full"
                                placeholder="e.g. 57"
                                value={missedSwingLayOddsPaise}
                                onChange={(e) => onMissedSwingLayOddsPaiseChange(e.currentTarget.value)}
                            />
                        </div>
                    </div>

                    <div className="settle-modal__notes-field">
                        <label className="settle-modal__field-label" htmlFor="missed-swing-bet-index">
                            Bet Timeline
                        </label>
                        <select
                            id="missed-swing-bet-index"
                            className="context-input w-full"
                            value={missedSwingBetIndex !== null ? String(missedSwingBetIndex) : ""}
                            onChange={(e) => handleBetSelect(e.currentTarget.value)}
                        >
                            <option value="">Select last bet placed when odds shortened</option>
                            {bets.map((bet, index) => (
                                <option key={bet.id} value={String(index)}>
                                    {formatBetLabel(bet, index)}
                                </option>
                            ))}
                        </select>
                    </div>

                    <div className="glass-card animate-fade-in p-4" aria-live="polite">
                        <div className="mb-3">
                            <span className="settle-preview__stat-label">Live Calculation</span>
                        </div>
                        <div className="flex items-center justify-between gap-4">
                            <span className="settle-preview__stat-label">Cumulative Amount Risked</span>
                            <span className="settle-preview__stat-value font-numeric">
                                {missedOpportunityResult ? formatMoney(missedOpportunityResult.cumulativeStake) : "--"}
                            </span>
                        </div>
                        <div className="mt-3 flex items-center justify-between gap-4">
                            <span className="settle-preview__stat-label">
                                {isScratchType ? "SIMULATED SCRATCH PNL" : "SIMULATED CASHOUT PNL"}
                            </span>
                            <span
                                className={`settle-preview__stat-value font-numeric ${
                                    missedOpportunityResult ? getResultToneClass(missedOpportunityResult.netPnl) : ""
                                }`}
                            >
                                {missedOpportunityResult ? formatMoney(missedOpportunityResult.netPnl) : "--"}
                            </span>
                        </div>
                        <div className="mt-3 flex items-center justify-between gap-4">
                            <span className="settle-preview__stat-label">ACTUAL TRADE LOSS</span>
                            <span className="settle-preview__stat-value font-numeric">
                                {formatMoney(actualTradeLoss)}
                            </span>
                        </div>
                        <div className="mt-3 flex items-center justify-between gap-4">
                            <span className="settle-preview__stat-label text-tier-negative">
                                {isScratchType ? "AVOIDABLE LOSS" : "COST OF GREED"}
                            </span>
                            <span className="settle-preview__stat-value font-numeric text-tier-negative">
                                {bottomLineDelta !== null ? formatMoney(bottomLineDelta) : "--"}
                            </span>
                        </div>
                    </div>
                </>
            )}
        </div>
    );
}
