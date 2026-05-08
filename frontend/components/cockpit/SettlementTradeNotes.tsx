"use client";

import type { BetResponse } from "@/lib/cockpit/live-trade-bets-api";
import type { MissedOpportunityResult } from "@/lib/cockpit/live-trade-calcs";
import type { SettleTradeRequest } from "./cockpit-api";
import SettlementMissedOpportunitySimulator from "./SettlementMissedOpportunitySimulator";

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
    missedSwingType: SettleTradeRequest["missed_swing_type"];
    showMissedOpportunitySimulator: boolean;
    team1: string;
    team2: string;
    bets: BetResponse[];
    missedOpportunityResult: MissedOpportunityResult | null;
    settledPnl: number;
    mistakeTags: string[];
    mistakeNote: string;
    onSentimentChange: (value: SettleTradeRequest["sentiment"]) => void;
    onFavSub30LossChange: (value: boolean) => void;
    onHasMissedSwingChange: (value: boolean) => void;
    onMissedSwingTypeChange: (value: SettleTradeRequest["missed_swing_type"]) => void;
    onMissedSwingTeamChange: (value: string) => void;
    onMissedSwingBackOddsPaiseChange: (value: string) => void;
    onMissedSwingLayOddsPaiseChange: (value: string) => void;
    onMissedSwingBetIndexChange: (value: number | null) => void;
    onMistakeTagsChange: (tags: string[]) => void;
    onMistakeNoteChange: (note: string) => void;
}

export default function SettlementTradeNotes({
    sentiment,
    favSub30Loss,
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
    mistakeTags,
    mistakeNote,
    onSentimentChange,
    onFavSub30LossChange,
    onHasMissedSwingChange,
    onMissedSwingTypeChange,
    onMissedSwingTeamChange,
    onMissedSwingBackOddsPaiseChange,
    onMissedSwingLayOddsPaiseChange,
    onMissedSwingBetIndexChange,
    onMistakeTagsChange,
    onMistakeNoteChange,
}: SettlementTradeNotesProps) {
    function toggleMistakeTag(slug: string): void {
        if (mistakeTags.includes(slug)) {
            onMistakeTagsChange(mistakeTags.filter((tag) => tag !== slug));
        } else {
            onMistakeTagsChange([...mistakeTags, slug]);
        }
    }

    return (
        <div id="settle-trade-notes" className="settle-modal__notes">
            <SettlementMissedOpportunitySimulator
                hasMissedSwing={hasMissedSwing}
                missedSwingTeam={missedSwingTeam}
                missedSwingBackOddsPaise={missedSwingBackOddsPaise}
                missedSwingLayOddsPaise={missedSwingLayOddsPaise}
                missedSwingBetIndex={missedSwingBetIndex}
                missedSwingType={missedSwingType}
                showMissedOpportunitySimulator={showMissedOpportunitySimulator}
                team1={team1}
                team2={team2}
                bets={bets}
                missedOpportunityResult={missedOpportunityResult}
                settledPnl={settledPnl}
                onHasMissedSwingChange={onHasMissedSwingChange}
                onMissedSwingTypeChange={onMissedSwingTypeChange}
                onMissedSwingTeamChange={onMissedSwingTeamChange}
                onMissedSwingBackOddsPaiseChange={onMissedSwingBackOddsPaiseChange}
                onMissedSwingLayOddsPaiseChange={onMissedSwingLayOddsPaiseChange}
                onMissedSwingBetIndexChange={onMissedSwingBetIndexChange}
            />

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
