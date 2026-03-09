"use client";

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


/** @schema-exempt — frontend-only union type, no Pydantic equivalent */
export type ComparisonSectionTone = "primary" | "secondary" | "tertiary" | "muted" | "default";

/** @schema-exempt — frontend-only union type, no Pydantic equivalent */
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

/** @schema-exempt — frontend-only rendering contract, no Pydantic equivalent */
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

/** @schema-exempt — frontend-only union type, no Pydantic equivalent */
export type ToneToken = "elite" | "strong" | "caution" | "danger" | "muted" | "default";

function isToneToken(value: unknown): value is ToneToken {
    return value === "elite" ||
        value === "strong" ||
        value === "caution" ||
        value === "danger" ||
        value === "muted" ||
        value === "default";
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

/** @schema-exempt — frontend-only rendering contract, no Pydantic equivalent */
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

/** @schema-exempt — frontend-only rendering contract, no Pydantic equivalent */
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

/** @schema-exempt — frontend-only rendering contract, no Pydantic equivalent */
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

/** @schema-exempt — frontend-only union type, no Pydantic equivalent */
export type TeamTone = "blue" | "emerald" | "amber" | "rose" | "violet" | "slate";

export function isTeamTone(value: unknown): value is TeamTone {
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
