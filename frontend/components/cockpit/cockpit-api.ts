/**
 * cockpit-api.ts - API client and TypeScript types for the Trading Cockpit.
 *
 * All fetch calls to /api/cockpit/* go through this file.
 * Types mirror the Pydantic schemas in api/cockpit/schemas.py exactly.
 */

import { requestJson } from "@/lib/api";

const COCKPIT_BASE = "/api/cockpit";

/** Body for POST /api/cockpit/trades */
export interface CreateTradeRequest {
    format?: string;
    season: number;
    match_date?: string | null;
    team_1: string;
    team_2: string;
    favourite_team: string;
    home_ground: "FAV" | "UG" | "NEU";
    stadium: string;
    toss_winner?: "FAV" | "UG" | "";
    toss_decision?: "BW" | "BT" | "";
    bankroll?: number;
    opening_odds?: number | null;
}

/** Body for PATCH /api/cockpit/trades/{id}/bullet */
export interface AddBulletRequest {
    bullet_number: 0 | 1 | 2 | 3;
    odds: number;
    stake: number;
}

/** Body for PATCH /api/cockpit/trades/{id}/close */
export interface CloseTradeRequest {
    exit_odds: number;
    fav_reached_130?: boolean;
    is_fake_favourite?: boolean;
    notes?: string | null;
}

/** Filters for GET /api/cockpit/trades */
export interface TradeFilters {
    season?: number;
    result?: "SAT" | "SAV+" | "SAV-" | "LOST" | "OPEN";
    is_fake_favourite?: boolean;
}

/** Returned by all trade endpoints. */
export interface TradeResponse {
    id: number;
    format: string;
    season: number;
    match_date: string | null;
    team_1: string;
    team_2: string;
    favourite_team: string;
    home_ground: string;
    stadium: string;
    toss_winner: string;
    toss_decision: string;
    bankroll: number;
    opening_odds: number | null;
    bullet_05_odds: number | null;
    bullet_05_stake: number | null;
    bullet_1_odds: number | null;
    bullet_1_stake: number | null;
    bullet_2_odds: number | null;
    bullet_2_stake: number | null;
    bullet_3_odds: number | null;
    bullet_3_stake: number | null;
    total_stake: number | null;
    target_profit: number | null;
    profit_80pct: number | null;
    exit_target_odds: number | null;
    breakeven_odds: number | null;
    actual_profit: number | null;
    pct_of_target: number | null;
    pct_return_on_stake: number | null;
    exit_odds: number | null;
    result: string | null;
    fav_reached_130: boolean;
    is_fake_favourite: boolean;
    notes: string | null;
    created_at: string;
    updated_at: string;
    alert_above_breakeven: boolean;
    alert_bullet3_active: boolean;
}

/** Returned by GET /api/cockpit/summary */
export interface TradeSummaryResponse {
    total_trades: number;
    total_pnl: number;
    win_rate: number;
    avg_pct_of_target: number | null;
    fake_f_pnl: number;
    non_fake_f_pnl: number;
    sat_count: number;
    savplus_count: number;
    savminus_count: number;
    lost_count: number;
    running_pnl: number[];
}

async function cockpitFetch<T>(
    path: string,
    init?: RequestInit
): Promise<T> {
    return requestJson<T>(`${COCKPIT_BASE}${path}`, init);
}

function buildQueryString(filters?: TradeFilters): string {
    const params = new URLSearchParams();

    if (filters?.season !== undefined) {
        params.set("season", String(filters.season));
    }
    if (filters?.result !== undefined) {
        params.set("result", filters.result);
    }
    if (filters?.is_fake_favourite !== undefined) {
        params.set("is_fake_favourite", String(filters.is_fake_favourite));
    }

    const query = params.toString();
    return query ? `?${query}` : "";
}

export async function createTrade(body: CreateTradeRequest): Promise<TradeResponse> {
    return cockpitFetch<TradeResponse>("/trades", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
    });
}

export async function listTrades(filters?: TradeFilters): Promise<TradeResponse[]> {
    return cockpitFetch<TradeResponse[]>(`/trades${buildQueryString(filters)}`);
}

export async function getTrade(id: number): Promise<TradeResponse> {
    return cockpitFetch<TradeResponse>(`/trades/${id}`);
}

export async function addBullet(
    id: number,
    body: AddBulletRequest
): Promise<TradeResponse> {
    return cockpitFetch<TradeResponse>(`/trades/${id}/bullet`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
    });
}

export async function closeTrade(
    id: number,
    body: CloseTradeRequest
): Promise<TradeResponse> {
    return cockpitFetch<TradeResponse>(`/trades/${id}/close`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
    });
}

export async function deleteTrade(id: number): Promise<void> {
    await cockpitFetch<{ deleted: boolean }>(`/trades/${id}`, {
        method: "DELETE",
    });
}

export async function getSummary(season?: number): Promise<TradeSummaryResponse> {
    const query = season !== undefined ? `?season=${encodeURIComponent(String(season))}` : "";
    return cockpitFetch<TradeSummaryResponse>(`/summary${query}`);
}
