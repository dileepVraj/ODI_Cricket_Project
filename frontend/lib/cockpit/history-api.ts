import { requestJson } from "@/lib/api";
import type { HistoryLeague } from "@/lib/cockpit/history-filters";
import type { HomeGround } from "@/components/cockpit/cockpit-types";

/** @schema HistoryTradeResponse in cockpit/schemas.py */
export interface HistoryTradeResponse {
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
    trade_sentiment: "saved" | "satisfied" | "lost" | "achieved" | null;
    fav_sub_30_loss: boolean;
    missed_swing_team: string | null;
    missed_swing_back_odds: number | null;
    missed_swing_lay_odds: number | null;
    missed_swing_bet_index: number | null;
    missed_swing_cumulative_stake: number | null;
    missed_swing_net_pnl: number | null;
    targeted_pnl: number | null;
    achieved_yield_percentage: number | null;
    trade_mistakes: string | null;
    total_volume_wagered: number;
    created_at: string;
    updated_at: string;
    format_key: string;
    format_label: string;
}

/** @schema HistorySummaryResponse in cockpit/schemas.py */
export interface HistorySummaryResponse {
    format_scope: "single" | "all";
    format_key: string | null;
    format_keys: string[];
    trade_count: number;
    settled_trade_count: number;
    total_realized_pnl: number;
    total_volume_wagered: number;
    positive_trades: number;
    negative_trades: number;
    gross_profit: number;
    gross_loss: number;
    profit_factor: number | null;
    profit_factor_tier: "elite" | "caution" | "danger";
    hit_rate: number | null;
    avg_win: number | null;
    avg_loss: number | null;
    earliest_match_date: string | null;
    latest_match_date: string | null;
}

/** @schema none -- frontend-only filter state */
export interface HistoryTradeFilters {
    league: HistoryLeague;
    year?: number;
    dateRange: string;
    dateFrom?: string;
    dateTo?: string;
}

function cockpitFetch<T>(path: string, init?: RequestInit): Promise<T> {
    return requestJson<T>(`/api/cockpit${path}`, init);
}

export function buildHistoryQueryString(filters: HistoryTradeFilters): string {
    const params = new URLSearchParams();

    if (filters.league === "all") {
        params.set("format_scope", "all");
    } else {
        params.set("format_scope", "single");
        params.set("format", filters.league);
    }

    if (filters.year !== undefined) {
        params.set("season", String(filters.year));
    }

    params.set("date_range", filters.dateRange);
    if (filters.dateRange === "custom") {
        if (filters.dateFrom) {
            params.set("date_from", filters.dateFrom);
        }
        if (filters.dateTo) {
            params.set("date_to", filters.dateTo);
        }
    }

    params.set("status", "SETTLED,VOID");

    const query = params.toString();
    return query ? `?${query}` : "";
}

export async function getHistoryTrades(filters: HistoryTradeFilters): Promise<HistoryTradeResponse[]> {
    return cockpitFetch<HistoryTradeResponse[]>(`/history/trades${buildHistoryQueryString(filters)}`);
}

export async function getHistorySummary(filters: HistoryTradeFilters): Promise<HistorySummaryResponse> {
    return cockpitFetch<HistorySummaryResponse>(`/history/summary${buildHistoryQueryString(filters)}`);
}
