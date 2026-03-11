"use client";

import { type TeamTone, isTeamTone } from "@/lib/comparison-types";

export type { TeamTone };

export type UnknownRecord = Record<string, unknown>;

function isRecord(value: unknown): value is UnknownRecord {
    return Boolean(value) && typeof value === "object" && !Array.isArray(value);
}

export function toRecord(value: unknown): UnknownRecord | null {
    if (!isRecord(value)) {
        return null;
    }

    return value;
}

export function toStringArray(value: unknown): string[] {
    if (!Array.isArray(value)) {
        return [];
    }

    return value.filter((entry): entry is string => typeof entry === "string");
}

export function toStringMap(value: unknown): Record<string, string> {
    const record = toRecord(value);
    if (!record) {
        return {};
    }

    const map: Record<string, string> = {};
    for (const [key, entry] of Object.entries(record)) {
        if (key && typeof entry === "string") {
            map[key] = entry;
        }
    }

    return map;
}

export function readNumber(record: UnknownRecord | null, key: string): number {
    return record && typeof record[key] === "number" ? record[key] : 0;
}

export function readString(record: UnknownRecord | null, key: string): string {
    return record && typeof record[key] === "string" ? record[key] : "";
}

export function toDisplayValue(value: unknown): string {
    if (typeof value === "string" || typeof value === "number") {
        return String(value);
    }

    return "-";
}

/** @schema-exempt - frontend-only rendering contract, no Pydantic equivalent */
export interface FortressBattingStats {
    avg: string;
    high: string;
    low: string;
    avg_win: string;
    low_def: string;
}

/** @schema-exempt - frontend-only rendering contract, no Pydantic equivalent */
export interface FortressChaseStats {
    avg: string;
    high: string;
    succ: string;
    fail: string;
}

/** @schema-exempt - frontend-only rendering contract, no Pydantic equivalent */
export interface FortressTeamStats {
    wins: number;
    defended: number;
    chased: number;
    bat1: FortressBattingStats;
    chase: FortressChaseStats;
    team_color: string;
    team_tone?: TeamTone;
}

/** @schema-exempt - frontend-only rendering contract, no Pydantic equivalent */
export interface FortressTeam {
    name: string;
    stats: FortressTeamStats;
}

/** @schema-exempt - frontend-only rendering contract, no Pydantic equivalent */
export interface FortressData {
    summary: {
        matches: number;
        home_win_pct: number;
        tie_nr: number;
    };
    home: FortressTeam;
    visitor: FortressTeam;
    venue_avg: {
        avg_1st: string;
        avg_2nd: string;
        avg_win_score: string;
    };
    team_colors: Record<string, string>;
    low_sample_warnings?: string[];
}

export function toTeamStats(value: unknown): FortressTeamStats | null {
    const record = toRecord(value);
    if (!record) {
        return null;
    }

    const stats: FortressTeamStats = {
        wins: readNumber(record, "wins"),
        defended: readNumber(record, "defended"),
        chased: readNumber(record, "chased"),
        bat1: {
            avg: toDisplayValue(toRecord(record["bat1"])?.["avg"]),
            high: toDisplayValue(toRecord(record["bat1"])?.["high"]),
            low: toDisplayValue(toRecord(record["bat1"])?.["low"]),
            avg_win: toDisplayValue(toRecord(record["bat1"])?.["avg_win"]),
            low_def: toDisplayValue(toRecord(record["bat1"])?.["low_def"]),
        },
        chase: {
            avg: toDisplayValue(toRecord(record["chase"])?.["avg"]),
            high: toDisplayValue(toRecord(record["chase"])?.["high"]),
            succ: toDisplayValue(toRecord(record["chase"])?.["succ"]),
            fail: toDisplayValue(toRecord(record["chase"])?.["fail"]),
        },
        team_color: readString(record, "team_color"),
    };

    if (isTeamTone(record["team_tone"])) {
        stats.team_tone = record["team_tone"];
    }

    return stats;
}

export function toTeam(value: unknown): FortressTeam | null {
    const record = toRecord(value);
    if (!record) {
        return null;
    }

    const stats = toTeamStats(record["stats"]);
    if (!stats) {
        return null;
    }

    return {
        name: readString(record, "name"),
        stats,
    };
}

export function getHomeFortressData(value: unknown): FortressData | null {
    const record = toRecord(value);
    if (!record) {
        return null;
    }

    const home = toTeam(record["home"]);
    const visitor = toTeam(record["visitor"]);
    const venueAvg = toRecord(record["venue_avg"]);

    if (!home || !visitor || !venueAvg) {
        return null;
    }

    const data: FortressData = {
        summary: {
            matches: readNumber(toRecord(record["summary"]), "matches"),
            home_win_pct: readNumber(toRecord(record["summary"]), "home_win_pct"),
            tie_nr: readNumber(toRecord(record["summary"]), "tie_nr"),
        },
        home,
        visitor,
        venue_avg: {
            avg_1st: toDisplayValue(venueAvg["avg_1st"]),
            avg_2nd: toDisplayValue(venueAvg["avg_2nd"]),
            avg_win_score: toDisplayValue(venueAvg["avg_win_score"]),
        },
        team_colors: toStringMap(record["team_colors"]),
    };

    const lowSampleWarnings = toStringArray(record["low_sample_warnings"]);
    if (lowSampleWarnings.length > 0) {
        data.low_sample_warnings = lowSampleWarnings;
    }

    return data;
}
