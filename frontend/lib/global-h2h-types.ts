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

export function readStringOrNumber(value: unknown): string {
    if (value === null || value === undefined || value === "") {
        return "-";
    }
    if (typeof value === "string" || typeof value === "number") {
        return String(value);
    }
    return "-";
}

function readNumber(record: Record<string, unknown>, key: string): number {
    return typeof record[key] === "number" ? record[key] : 0;
}

function readStringNumberOrFallback(
    record: Record<string, unknown>,
    key: string
): string | number {
    const value = record[key];
    if (typeof value === "string" || typeof value === "number") {
        return value;
    }
    return "-";
}

function toBooleanRecord(value: unknown): Record<string, boolean> {
    const record = toRecord(value);
    if (!record) {
        return {};
    }

    const flags: Record<string, boolean> = {};
    for (const [key, entry] of Object.entries(record)) {
        if (typeof entry === "boolean") {
            flags[key] = entry;
        }
    }

    return flags;
}

/** @schema-exempt — frontend-only rendering contract, no Pydantic equivalent */
export interface GlobalH2HBattingStats {
    avg: string;
    high: string;
    low: string;
    avg_win: string;
    low_def: string;
}

/** @schema-exempt — frontend-only rendering contract, no Pydantic equivalent */
export interface GlobalH2HChaseStats {
    avg: string;
    high: string;
    succ: string;
    fail: string;
}

/** @schema-exempt — frontend-only rendering contract, no Pydantic equivalent */
export interface GlobalH2HStatsBlock {
    wins: number;
    defended: number;
    chased: number;
    bat1: GlobalH2HBattingStats;
    chase: GlobalH2HChaseStats;
    team_color: string;
    team_tone: TeamTone;
    low_sample_warnings: string[];
    highlight_flags: Record<string, boolean>;
    derived_badges: string[];
}

/** @schema-exempt — frontend-only rendering contract, no Pydantic equivalent */
export interface GlobalH2HTeam {
    name: string;
    stats: GlobalH2HStatsBlock;
}

/** @schema-exempt — frontend-only rendering contract, no Pydantic equivalent */
export interface GlobalH2HSummary {
    matches: number;
    win_pct: string | number;
    tie_nr: number;
    last_5_home: string;
    last_5_away: string;
}

/** @schema-exempt — frontend-only rendering contract, no Pydantic equivalent */
export interface GlobalH2HVenueAvg {
    avg_1st: string;
    avg_2nd: string;
    avg_win_score: string;
}

/** @schema-exempt — frontend-only rendering contract, no Pydantic equivalent */
export interface GlobalH2HData {
    summary: GlobalH2HSummary;
    team_a: GlobalH2HTeam;
    team_b: GlobalH2HTeam;
    venue_avg: GlobalH2HVenueAvg;
    low_sample_warnings: string[];
    highlight_flags: Record<string, boolean>;
    derived_badges: string[];
}

function toGlobalH2HBattingStats(value: unknown): GlobalH2HBattingStats | null {
    const record = toRecord(value);
    if (!record) {
        return null;
    }

    return {
        avg: readStringOrNumber(record["avg"]),
        high: readStringOrNumber(record["high"]),
        low: readStringOrNumber(record["low"]),
        avg_win: readStringOrNumber(record["avg_win"]),
        low_def: readStringOrNumber(record["low_def"]),
    };
}

function toGlobalH2HChaseStats(value: unknown): GlobalH2HChaseStats | null {
    const record = toRecord(value);
    if (!record) {
        return null;
    }

    return {
        avg: readStringOrNumber(record["avg"]),
        high: readStringOrNumber(record["high"]),
        succ: readStringOrNumber(record["succ"]),
        fail: readStringOrNumber(record["fail"]),
    };
}

function toGlobalH2HStatsBlock(value: unknown): GlobalH2HStatsBlock | null {
    const record = toRecord(value);
    if (!record) {
        return null;
    }

    const bat1 = toGlobalH2HBattingStats(record["bat1"]);
    const chase = toGlobalH2HChaseStats(record["chase"]);
    if (!bat1 || !chase) {
        return null;
    }

    return {
        wins: readNumber(record, "wins"),
        defended: readNumber(record, "defended"),
        chased: readNumber(record, "chased"),
        bat1,
        chase,
        team_color: readString(record, "team_color"),
        team_tone: isTeamTone(record["team_tone"]) ? record["team_tone"] : "slate",
        low_sample_warnings: toStringArray(record["low_sample_warnings"]),
        highlight_flags: toBooleanRecord(record["highlight_flags"]),
        derived_badges: toStringArray(record["derived_badges"]),
    };
}

function toGlobalH2HTeam(value: unknown): GlobalH2HTeam | null {
    const record = toRecord(value);
    if (!record) {
        return null;
    }

    const stats = toGlobalH2HStatsBlock(record["stats"]);
    if (!stats) {
        return null;
    }

    return {
        name: readString(record, "name"),
        stats,
    };
}

function toGlobalH2HSummary(value: unknown): GlobalH2HSummary | null {
    const record = toRecord(value);
    if (!record) {
        return null;
    }

    return {
        matches: readNumber(record, "matches"),
        win_pct: readStringNumberOrFallback(record, "win_pct"),
        tie_nr: readNumber(record, "tie_nr"),
        last_5_home: readStringOrNumber(record["last_5_home"]),
        last_5_away: readStringOrNumber(record["last_5_away"]),
    };
}

function toGlobalH2HVenueAvg(value: unknown): GlobalH2HVenueAvg | null {
    const record = toRecord(value);
    if (!record) {
        return null;
    }

    return {
        avg_1st: readStringOrNumber(record["avg_1st"]),
        avg_2nd: readStringOrNumber(record["avg_2nd"]),
        avg_win_score: readStringOrNumber(record["avg_win_score"]),
    };
}

export function getGlobalH2HData(data: Record<string, unknown>): GlobalH2HData | null {
    try {
        const record = toRecord(data);
        if (!record) {
            return null;
        }

        if (!("summary" in record) || !("team_a" in record) || !("team_b" in record) || !("venue_avg" in record)) {
            return null;
        }

        const summary = toGlobalH2HSummary(record["summary"]);
        const teamA = toGlobalH2HTeam(record["team_a"]);
        const teamB = toGlobalH2HTeam(record["team_b"]);
        const venueAvg = toGlobalH2HVenueAvg(record["venue_avg"]);

        if (!summary || !teamA || !teamB || !venueAvg) {
            return null;
        }

        return {
            summary,
            team_a: teamA,
            team_b: teamB,
            venue_avg: venueAvg,
            low_sample_warnings: toStringArray(record["low_sample_warnings"]),
            highlight_flags: toBooleanRecord(record["highlight_flags"]),
            derived_badges: toStringArray(record["derived_badges"]),
        };
    } catch {
        return null;
    }
}
