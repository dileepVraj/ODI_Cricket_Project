/**
 * cockpit-api.ts - API client and TypeScript types for the Trading Dashboard.
 *
 * All fetch calls to /api/cockpit/* go through this file.
 * Types mirror the Pydantic schemas in cockpit/schemas.py exactly.
 * Live trade fields (bullets, P&L, close) have been removed.
 */

import { requestJson } from "@/lib/api";
import type { BetResponse } from "@/lib/cockpit/live-trade-bets-api";
import type { HomeGround } from "./cockpit-types";

const COCKPIT_BASE = "/api/cockpit";
export type TradeSentiment = "saved" | "satisfied" | "lost" | "achieved";

/** Body for POST /api/cockpit/trades and PATCH /api/cockpit/trades/{id} */
export interface CreateTradeRequest {
    season: number;
    match_date?: string | null;
    team_1: string;
    team_2: string;
    favourite_team: string;
    home_ground: HomeGround;
    stadium: string;
    toss_winner?: string | null;
    toss_decision?: string | null;
    bankroll?: number;
    opening_odds?: number | null;
    selected_team_before_toss?: string | null;
    back_odds_before_toss?: number | null;
    lay_odds_before_toss?: number | null;
    selected_team_after_toss?: string | null;
    back_odds_after_toss?: number | null;
    lay_odds_after_toss?: number | null;
}

export interface VenueOption {
    id: string;
    label: string;
}

export interface CockpitVenuesResponse {
    format: string;
    season: number;
    venues: VenueOption[];
}

/** Filters for GET /api/cockpit/trades */
export interface TradeFilters {
    format?: string;
    season?: number;
    status?: string;
    result?: "SAT" | "SAV+" | "SAV-" | "LOST" | "OPEN";
    is_fake_favourite?: boolean;
}

/** @schema TradeResponse in cockpit/schemas.py */
export interface TradeResponse {
    id: number;
    season: number;
    match_date: string | null;
    team_1: string;
    team_2: string;
    favourite_team: string;
    home_ground: HomeGround;
    stadium: string;
    status: "DRAFT" | "ACTIVE" | "SETTLED" | "VOID";
    toss_winner: string | null;
    toss_decision: "bat" | "field" | null;
    bankroll: number;
    opening_odds: number | null;
    total_stake: number | null;
    target_profit: number | null;
    profit_80pct: number | null;
    exit_target_odds: number | null;
    breakeven_odds: number | null;
    pct_of_target: number | null;
    pct_return_on_stake: number | null;
    exit_odds: number | null;
    bullet_05_odds: number | null;
    bullet_05_stake: number | null;
    bullet_1_odds: number | null;
    bullet_1_stake: number | null;
    bullet_2_odds: number | null;
    bullet_2_stake: number | null;
    bullet_3_odds: number | null;
    bullet_3_stake: number | null;
    selected_team_before_toss: string | null;
    back_odds_before_toss: number | null;
    lay_odds_before_toss: number | null;
    selected_team_after_toss: string | null;
    back_odds_after_toss: number | null;
    lay_odds_after_toss: number | null;
    fav_reached_130: boolean;
    is_fake_favourite: boolean;
    notes: string | null;
    crex_url: string | null;
    result: string | null;
    winner: "team_1" | "team_2" | "tie" | null;
    actual_profit: number | null;
    trade_sentiment: TradeSentiment | null;
    fav_sub_30_loss: boolean;
    missed_swing_team?: string | null;
    missed_swing_back_odds?: number | null;
    missed_swing_lay_odds?: number | null;
    missed_swing_bet_index?: number | null;
    missed_swing_cumulative_stake?: number | null;
    missed_swing_net_pnl?: number | null;
    trade_mistakes?: string | null;
    targeted_pnl: number | null;
    achieved_yield_percentage: number | null;
    total_volume_wagered: number;
    created_at: string;
    updated_at: string;
}

/** @schema TradeSummaryResponse in cockpit/schemas.py */
export interface TradeSummaryResponse {
    total_pnl: number;
    win_rate: number;
    avg_pct_of_target: number | null;
    fake_f_pnl: number;
    running_pnl: number[];
}

/** @schema TradeMistakes in cockpit/schemas.py */
export interface TradeMistakes {
    tags: string[];
    note: string | null;
}

/** @schema SettleTradeRequest in cockpit/schemas.py */
export interface SettleTradeRequest {
    winner: "team_1" | "team_2" | "tie";
    sentiment: TradeSentiment;
    fav_sub_30_loss: boolean;
    missed_swing_team: string | null;
    missed_swing_back_odds: number | null;
    missed_swing_lay_odds: number | null;
    missed_swing_bet_index: number | null;
    missed_swing_cumulative_stake: number | null;
    missed_swing_net_pnl: number | null;
    targeted_pnl: number;
    achieved_yield: number;
    trade_mistakes: TradeMistakes | null;
}

/** @schema TradeRestoreRequest in cockpit/schemas.py */
export interface RestoreTradeSnapshotRequest {
    trade: TradeResponse;
    bets: BetResponse[];
}

/** @schema TradeStateResponse in cockpit/schemas.py */
export interface TradeStateResponse extends TradeResponse {
    net_pnl_team_1: number;
    net_pnl_team_2: number;
    total_exposure: number;
    available_bankroll: number;
}

export interface CockpitTeamsResponse {
    format: string;
    season: number;
    teams: string[];
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
    if (filters?.format !== undefined) {
        params.set("format", filters.format);
    }
    if (filters?.status !== undefined) {
        params.set("status", filters.status);
    }

    const query = params.toString();
    return query ? `?${query}` : "";
}

export async function createTrade(body: CreateTradeRequest, format = "ipl"): Promise<TradeResponse> {
    return cockpitFetch<TradeResponse>(`/trades?format=${encodeURIComponent(format)}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
    });
}

export async function updateTrade(
    id: number,
    body: CreateTradeRequest,
    format = "ipl"
): Promise<TradeResponse> {
    return cockpitFetch<TradeResponse>(`/trades/${id}?format=${encodeURIComponent(format)}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
    });
}

export async function settleTrade(
    tradeId: number,
    body: SettleTradeRequest,
    format = "ipl"
): Promise<TradeResponse> {
    return cockpitFetch<TradeResponse>(`/trades/${tradeId}/settle?format=${encodeURIComponent(format)}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
    });
}

export async function resettleTrade(
    tradeId: number,
    body: SettleTradeRequest,
    format = "ipl"
): Promise<TradeResponse> {
    return cockpitFetch<TradeResponse>(`/trades/${tradeId}/settlement?format=${encodeURIComponent(format)}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
    });
}

export async function restoreTradeSnapshot(
    body: RestoreTradeSnapshotRequest,
    format = "ipl"
): Promise<TradeResponse> {
    return cockpitFetch<TradeResponse>(`/trades/restore?format=${encodeURIComponent(format)}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
    });
}

export async function voidTrade(tradeId: number, format = "ipl"): Promise<TradeResponse> {
    return cockpitFetch<TradeResponse>(`/trades/${tradeId}/void?format=${encodeURIComponent(format)}`, {
        method: "POST",
        headers: { Accept: "application/json" },
    });
}

export async function fetchCockpitTeams(format: string): Promise<string[]> {
    const params = new URLSearchParams();
    params.set("format", format);
    const data = await cockpitFetch<CockpitTeamsResponse>(`/teams?${params.toString()}`);
    return data.teams;
}

export async function fetchCockpitVenues(format: string): Promise<VenueOption[]> {
    const params = new URLSearchParams();
    params.set("format", format);
    const data = await cockpitFetch<CockpitVenuesResponse>(`/venues?${params.toString()}`);
    return data.venues;
}

export async function getSummary(season?: number, format?: string): Promise<TradeSummaryResponse> {
    const params = new URLSearchParams();
    if (season !== undefined) {
        params.set("season", String(season));
    }
    if (format !== undefined) {
        params.set("format", format);
    }
    const query = params.toString();
    return cockpitFetch<TradeSummaryResponse>(`/summary${query ? `?${query}` : ""}`);
}

export async function listTrades(filters?: TradeFilters): Promise<TradeResponse[]> {
    return cockpitFetch<TradeResponse[]>(`/trades${buildQueryString(filters)}`);
}

export async function getTrade(id: number, format = "ipl"): Promise<TradeResponse> {
    return cockpitFetch<TradeResponse>(`/trades/${id}?format=${encodeURIComponent(format)}`);
}

export async function fetchTradeState(id: number, format = "ipl"): Promise<TradeStateResponse> {
    return cockpitFetch<TradeStateResponse>(`/trades/${id}/state?format=${encodeURIComponent(format)}`);
}

export async function deleteTrade(id: number, format = "ipl"): Promise<void> {
    await cockpitFetch<{ deleted: boolean }>(`/trades/${id}?format=${encodeURIComponent(format)}`, {
        method: "DELETE",
        headers: { Accept: "application/json" },
    });
}

export async function fetchTradeById(id: number, format = "ipl"): Promise<TradeResponse> {
    return cockpitFetch<TradeResponse>(`/trades/${id}?format=${encodeURIComponent(format)}`);
}
