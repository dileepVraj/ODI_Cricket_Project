"use client";

import type { TradeResponse } from "./cockpit-api";
import type { BulletInputState, BulletNumber } from "./cockpit-types";

interface CockpitTradeDetailsProps {
    trade: TradeResponse;
    bulletInputs: BulletInputState;
    bulletLoading: BulletNumber | null;
    bulletError: string | null;
    deleteError: string | null;
    onBulletInputChange: (bulletNumber: BulletNumber, field: "odds" | "stake", value: string) => void;
    onAddBullet: (bulletNumber: BulletNumber) => void;
    onRequestClose: (tradeId: number) => void;
    onDelete: () => void;
}

interface SummaryItem {
    label: string;
    value: string;
    tone?: "elite";
}

const BULLET_ROWS: Array<{
    number: BulletNumber;
    title: string;
    subtitle: string;
    tag?: string;
    tagClassName?: string;
}> = [
    { number: 0, title: "Bullet 0.5", subtitle: "Early Entry" },
    { number: 1, title: "Bullet 1", subtitle: "Main Entry", tag: "PRIMARY", tagClassName: "cockpit-bullet-tag cockpit-bullet-tag--primary" },
    { number: 2, title: "Bullet 2", subtitle: "Average Down" },
    { number: 3, title: "Bullet 3", subtitle: "Emergency", tag: "HIGH RISK", tagClassName: "cockpit-bullet-tag cockpit-bullet-tag--danger" },
];

function getBulletFields(trade: TradeResponse, num: BulletNumber): { odds: number | null; stake: number | null } {
    if (num === 0) return { odds: trade.bullet_05_odds, stake: trade.bullet_05_stake };
    if (num === 1) return { odds: trade.bullet_1_odds, stake: trade.bullet_1_stake };
    if (num === 2) return { odds: trade.bullet_2_odds, stake: trade.bullet_2_stake };
    return { odds: trade.bullet_3_odds, stake: trade.bullet_3_stake };
}

function formatAmount(value: number | null): string {
    if (value === null) {
        return "N/A";
    }
    return `INR ${value.toFixed(2)}`;
}

function formatTossSummary(winner: string | null, decision: string | null): string {
    const normalizedDecision = decision?.toLowerCase() === "bw"
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

export default function CockpitTradeDetails({
    trade,
    bulletInputs,
    bulletLoading,
    bulletError,
    deleteError,
    onBulletInputChange,
    onAddBullet,
    onRequestClose,
    onDelete,
}: CockpitTradeDetailsProps) {
    const summaryItems: SummaryItem[] = [
        { label: "Match", value: `${trade.team_1} vs ${trade.team_2}` },
        { label: "Favourite", value: trade.favourite_team, tone: "elite" },
        { label: "Venue", value: trade.stadium },
        { label: "Bankroll", value: formatAmount(trade.bankroll) },
        { label: "Home Ground", value: trade.home_ground },
        { label: "Toss", value: formatTossSummary(trade.toss_winner, trade.toss_decision) },
    ] as const;

    const hasAnyBullet = trade.bullet_05_odds !== null || trade.bullet_1_odds !== null || trade.bullet_2_odds !== null || trade.bullet_3_odds !== null;

    return (
        <>
            <div className="cockpit-trade-header">
                <h2 className="cockpit-trade-title">
                    Live Trade - {trade.favourite_team}{" "}
                    <span className="cockpit-trade-title-subtle">
                        ({trade.team_1} vs {trade.team_2})
                    </span>
                </h2>
            </div>

            <div className="cockpit-trade-summary-grid">
                {summaryItems.map((item) => (
                    <div key={item.label} className="cockpit-trade-summary-item">
                        <p className="cockpit-trade-summary-label">{item.label}</p>
                        <p className={`cockpit-trade-summary-value${item.tone === "elite" ? " cockpit-trade-summary-value--elite" : ""}`}>
                            {item.value}
                        </p>
                    </div>
                ))}
            </div>

            <div className="cockpit-trade-metrics">
                {trade.total_stake !== null && (
                    <div className="cockpit-trade-metric">
                        <p className="cockpit-trade-metric-label">Total Staked</p>
                        <p className="cockpit-trade-metric-value">{formatAmount(trade.total_stake)}</p>
                    </div>
                )}
                {trade.target_profit !== null && (
                    <div className="cockpit-trade-metric">
                        <p className="cockpit-trade-metric-label">Target Profit</p>
                        <p className="cockpit-trade-metric-value">{formatAmount(trade.target_profit)}</p>
                    </div>
                )}
                {trade.exit_target_odds !== null && (
                    <div className="cockpit-trade-metric">
                        <p className="cockpit-trade-metric-label">Exit Target</p>
                        <p className="cockpit-trade-metric-value">{trade.exit_target_odds.toFixed(2)}</p>
                    </div>
                )}
                {trade.breakeven_odds !== null && (
                    <div className="cockpit-trade-metric">
                        <p className="cockpit-trade-metric-label">Break-even</p>
                        <p className="cockpit-trade-metric-value cockpit-trade-metric-value--danger">
                            {trade.breakeven_odds.toFixed(2)}
                        </p>
                    </div>
                )}
            </div>

            {trade.exit_target_odds !== null && trade.opening_odds !== null && trade.exit_target_odds > trade.opening_odds && (
                <div className="cockpit-trade-warning">
                    WARNING: Exit target is above entry price - check your bullets
                </div>
            )}

            {trade.alert_bullet3_active === true && (
                <div className="cockpit-trade-warning cockpit-trade-warning--strong">
                    WARNING: Emergency bullet active. 3 of 4 losses in historical data used Bullet 3.
                </div>
            )}

            <div>
                <p className="cockpit-trade-section-label">Bullets Used</p>
                <div className="cockpit-trade-chip-row">
                    {BULLET_ROWS.map((bullet) => {
                        const fields = getBulletFields(trade, bullet.number);
                        if (fields.odds === null) {
                            return null;
                        }
                        return (
                            <span key={bullet.number} className="cockpit-trade-chip">
                                {bullet.number === 0 ? "B0.5" : `B${bullet.number}`} @ {fields.odds.toFixed(2)} ({fields.stake !== null ? fields.stake.toFixed(2) : "0.00"} INR)
                            </span>
                        );
                    })}
                    {!hasAnyBullet && (
                        <span className="cockpit-trade-chip cockpit-trade-chip--muted">
                            No bullets added
                        </span>
                    )}
                </div>
            </div>

            <div className="cockpit-bullet-list">
                {BULLET_ROWS.map((bullet) => {
                    const fields = getBulletFields(trade, bullet.number);
                    return (
                        <div key={bullet.number} className="cockpit-bullet-row">
                            <div className="cockpit-bullet-meta">
                                <p className="cockpit-bullet-title">{bullet.title}</p>
                                <p className="cockpit-bullet-subtitle">{bullet.subtitle}</p>
                                {bullet.tag && (
                                    <span className={bullet.tagClassName ?? "cockpit-bullet-tag"}>
                                        {bullet.tag}
                                    </span>
                                )}
                            </div>
                            <input
                                type="number"
                                step="0.01"
                                min="1.01"
                                className="context-input cockpit-bullet-input"
                                placeholder="Odds"
                                value={bulletInputs[bullet.number].odds}
                                onChange={(event) => onBulletInputChange(bullet.number, "odds", event.target.value)}
                                disabled={fields.odds !== null || trade.exit_odds !== null || bulletLoading !== null}
                            />
                            <input
                                type="number"
                                step="0.5"
                                min="0.5"
                                className="context-input cockpit-bullet-input"
                                placeholder="Stake"
                                value={bulletInputs[bullet.number].stake}
                                onChange={(event) => onBulletInputChange(bullet.number, "stake", event.target.value)}
                                disabled={fields.odds !== null || trade.exit_odds !== null || bulletLoading !== null}
                            />
                            {fields.odds !== null ? (
                                <span className="cockpit-bullet-status cockpit-bullet-status--added">
                                    Added
                                </span>
                            ) : (
                                <button
                                    type="button"
                                    className="btn-primary cockpit-bullet-action"
                                    disabled={trade.exit_odds !== null || bulletLoading !== null}
                                    onClick={() => onAddBullet(bullet.number)}
                                >
                                    {bulletLoading === bullet.number ? "..." : "Add"}
                                </button>
                            )}
                        </div>
                    );
                })}
            </div>

            {trade.total_stake !== null && trade.total_stake > 0 && (
                <p className="cockpit-trade-total">
                    Total staked: <strong>{formatAmount(trade.total_stake)}</strong>
                </p>
            )}

            {bulletError && (
                <p className="cockpit-trade-error" role="alert">
                    {bulletError}
                </p>
            )}

            {trade.exit_odds === null ? (
                <div className="cockpit-trade-actions">
                    <button
                        type="button"
                        className="btn-primary cockpit-trade-action"
                        onClick={() => onRequestClose(trade.id)}
                    >
                        Close Trade
                    </button>
                    <button
                        type="button"
                        className="btn-danger cockpit-trade-action cockpit-trade-action--secondary"
                        onClick={onDelete}
                    >
                        Delete
                    </button>
                </div>
            ) : (
                <div className="cockpit-trade-success">
                    Trade closed - view in History
                </div>
            )}

            {deleteError && (
                <p className="cockpit-trade-error" role="alert">
                    {deleteError}
                </p>
            )}
        </>
    );
}
