/**
 * cockpit-api.ts - API client and TypeScript types for the Trading Dashboard.
 *
 * All fetch calls to /api/cockpit/* go through this file.
 * Types mirror the Pydantic schemas in api/cockpit/schemas.py exactly.
 */

import { requestJson } from "@/lib/api";
import type { HomeGround } from "./cockpit-types";

const COCKPIT_BASE = "/api/cockpit";

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
    odds_after_1st_over?: number | null;
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
    format?: string;
    season?: number;
    result?: "SAT" | "SAV+" | "SAV-" | "LOST" | "OPEN";
    is_fake_favourite?: boolean;
    status?: "DRAFT" | "ACTIVE";
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
    home_ground: HomeGround;
    stadium: string;
    status: "DRAFT" | "ACTIVE";
    toss_winner: string | null;
    toss_decision: "bat" | "field" | null;
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
    result: "OPEN" | "LOST" | "SAT" | "SAV+" | "SAV-" | null;
    fav_reached_130: boolean;
    is_fake_favourite: boolean;
    notes: string | null;
    created_at: string;
    updated_at: string;
    alert_above_breakeven: boolean;
    alert_bullet3_active: boolean;
    selected_team_before_toss: string | null;
    back_odds_before_toss: number | null;
    lay_odds_before_toss: number | null;
    selected_team_after_toss: string | null;
    back_odds_after_toss: number | null;
    lay_odds_after_toss: number | null;
    odds_after_1st_over: number | null;
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
    if (filters?.result !== undefined) {
        params.set("result", filters.result);
    }
    if (filters?.is_fake_favourite !== undefined) {
        params.set("is_fake_favourite", String(filters.is_fake_favourite));
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

export async function fetchTradeById(id: number): Promise<TradeResponse> {
    return cockpitFetch<TradeResponse>(`/trades/${id}`);
}

export async function getSummary(season?: number, format?: string): Promise<TradeSummaryResponse> {
    const params = new URLSearchParams();
    if (season !== undefined) {
        params.set("season", String(season));
    }
    if (format !== undefined) {
        params.set("format", format);
    }
    const query = params.toString() ? `?${params.toString()}` : "";
    return cockpitFetch<TradeSummaryResponse>(`/summary${query}`);
}

/** Body for PATCH /api/cockpit/trades/{id}/odds-after-1over */
export interface UpdateOdds1OverRequest {
    odds_after_1st_over: number;
}

export async function updateOddsAfter1Over(
    id: number,
    oddsAfter1Over: number
): Promise<TradeResponse> {
    return cockpitFetch<TradeResponse>(`/trades/${id}/odds-after-1over`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ odds_after_1st_over: oddsAfter1Over }),
    });
}
