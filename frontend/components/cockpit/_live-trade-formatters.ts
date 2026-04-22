/**
 * _live-trade-formatters.ts
 * Pure formatting and domain-logic utilities for the Live Trade Cockpit.
 * No React, no imports from outside this module.
 */

import type { LiveBall, LiveData } from "./cockpit-types";

export function extractGmid(url: string | null | undefined): string | null {
    if (!url) return null;
    const match = url.match(/game-details\/4\/(\d+)/);
    return match ? match[1] : null;
}

export function getSecondsAgo(isoString: string): string {
    const diff = Math.floor((Date.now() - new Date(isoString).getTime()) / 1000);
    if (diff < 60) return `${diff}s ago`;
    return `${Math.floor(diff / 60)}m ago`;
}

export function formatScore(runs: number, wickets: number): string {
    return `${runs}-${wickets}`;
}

export function formatOvers(overs: string): string {
    return `(${overs})`;
}

export function formatCrr(crr: number | null): string | null {
    if (crr == null) return null;
    return `CRR ${crr.toFixed(2)}`;
}

export function formatOdds(value: number | null | undefined): string {
    if (value == null) return "—";
    return value.toFixed(2);
}

export function getBallClass(type: string): string {
    if (type === "four") return "ltc-ball ltc-ball--four";
    if (type === "six") return "ltc-ball ltc-ball--six";
    if (type === "wicket") return "ltc-ball ltc-ball--wicket";
    return "ltc-ball";
}

export function getBallLabel(ball: LiveBall): string {
    return ball.type === "wicket" ? "W" : ball.value;
}

/** Returns true when team1 is the current market favourite (lower back price = shorter odds). */
export function isTeam1Favourite(odds: LiveData["odds"]): boolean {
    return odds.team1_back <= odds.team2_back;
}

export function buildTossLine(winner: string, decision: string): string | null {
    if (!winner || !decision) return null;
    return `Toss: ${winner} chose to ${decision.toUpperCase()}`;
}

export function buildMetaLine(tossLine: string | null, stadium: string): string {
    return [tossLine, stadium ? `Venue: ${stadium}` : null]
        .filter(Boolean)
        .join("  ·  ");
}

export function buildFormatLabel(format: string | undefined, season: number): string {
    return [format?.toUpperCase(), String(season)].filter(Boolean).join(" ");
}
