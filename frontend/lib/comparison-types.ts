"use client";
type UnknownRecord = Record<string, unknown>;
function isRecord(v: unknown): v is UnknownRecord { return Boolean(v) && typeof v === "object" && !Array.isArray(v); }
function toRecord(v: unknown): UnknownRecord | null { return isRecord(v) ? v : null; }

/** @schema-exempt — frontend-only union type */
export type ComparisonSectionTone = "primary" | "secondary" | "tertiary" | "muted" | "default";
/** @schema-exempt — frontend-only union type */
export type ComparisonValueTone = "elite" | "strong" | "caution" | "danger" | "muted" | "default";

function isComparisonSectionTone(v: unknown): v is ComparisonSectionTone { return v === "primary" || v === "secondary" || v === "tertiary" || v === "muted" || v === "default"; }
function isComparisonValueTone(v: unknown): v is ComparisonValueTone { return v === "elite" || v === "strong" || v === "caution" || v === "danger" || v === "muted" || v === "default"; }

/** @schema-exempt — frontend-only rendering contract */
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
    if (record["row_kind"] === "section" || record["row_kind"] === "metric" || record["row_kind"] === "meta") row.row_kind = record["row_kind"];
    if (typeof record["section_label"] === "string") row.section_label = record["section_label"];
    if (isComparisonSectionTone(record["section_tone"])) row.section_tone = record["section_tone"];
    if (isComparisonValueTone(record["value_tone"])) row.value_tone = record["value_tone"];
    if (typeof record["is_zero_or_empty"] === "boolean") row.is_zero_or_empty = record["is_zero_or_empty"];
    if (typeof record["display_metric"] === "string") row.display_metric = record["display_metric"];
    return row;
}

export function toComparisonRows(rows: ReadonlyArray<Record<string, unknown>>): ComparisonRow[] { return rows.map((row) => toComparisonRow(row)); }

/** @schema-exempt — frontend-only union type */
export type ToneToken = "elite" | "strong" | "caution" | "danger" | "muted" | "default";
function isToneToken(v: unknown): v is ToneToken { return v === "elite" || v === "strong" || v === "caution" || v === "danger" || v === "muted" || v === "default"; }

function toBooleanRecord(v: unknown): Record<string, boolean> | undefined {
    const record = toRecord(v); if (!record) return undefined;
    const flags: Record<string, boolean> = {};
    for (const [key, entry] of Object.entries(record)) { if (typeof entry === "boolean") flags[key] = entry; }
    return Object.keys(flags).length > 0 ? flags : undefined;
}

function toToneRecord(v: unknown): Record<string, ToneToken> | undefined {
    const record = toRecord(v); if (!record) return undefined;
    const tones: Record<string, ToneToken> = {};
    for (const [key, entry] of Object.entries(record)) { if (isToneToken(entry)) tones[key] = entry; }
    return Object.keys(tones).length > 0 ? tones : undefined;
}

/** @schema-exempt — frontend-only rendering contract */
export interface MatrixRow extends Record<string, unknown> {
    cell_tones?: Record<string, ToneToken>;
    highlight_flags?: Record<string, boolean>;
}

function toMatrixRow(record: Record<string, unknown>): MatrixRow {
    const row: MatrixRow = { ...record };
    const cellTones = toToneRecord(record["cell_tones"]);
    const highlightFlags = toBooleanRecord(record["highlight_flags"]);
    if (cellTones) row.cell_tones = cellTones;
    if (highlightFlags) row.highlight_flags = highlightFlags;
    return row;
}

export function toMatrixRows(rows: ReadonlyArray<Record<string, unknown>>): MatrixRow[] { return rows.map((row) => toMatrixRow(row)); }

/** @schema-exempt — frontend-only rendering contract */
export interface DataRow extends Record<string, unknown> {
    cell_tones?: Record<string, ToneToken>;
}

export function toDataRows(rows: ReadonlyArray<Record<string, unknown>>): DataRow[] {
    return rows.map((record) => {
        const row: DataRow = { ...record };
        const cellTones = toToneRecord(record["cell_tones"]);
        if (cellTones) row.cell_tones = cellTones;
        return row;
    });
}

/** @schema-exempt — frontend-only union type */
export type ThreatRating = "BUNNY" | "DOMINATED" | "WATCHFUL" | "CONTESTED" | "ADVANTAGE" | "THREAT" | "DOMINANT" | "LOW DATA" | "NEW MATCHUP";

export const THREAT_STRIP_COLORS: Record<ThreatRating, string> = {
    "NEW MATCHUP": "var(--text-disabled)", "LOW DATA": "var(--text-disabled)",
    BUNNY: "var(--tier-danger)", DOMINATED: "var(--tier-danger)",
    WATCHFUL: "var(--tier-caution)", CONTESTED: "var(--bg-active)",
    ADVANTAGE: "var(--tier-strong)", THREAT: "var(--tier-caution)", DOMINANT: "var(--tier-elite)",
};

export const THREAT_BORDER_CLASSES: Record<ThreatRating, string> = {
    "NEW MATCHUP": "[border-left-color:var(--text-disabled)]", "LOW DATA": "[border-left-color:var(--text-disabled)]",
    BUNNY: "[border-left-color:var(--tier-danger)]", DOMINATED: "[border-left-color:var(--tier-danger)]",
    WATCHFUL: "[border-left-color:var(--tier-caution)]", CONTESTED: "[border-left-color:var(--bg-active)]",
    ADVANTAGE: "[border-left-color:var(--tier-strong)]", THREAT: "[border-left-color:var(--tier-caution)]", DOMINANT: "[border-left-color:var(--tier-elite)]",
};

export const THREAT_TEXT_CLASSES: Record<ThreatRating, string> = {
    "NEW MATCHUP": "[color:var(--text-disabled)]", "LOW DATA": "[color:var(--text-disabled)]",
    BUNNY: "[color:var(--tier-danger)]", DOMINATED: "[color:var(--tier-danger)]",
    WATCHFUL: "[color:var(--tier-caution)]", CONTESTED: "[color:var(--bg-active)]",
    ADVANTAGE: "[color:var(--tier-strong)]", THREAT: "[color:var(--tier-caution)]", DOMINANT: "[color:var(--tier-elite)]",
};

export const PILL_BG_CLASSES: Record<ThreatRating, string> = {
    "NEW MATCHUP": "[background:transparent]", "LOW DATA": "[background:transparent]",
    BUNNY: "[background:var(--tier-danger)]", DOMINATED: "[background:var(--tier-danger)]",
    WATCHFUL: "[background:var(--tier-caution)]", CONTESTED: "[background:var(--tier-caution)]",
    ADVANTAGE: "[background:var(--accent-primary)]", THREAT: "[background:var(--tier-caution)]", DOMINANT: "[background:var(--tier-elite)]",
};

export const PILL_TEXT_CLASSES: Record<ThreatRating, string> = {
    "NEW MATCHUP": "[color:var(--text-disabled)]", "LOW DATA": "[color:var(--text-disabled)]",
    BUNNY: "[color:white]", DOMINATED: "[color:var(--bg-deepest)]",
    WATCHFUL: "[color:var(--bg-deepest)]", CONTESTED: "[color:var(--bg-deepest)]",
    ADVANTAGE: "[color:white]", THREAT: "[color:var(--bg-deepest)]", DOMINANT: "[color:var(--bg-deepest)]",
};

export const PHASE_SEVERITY_ORDER: ThreatRating[] = ["BUNNY", "DOMINATED", "WATCHFUL", "CONTESTED", "THREAT", "ADVANTAGE", "DOMINANT", "NEW MATCHUP", "LOW DATA"];

/** @schema-exempt — frontend-only rendering contract */
export interface MatchupRow extends Record<string, unknown> {
    Bowler?: string; Style?: string; Balls?: number; Runs?: number; Outs?: number; Avg?: number; SR?: number;
    ThreatRating?: ThreatRating; Confidence?: number; MatchCount?: number; BoundaryBalls?: number; BoundaryRate?: number;
    DotBalls?: number; DotBallRate?: number; DismissalStructural?: number; DismissalCaught?: number; DismissalOther?: number;
    VenueFiltered?: boolean; Batter?: string;
    PP_Balls?: number; PP_Runs?: number; PP_Outs?: number; PP_Avg?: number; PP_SR?: number; PP_ThreatRating?: ThreatRating; PP_MatchCount?: number;
    Mid_Balls?: number; Mid_Runs?: number; Mid_Outs?: number; Mid_Avg?: number; Mid_SR?: number; Mid_ThreatRating?: ThreatRating; Mid_MatchCount?: number;
    Death_Balls?: number; Death_Runs?: number; Death_Outs?: number; Death_Avg?: number; Death_SR?: number; Death_ThreatRating?: ThreatRating; Death_MatchCount?: number;
    Inn1_Balls?: number; Inn1_Avg?: number; Inn1_SR?: number; Inn1_ThreatRating?: ThreatRating;
    Inn2_Balls?: number; Inn2_Avg?: number; Inn2_SR?: number; Inn2_ThreatRating?: ThreatRating;
    highlight_flags?: Record<string, boolean>; cell_tones?: Record<string, ToneToken>;
}

export function toMatchupRows(rows: ReadonlyArray<Record<string, unknown>>): MatchupRow[] {
    return rows.map((record) => {
        const row: MatchupRow = { ...record } as MatchupRow;
        const highlightFlags = toBooleanRecord(record["highlight_flags"]);
        const cellTones = toToneRecord(record["cell_tones"]);
        if (highlightFlags) row.highlight_flags = highlightFlags;
        if (cellTones) row.cell_tones = cellTones;
        return row;
    });
}

export function worstThreatFromRow(row: MatchupRow): ThreatRating {
    const values = [row.PP_ThreatRating, row.Mid_ThreatRating, row.Death_ThreatRating].filter((v): v is ThreatRating => !!v);
    if (values.length === 0) return row.ThreatRating ?? "LOW DATA";
    let worst = values[0];
    for (const current of values) {
        const wi = PHASE_SEVERITY_ORDER.indexOf(worst), ci = PHASE_SEVERITY_ORDER.indexOf(current);
        if (ci !== -1 && (wi === -1 || ci < wi)) worst = current;
    }
    return worst;
}

/** @schema-exempt — frontend-only union type */
export type TeamTone = "blue" | "emerald" | "amber" | "rose" | "violet" | "slate";
export function isTeamTone(v: unknown): v is TeamTone { return v === "blue" || v === "emerald" || v === "amber" || v === "rose" || v === "violet" || v === "slate"; }
export function getTeamTone(v: unknown): TeamTone { return isTeamTone(v) ? v : "slate"; }
