"use client";

import type { BetResponse } from "@/lib/cockpit/live-trade-bets-api";
import type { MissedOpportunityResult } from "@/lib/cockpit/live-trade-calcs";
import type { SettleTradeRequest } from "./cockpit-api";

const MISTAKE_OPTIONS: ReadonlyArray<{ slug: string; label: string }> = [
    { slug: "chased_loss", label: "Chased a loss" },
    { slug: "ignored_analysis", label: "Ignored analysis" },
    { slug: "late_entry", label: "Entered too late" },
    { slug: "wrong_side", label: "Wrong side" },
    { slug: "overexposed", label: "Over-exposed" },
    { slug: "no_exit_plan", label: "No exit plan" },
    { slug: "emotional_bet", label: "Emotional bet" },
    { slug: "missed_cashout", label: "Missed cash-out" },
    { slug: "poor_odds", label: "Poor odds" },
];

interface SettlementTradeNotesProps {
    sentiment: SettleTradeRequest["sentiment"];
    favSub30Loss: boolean;
    hasMissedSwing: boolean;
    missedSwingTeam: string;
    missedSwingBackOddsPaise: string;
    missedSwingLayOddsPaise: string;
    missedSwingBetIndex: number | null;
    team1: string;
    team2: string;
    bets: BetResponse[];
    missedOpportunityResult: MissedOpportunityResult | null;
    mistakeTags: string[];
    mistakeNote: string;
    onSentimentChange: (value: SettleTradeRequest["sentiment"]) => void;
    onFavSub30LossChange: (value: boolean) => void;
    onHasMissedSwingChange: (value: boolean) => void;
    onMissedSwingTeamChange: (value: string) => void;
    onMissedSwingBackOddsPaiseChange: (value: string) => void;
    onMissedSwingLayOddsPaiseChange: (value: string) => void;
    onMissedSwingBetIndexChange: (value: number | null) => void;
    onMistakeTagsChange: (tags: string[]) => void;
    onMistakeNoteChange: (note: string) => void;
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

export default function SettlementTradeNotes({
    sentiment,
    favSub30Loss,
    hasMissedSwing,
    missedSwingTeam,
    missedSwingBackOddsPaise,
    missedSwingLayOddsPaise,
    missedSwingBetIndex,
    team1,
    team2,
    bets,
    missedOpportunityResult,
    mistakeTags,
    mistakeNote,
    onSentimentChange,
    onFavSub30LossChange,
    onHasMissedSwingChange,
    onMissedSwingTeamChange,
    onMissedSwingBackOddsPaiseChange,
    onMissedSwingLayOddsPaiseChange,
    onMissedSwingBetIndexChange,
    onMistakeTagsChange,
    onMistakeNoteChange,
}: SettlementTradeNotesProps) {
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

    function toggleMistakeTag(slug: string): void {
        if (mistakeTags.includes(slug)) {
            onMistakeTagsChange(mistakeTags.filter((tag) => tag !== slug));
        } else {
            onMistakeTagsChange([...mistakeTags, slug]);
        }
    }

    return (
        <div id="settle-trade-notes" className="settle-modal__notes">
            <div className="settle-modal__notes-field">
                <p className="settle-result-selector__label">
                    Did odds shorten favorably after taking your position?
                </p>
                <div className="settle-result-selector__teams" role="radiogroup" aria-label="Missed opportunity toggle">
                    <button
                        type="button"
                        className={`settle-result-selector__team-btn${hasMissedSwing ? " settle-result-selector__team-btn--active" : ""}`}
                        role="radio"
                        aria-checked={hasMissedSwing}
                        onClick={() => onHasMissedSwingChange(true)}
                    >
                        <span className="settle-result-selector__team-name">Yes</span>
                        <span className="settle-result-selector__team-hint">simulate cashout</span>
                    </button>
                    <button
                        type="button"
                        className={`settle-result-selector__team-btn${!hasMissedSwing ? " settle-result-selector__team-btn--active" : ""}`}
                        role="radio"
                        aria-checked={!hasMissedSwing}
                        onClick={() => onHasMissedSwingChange(false)}
                    >
                        <span className="settle-result-selector__team-name">No</span>
                        <span className="settle-result-selector__team-hint">skip simulator</span>
                    </button>
                </div>
            </div>

            {hasMissedSwing && (
                <div className="settle-modal__notes">
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
                            <span className="settle-preview__stat-label">Potential Net PNL at Cashout</span>
                            <span
                                className={`settle-preview__stat-value font-numeric ${
                                    missedOpportunityResult ? getResultToneClass(missedOpportunityResult.netPnl) : ""
                                }`}
                            >
                                {missedOpportunityResult ? formatMoney(missedOpportunityResult.netPnl) : "--"}
                            </span>
                        </div>
                    </div>
                </div>
            )}

            <div className="settle-modal__notes-field">
                <label className="settle-modal__field-label" htmlFor="trade-sentiment">
                    Sentiment
                </label>
                <select
                    id="trade-sentiment"
                    className="context-input w-full"
                    value={sentiment}
                    onChange={(e) => onSentimentChange(e.currentTarget.value as SettleTradeRequest["sentiment"])}
                >
                    <option value="saved">Saved</option>
                    <option value="satisfied">Satisfied</option>
                    <option value="achieved">Achieved</option>
                    <option value="lost">Lost</option>
                </select>
            </div>

            <label className="settle-modal__checkbox-label">
                <input
                    type="checkbox"
                    checked={favSub30Loss}
                    onChange={(e) => onFavSub30LossChange(e.currentTarget.checked)}
                />
                <span>Favorite went below 30p and lost</span>
            </label>

            <div className="settle-modal__notes-field">
                <span className="settle-modal__field-label">Mistakes</span>
                <div className="settle-modal__mistake-pills" role="group" aria-label="Select trade mistakes">
                    {MISTAKE_OPTIONS.map((opt) => {
                        const active = mistakeTags.includes(opt.slug);
                        return (
                            <button
                                key={opt.slug}
                                type="button"
                                className={`settle-modal__mistake-pill${active ? " settle-modal__mistake-pill--active" : ""}`}
                                onClick={() => toggleMistakeTag(opt.slug)}
                                aria-pressed={active}
                            >
                                {opt.label}
                            </button>
                        );
                    })}
                </div>
            </div>

            <div className="settle-modal__notes-field">
                <label className="settle-modal__field-label" htmlFor="mistake-note">
                    Other Mistake (optional)
                </label>
                <input
                    id="mistake-note"
                    type="text"
                    className="context-input w-full"
                    placeholder="e.g. should have exited at 1.50"
                    value={mistakeNote}
                    onChange={(e) => onMistakeNoteChange(e.currentTarget.value)}
                />
            </div>
        </div>
    );
}
