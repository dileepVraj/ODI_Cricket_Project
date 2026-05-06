"use client";

import { useEffect, useRef, type Dispatch, type SetStateAction } from "react";
import { AlertCircle, Loader2 } from "lucide-react";
import type { TradeStateResponse } from "@/components/cockpit/cockpit-api";
import type { SettleTradeRequest } from "@/components/cockpit/cockpit-api";

export const ERROR_GRID_STYLE = { gridColumn: "1 / -1" } as const;

export function parseTradeId(value: string | string[] | undefined): number {
    const raw = Array.isArray(value) ? value[0] ?? "" : value ?? "";
    return Number(raw);
}

export function SettlePageSkeleton() {
    return (
        <div className="settle-page animate-fade-in" aria-busy="true" aria-live="polite">
            <div className="settle-page__left">
                <div className="skeleton h-8 w-48" />
                <div className="skeleton h-16 w-full rounded-lg" />
                <div className="skeleton h-32 w-full rounded-lg" />
            </div>
            <div className="settle-page__right">
                <div className="settle-page__right-card">
                    <div className="skeleton h-6 w-32" />
                    <div className="skeleton h-24 w-full rounded-lg" />
                    <div className="skeleton h-10 w-full rounded-lg" />
                    <div className="skeleton h-10 w-full rounded-lg" />
                    <div className="skeleton h-10 w-full rounded-lg" />
                    <div className="skeleton h-16 w-full rounded-lg" />
                </div>
            </div>
        </div>
    );
}

interface EditPrePopulateDispatchers {
    setWinner: Dispatch<SetStateAction<SettleTradeRequest["winner"] | null>>;
    setSentiment: Dispatch<SetStateAction<SettleTradeRequest["sentiment"]>>;
    setFavSub30Loss: Dispatch<SetStateAction<boolean>>;
    setHasMissedSwing: Dispatch<SetStateAction<boolean>>;
    setMissedSwingTeam: Dispatch<SetStateAction<string>>;
    setMissedSwingBackOddsPaise: Dispatch<SetStateAction<string>>;
    setMissedSwingLayOddsPaise: Dispatch<SetStateAction<string>>;
    setMissedSwingBetIndex: Dispatch<SetStateAction<number | null>>;
    setMistakeTags: Dispatch<SetStateAction<string[]>>;
    setMistakeNote: Dispatch<SetStateAction<string>>;
}

export function useSettleEditPrePopulate(
    isEditMode: boolean,
    tradeState: TradeStateResponse | null,
    dispatchers: EditPrePopulateDispatchers,
): void {
    const initializedRef = useRef(false);
    useEffect(() => {
        if (!isEditMode || !tradeState || initializedRef.current) return;
        initializedRef.current = true;
        const {
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
        } = dispatchers;
        if (tradeState.winner) setWinner(tradeState.winner);
        if (tradeState.trade_sentiment) setSentiment(tradeState.trade_sentiment);
        setFavSub30Loss(tradeState.fav_sub_30_loss);
        const hasMissedSwing = (
            tradeState.missed_swing_team != null
            || tradeState.missed_swing_back_odds != null
            || tradeState.missed_swing_lay_odds != null
            || tradeState.missed_swing_bet_index != null
            || tradeState.missed_swing_cumulative_stake != null
            || tradeState.missed_swing_net_pnl != null
        );
        setHasMissedSwing(hasMissedSwing);
        if (hasMissedSwing && tradeState.missed_swing_team == null) {
            setMissedSwingTeam(tradeState.team_1);
        }
        if (tradeState.missed_swing_team != null) {
            setMissedSwingTeam(tradeState.missed_swing_team);
        }
        if (tradeState.missed_swing_back_odds != null) {
            setMissedSwingBackOddsPaise(String(tradeState.missed_swing_back_odds));
        }
        if (tradeState.missed_swing_lay_odds != null) {
            setMissedSwingLayOddsPaise(String(tradeState.missed_swing_lay_odds));
        }
        if (tradeState.missed_swing_bet_index != null) {
            setMissedSwingBetIndex(tradeState.missed_swing_bet_index);
        }
        if (tradeState.trade_mistakes) {
            try {
                const parsed: unknown = JSON.parse(tradeState.trade_mistakes);
                if (typeof parsed === "object" && parsed !== null) {
                    const obj = parsed as Record<string, unknown>;
                    if (Array.isArray(obj.tags)) setMistakeTags(obj.tags as string[]);
                    if (typeof obj.note === "string" && obj.note.trim()) setMistakeNote(obj.note.trim());
                }
            } catch {
                // ignore malformed mistakes JSON
            }
        }
    // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [isEditMode, tradeState]);
}

interface SettlePageFooterProps {
    isEditMode: boolean;
    isBusy: boolean;
    isSubmitting: boolean;
    isVoiding: boolean;
    canSubmit: boolean;
    voidConfirmPending: boolean;
    onBack: () => void;
    onVoid: () => void;
    onConfirm: () => void;
}

export function SettlePageFooter({
    isEditMode,
    isBusy,
    isSubmitting,
    isVoiding,
    canSubmit,
    voidConfirmPending,
    onBack,
    onVoid,
    onConfirm,
}: SettlePageFooterProps) {
    return (
        <div className="settle-page__actions">
            <button
                type="button"
                className="btn-ghost"
                onClick={onBack}
                disabled={isBusy}
                aria-label="Cancel settlement and go back"
            >
                Cancel
            </button>
            {!isEditMode && (
                <button
                    type="button"
                    className={`btn-ghost settle-page__void-btn${voidConfirmPending ? " settle-page__void-btn--confirm" : ""}`}
                    onClick={onVoid}
                    disabled={isBusy}
                    aria-label={voidConfirmPending ? "Confirm void -- click again" : "Void the match"}
                >
                    {isVoiding && <Loader2 size={14} className="animate-spin" aria-hidden="true" />}
                    <span>
                        {isVoiding ? "Voiding..." : voidConfirmPending ? "Click again to void" : "Void Match"}
                    </span>
                </button>
            )}
            <button
                type="button"
                className="btn-primary settle-page__confirm-btn"
                onClick={onConfirm}
                disabled={!canSubmit}
                aria-label="Confirm the settlement"
            >
                {isSubmitting && <Loader2 size={14} className="animate-spin" aria-hidden="true" />}
                <span>
                    {isSubmitting
                        ? (isEditMode ? "Saving..." : "Settling...")
                        : (isEditMode ? "Save Changes" : "Confirm Settlement")}
                </span>
            </button>
        </div>
    );
}

export function SettlePageError({ message }: { message: string }) {
    return (
        <div className="settle-page animate-fade-in">
            <div className="settle-page__left">
                <div className="glass-card settle-page__section" role="alert">
                    <div className="flex items-start gap-3">
                        <AlertCircle size={20} className="mt-0.5 shrink-0 text-[var(--tier-danger)]" />
                        <div className="min-w-0">
                            <p className="text-[var(--text-primary)] font-semibold text-sm">
                                Unable to load trade
                            </p>
                            <p className="text-[var(--text-secondary)] text-xs mt-1">{message}</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
