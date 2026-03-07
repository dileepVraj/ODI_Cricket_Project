"use client";

type UnknownRecord = Record<string, unknown>;

function isRecord(value: unknown): value is UnknownRecord {
    return Boolean(value) && typeof value === "object" && !Array.isArray(value);
}

/** @schema runtime-guard:event-target-node */
export function isNodeTarget(value: EventTarget | null): value is Node {
    return value instanceof Node;
}

/** @schema runtime-guard:event-target-html-element */
export function isHTMLElementTarget(value: EventTarget | null): value is HTMLElement {
    return value instanceof HTMLElement;
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

/** @schema {unknown} - TODO: confirm backend schema */
export interface PercentBreakdown extends Record<string, unknown> {
    bat_first?: unknown;
    chase?: unknown;
    tie_nr?: unknown;
}

export function getPercentBreakdown(value: unknown): PercentBreakdown {
    const record = toRecord(value);
    if (!record) {
        return {};
    }
    return { ...record };
}

/** @schema {unknown} - TODO: confirm backend schema */
export type ComparisonSectionTone = "primary" | "secondary" | "tertiary" | "muted" | "default";

/** @schema {unknown} - TODO: confirm backend schema */
export type ComparisonValueTone = "elite" | "strong" | "caution" | "danger" | "muted" | "default";

function isComparisonSectionTone(value: unknown): value is ComparisonSectionTone {
    return value === "primary" ||
        value === "secondary" ||
        value === "tertiary" ||
        value === "muted" ||
        value === "default";
}

function isComparisonValueTone(value: unknown): value is ComparisonValueTone {
    return value === "elite" ||
        value === "strong" ||
        value === "caution" ||
        value === "danger" ||
        value === "muted" ||
        value === "default";
}

/** @schema {unknown} - TODO: confirm backend schema */
export interface ComparisonRow extends Record<string, unknown> {
    row_kind?: "section" | "metric" | "meta";
    section_label?: string;
    section_tone?: ComparisonSectionTone;
    value_tone?: ComparisonValueTone;
    is_zero_or_empty?: boolean;
    display_metric?: string;
}

function toComparisonRow(record: Record<string, unknown>): ComparisonRow {
    const row: ComparisonRow = { ...record };

    if (record["row_kind"] === "section" || record["row_kind"] === "metric" || record["row_kind"] === "meta") {
        row.row_kind = record["row_kind"];
    }
    if (typeof record["section_label"] === "string") {
        row.section_label = record["section_label"];
    }
    if (isComparisonSectionTone(record["section_tone"])) {
        row.section_tone = record["section_tone"];
    }
    if (isComparisonValueTone(record["value_tone"])) {
        row.value_tone = record["value_tone"];
    }
    if (typeof record["is_zero_or_empty"] === "boolean") {
        row.is_zero_or_empty = record["is_zero_or_empty"];
    }
    if (typeof record["display_metric"] === "string") {
        row.display_metric = record["display_metric"];
    }

    return row;
}

export function toComparisonRows(rows: ReadonlyArray<Record<string, unknown>>): ComparisonRow[] {
    return rows.map((row) => toComparisonRow(row));
}

/** @schema {unknown} - TODO: confirm backend schema */
export type ToneToken = "elite" | "strong" | "caution" | "danger" | "muted" | "default";

function isToneToken(value: unknown): value is ToneToken {
    return value === "elite" ||
        value === "strong" ||
        value === "caution" ||
        value === "danger" ||
        value === "muted" ||
        value === "default";
}

function toToneRecord(value: unknown): Record<string, ToneToken> | undefined {
    const record = toRecord(value);
    if (!record) {
        return undefined;
    }

    const tones: Record<string, ToneToken> = {};
    for (const [key, entry] of Object.entries(record)) {
        if (isToneToken(entry)) {
            tones[key] = entry;
        }
    }

    return Object.keys(tones).length > 0 ? tones : undefined;
}

/** @schema {unknown} - TODO: confirm backend schema */
export interface MatrixRow extends Record<string, unknown> {
    cell_tones?: Record<string, ToneToken>;
    highlight_flags?: Record<string, boolean>;
}

function toMatrixRow(record: Record<string, unknown>): MatrixRow {
    const row: MatrixRow = { ...record };
    const cellTones = toToneRecord(record["cell_tones"]);
    const highlightFlags = toBooleanRecord(record["highlight_flags"]);

    if (cellTones) {
        row.cell_tones = cellTones;
    }
    if (highlightFlags) {
        row.highlight_flags = highlightFlags;
    }

    return row;
}

export function toMatrixRows(rows: ReadonlyArray<Record<string, unknown>>): MatrixRow[] {
    return rows.map((row) => toMatrixRow(row));
}

/** @schema {unknown} - TODO: confirm backend schema */
export interface FormSummary {
    wins?: number;
    losses?: number;
    ties_or_nr?: number;
    total?: number;
}

function toFormSummary(value: unknown): FormSummary | undefined {
    const record = toRecord(value);
    if (!record) {
        return undefined;
    }

    const summary: FormSummary = {};
    if (typeof record["wins"] === "number") {
        summary.wins = record["wins"];
    }
    if (typeof record["losses"] === "number") {
        summary.losses = record["losses"];
    }
    if (typeof record["ties_or_nr"] === "number") {
        summary.ties_or_nr = record["ties_or_nr"];
    }
    if (typeof record["total"] === "number") {
        summary.total = record["total"];
    }

    return Object.keys(summary).length > 0 ? summary : undefined;
}

/** @schema {unknown} - TODO: confirm backend schema */
export interface FormRow extends Record<string, unknown> {
    ResultTone?: string;
    ResultSymbol?: string;
    form_summary?: FormSummary;
}

export function toFormRows(rows: ReadonlyArray<Record<string, unknown>>): FormRow[] {
    return rows.map((record) => {
        const row: FormRow = { ...record };
        const summary = toFormSummary(record["form_summary"]);

        if (typeof record["ResultTone"] === "string") {
            row.ResultTone = record["ResultTone"];
        }
        if (typeof record["ResultSymbol"] === "string") {
            row.ResultSymbol = record["ResultSymbol"];
        }
        if (summary) {
            row.form_summary = summary;
        }

        return row;
    });
}

/** @schema {unknown} - TODO: confirm backend schema */
export interface DataRow extends Record<string, unknown> {
    cell_tones?: Record<string, ToneToken>;
}

export function toDataRows(rows: ReadonlyArray<Record<string, unknown>>): DataRow[] {
    return rows.map((record) => {
        const row: DataRow = { ...record };
        const cellTones = toToneRecord(record["cell_tones"]);
        if (cellTones) {
            row.cell_tones = cellTones;
        }
        return row;
    });
}

/** @schema {unknown} - TODO: confirm backend schema */
export interface MatchupRow extends Record<string, unknown> {
    highlight_flags?: Record<string, boolean>;
    cell_tones?: Record<string, ToneToken>;
}

export function toMatchupRows(rows: ReadonlyArray<Record<string, unknown>>): MatchupRow[] {
    return rows.map((record) => {
        const row: MatchupRow = { ...record };
        const highlightFlags = toBooleanRecord(record["highlight_flags"]);
        const cellTones = toToneRecord(record["cell_tones"]);

        if (highlightFlags) {
            row.highlight_flags = highlightFlags;
        }
        if (cellTones) {
            row.cell_tones = cellTones;
        }

        return row;
    });
}

/** @schema {unknown} - TODO: confirm backend schema */
export interface VenueTeamBattingStats {
    avg: string;
    high: string;
    low: string;
    avg_win: string;
    low_def: string;
}

/** @schema {unknown} - TODO: confirm backend schema */
export interface VenueTeamChaseStats {
    avg: string;
    high: string;
    succ: string;
    fail: string;
}

/** @schema {unknown} - TODO: confirm backend schema */
export interface VenueTeamStats {
    wins: number;
    defended: number;
    chased: number;
    bat1: VenueTeamBattingStats;
    chase: VenueTeamChaseStats;
    team_color: string;
    team_tone?: TeamTone;
}

/** @schema {unknown} - TODO: confirm backend schema */
export interface VenueMatchupSummary {
    matches: number;
    win_pct: number;
    tie_nr: number;
    last_5_home?: string;
    last_5_away?: string;
}

/** @schema {unknown} - TODO: confirm backend schema */
export interface VenueMatchupTeam {
    name: string;
    stats: VenueTeamStats;
}

/** @schema {unknown} - TODO: confirm backend schema */
export interface VenueMatchupAverages {
    avg_1st: string;
    avg_2nd: string;
    avg_win_score: string;
}

/** @schema {unknown} - TODO: confirm backend schema */
export interface VenueMatchupData {
    summary: VenueMatchupSummary;
    team_a: VenueMatchupTeam;
    team_b: VenueMatchupTeam;
    venue_avg: VenueMatchupAverages;
    low_sample_warnings?: string[];
    highlight_flags?: Record<string, boolean>;
    derived_badges?: string[];
}

function readString(record: Record<string, unknown>, key: string): string {
    return typeof record[key] === "string" ? record[key] : "";
}

function readNumber(record: Record<string, unknown>, key: string): number {
    return typeof record[key] === "number" ? record[key] : 0;
}

function toVenueTeamBattingStats(value: unknown): VenueTeamBattingStats {
    const record = toRecord(value);
    if (!record) {
        return { avg: "", high: "", low: "", avg_win: "", low_def: "" };
    }

    return {
        avg: readString(record, "avg"),
        high: readString(record, "high"),
        low: readString(record, "low"),
        avg_win: readString(record, "avg_win"),
        low_def: readString(record, "low_def"),
    };
}

function toVenueTeamChaseStats(value: unknown): VenueTeamChaseStats {
    const record = toRecord(value);
    if (!record) {
        return { avg: "", high: "", succ: "", fail: "" };
    }

    return {
        avg: readString(record, "avg"),
        high: readString(record, "high"),
        succ: readString(record, "succ"),
        fail: readString(record, "fail"),
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

function toVenueMatchupTeam(value: unknown): VenueMatchupTeam | null {
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

function toVenueMatchupSummary(value: unknown): VenueMatchupSummary {
    const record = toRecord(value);
    if (!record) {
        return { matches: 0, win_pct: 0, tie_nr: 0 };
    }

    const summary: VenueMatchupSummary = {
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

function toVenueMatchupAverages(value: unknown): VenueMatchupAverages | null {
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

export function getVenueMatchupData(value: unknown): VenueMatchupData | null {
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

    const data: VenueMatchupData = {
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

/** @schema {unknown} - TODO: confirm backend schema */
export type TeamTone = "blue" | "emerald" | "amber" | "rose" | "violet" | "slate";

function isTeamTone(value: unknown): value is TeamTone {
    return value === "blue" ||
        value === "emerald" ||
        value === "amber" ||
        value === "rose" ||
        value === "violet" ||
        value === "slate";
}

export function getTeamTone(value: unknown): TeamTone {
    return isTeamTone(value) ? value : "slate";
}

/** @schema {unknown} - TODO: confirm backend schema */
export interface PredictionGauge extends Record<string, unknown> {
    par_marker_pct?: unknown;
    range_left_pct?: unknown;
    range_width_pct?: unknown;
    predicted_pct?: unknown;
    min_score?: unknown;
    max_score?: unknown;
}

export function getPredictionGauge(value: unknown): PredictionGauge {
    const record = toRecord(value);
    if (!record) {
        return {};
    }
    return { ...record };
}

export function getPredictionNotes(value: unknown): string[] {
    return toStringArray(value);
}

/** @schema {unknown} - TODO: confirm backend schema */
export interface PlayerPayloadFragment extends Record<string, unknown> {}

export function toPlayerPayloadFragment(value: unknown): PlayerPayloadFragment | null {
    const record = toRecord(value);
    if (!record) {
        return null;
    }
    return { ...record };
}

/** @schema {unknown} - TODO: confirm backend schema */
export type MatchAuditStatusTone = "elite" | "caution" | "danger" | "muted";

function isMatchAuditStatusTone(value: unknown): value is MatchAuditStatusTone {
    return value === "elite" ||
        value === "caution" ||
        value === "danger" ||
        value === "muted";
}

/** @schema {unknown} - TODO: confirm backend schema */
export interface MatchAuditRow extends Record<string, unknown> {
    status_tone?: MatchAuditStatusTone;
}

export function toMatchAuditRow(record: Record<string, unknown>): MatchAuditRow {
    const row: MatchAuditRow = { ...record };
    if (isMatchAuditStatusTone(record["status_tone"])) {
        row.status_tone = record["status_tone"];
    }
    return row;
}
