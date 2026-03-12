"use client";

import { TeamTone, isTeamTone } from "@/lib/comparison-types";

export type { TeamTone };

type UnknownRecord = Record<string, unknown>;

function isRecord(value: unknown): value is UnknownRecord {
    return Boolean(value) && typeof value === "object" && !Array.isArray(value);
}

function toRecord(value: unknown): UnknownRecord | null {
    if (!isRecord(value)) {
        return null;
    }
    return value;
}

function toStringArray(value: unknown): string[] {
    if (!Array.isArray(value)) {
        return [];
    }
    return value.filter((entry): entry is string => typeof entry === "string");
}

function readString(record: Record<string, unknown>, key: string): string {
    return typeof record[key] === "string" ? record[key] : "";
}

function readStringOrNumber(record: Record<string, unknown>, key: string): string {
    const value = record[key];
    if (typeof value === "string" || typeof value === "number") {
        return String(value);
    }
    return "";
}

function readNumber(record: Record<string, unknown>, key: string): number {
    return typeof record[key] === "number" ? record[key] : 0;
}

function toBooleanRecord(value: unknown): Record<string, boolean> | undefined {
    const record = toRecord(value);
    if (!record) {
        return undefined;
    }

    const flags: Record<string, boolean> = {};
    for (const [key, entry] of Object.entries(record)) {
        if (typeof entry === "boolean") {
            flags[key] = entry;
        }
    }

    return Object.keys(flags).length > 0 ? flags : undefined;
}

/** @schema-exempt — frontend-only rendering contract, no Pydantic equivalent */
export interface VenueTeamBattingStats {
    avg: string;
    high: string;
    low: string;
    avg_win: string;
    low_def: string;
}

/** @schema-exempt — frontend-only rendering contract, no Pydantic equivalent */
export interface VenueTeamChaseStats {
    avg: string;
    high: string;
    succ: string;
    fail: string;
}

/** @schema-exempt — frontend-only rendering contract, no Pydantic equivalent */
export interface VenueTeamStats {
    wins: number;
    defended: number;
    chased: number;
    bat1: VenueTeamBattingStats;
    chase: VenueTeamChaseStats;
    team_color: string;
    team_tone?: TeamTone;
}

/** @schema-exempt — frontend-only rendering contract, no Pydantic equivalent */
export interface CountryH2HSummary {
    matches: number;
    win_pct: number;
    tie_nr: number;
    last_5_home?: string;
    last_5_away?: string;
}

/** @schema-exempt — frontend-only rendering contract, no Pydantic equivalent */
export interface CountryH2HTeam {
    name: string;
    stats: VenueTeamStats;
}

/** @schema-exempt — frontend-only rendering contract, no Pydantic equivalent */
export interface CountryH2HAverages {
    avg_1st: string;
    avg_2nd: string;
    avg_win_score: string;
}

/** @schema {VenueMatchupReport} in core/interfaces/team_types.py */
export interface CountryH2HData {
    summary: CountryH2HSummary;
    team_a: CountryH2HTeam;
    team_b: CountryH2HTeam;
    venue_avg: CountryH2HAverages;
    low_sample_warnings?: string[];
    highlight_flags?: Record<string, boolean>;
    derived_badges?: string[];
}

function toVenueTeamBattingStats(value: unknown): VenueTeamBattingStats {
    const record = toRecord(value);
    if (!record) {
        return { avg: "", high: "", low: "", avg_win: "", low_def: "" };
    }

    return {
        avg: readStringOrNumber(record, "avg"),
        high: readStringOrNumber(record, "high"),
        low: readStringOrNumber(record, "low"),
        avg_win: readStringOrNumber(record, "avg_win"),
        low_def: readStringOrNumber(record, "low_def"),
    };
}

function toVenueTeamChaseStats(value: unknown): VenueTeamChaseStats {
    const record = toRecord(value);
    if (!record) {
        return { avg: "", high: "", succ: "", fail: "" };
    }

    return {
        avg: readStringOrNumber(record, "avg"),
        high: readStringOrNumber(record, "high"),
        succ: readStringOrNumber(record, "succ"),
        fail: readStringOrNumber(record, "fail"),
    };
}

function toVenueTeamStats(value: unknown): VenueTeamStats | null {
    const record = toRecord(value);
    if (!record) {
        return null;
    }

    const stats: VenueTeamStats = {
        wins: readNumber(record, "wins"),
        defended: readNumber(record, "defended"),
        chased: readNumber(record, "chased"),
        bat1: toVenueTeamBattingStats(record["bat1"]),
        chase: toVenueTeamChaseStats(record["chase"]),
        team_color: readString(record, "team_color"),
    };

    if (isTeamTone(record["team_tone"])) {
        stats.team_tone = record["team_tone"];
    }

    return stats;
}

function toVenueMatchupTeam(value: unknown): CountryH2HTeam | null {
    const record = toRecord(value);
    if (!record) {
        return null;
    }

    const stats = toVenueTeamStats(record["stats"]);
    if (!stats) {
        return null;
    }

    return {
        name: readString(record, "name"),
        stats,
    };
}

function toVenueMatchupSummary(value: unknown): CountryH2HSummary {
    const record = toRecord(value);
    if (!record) {
        return { matches: 0, win_pct: 0, tie_nr: 0 };
    }

    const summary: CountryH2HSummary = {
        matches: readNumber(record, "matches"),
        win_pct: readNumber(record, "win_pct"),
        tie_nr: readNumber(record, "tie_nr"),
    };

    if (typeof record["last_5_home"] === "string") {
        summary.last_5_home = record["last_5_home"];
    }
    if (typeof record["last_5_away"] === "string") {
        summary.last_5_away = record["last_5_away"];
    }

    return summary;
}

function toVenueMatchupAverages(value: unknown): CountryH2HAverages | null {
    const record = toRecord(value);
    if (!record) {
        return null;
    }

    return {
        avg_1st: readString(record, "avg_1st"),
        avg_2nd: readString(record, "avg_2nd"),
        avg_win_score: readString(record, "avg_win_score"),
    };
}

export function getCountryH2HData(value: unknown): CountryH2HData | null {
    // getCountryH2HData intentionally mirrors getVenueMatchupData.
    const record = toRecord(value);
    if (!record) {
        return null;
    }

    const teamA = toVenueMatchupTeam(record["team_a"]);
    const teamB = toVenueMatchupTeam(record["team_b"]);
    const venueAvg = toVenueMatchupAverages(record["venue_avg"]);

    if (!teamA || !teamB || !venueAvg) {
        return null;
    }

    const data: CountryH2HData = {
        summary: toVenueMatchupSummary(record["summary"]),
        team_a: teamA,
        team_b: teamB,
        venue_avg: venueAvg,
    };

    const lowSampleWarnings = toStringArray(record["low_sample_warnings"]);
    const highlightFlags = toBooleanRecord(record["highlight_flags"]);
    const derivedBadges = toStringArray(record["derived_badges"]);

    if (lowSampleWarnings.length > 0) {
        data.low_sample_warnings = lowSampleWarnings;
    }
    if (highlightFlags) {
        data.highlight_flags = highlightFlags;
    }
    if (derivedBadges.length > 0) {
        data.derived_badges = derivedBadges;
    }

    return data;
}
