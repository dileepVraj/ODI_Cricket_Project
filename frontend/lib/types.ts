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

function toStringArray(value: unknown): string[] {
    if (!Array.isArray(value)) {
        return [];
    }
    return value.filter((entry): entry is string => typeof entry === "string");
}

/** @schema runtime-guard:event-target-node */
export function isNodeTarget(value: EventTarget | null): value is Node {
    return value instanceof Node;
}

/** @schema runtime-guard:event-target-html-element */
export function isHTMLElementTarget(value: EventTarget | null): value is HTMLElement {
    return value instanceof HTMLElement;
}

/** @schema runtime-guard:json-record-array — guards unknown API payload arrays before renderer dispatch */
export function isJsonRecordArray(value: unknown): value is Array<Record<string, unknown>> {
    return Array.isArray(value) && value.every((item) => isRecord(item));
}

/** @schema-exempt — frontend-only rendering contract, no Pydantic equivalent */
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

/** @schema-exempt — frontend-only rendering contract, no Pydantic equivalent */
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

/** @schema-exempt — frontend-only rendering contract, no Pydantic equivalent */
export interface PlayerPayloadFragment extends Record<string, unknown> { }

export function toPlayerPayloadFragment(value: unknown): PlayerPayloadFragment | null {
    const record = toRecord(value);
    if (!record) {
        return null;
    }
    return { ...record };
}

/** @schema-exempt — frontend-only union type, no Pydantic equivalent */
export type MatchAuditStatusTone = "elite" | "caution" | "danger" | "muted";

function isMatchAuditStatusTone(value: unknown): value is MatchAuditStatusTone {
    return value === "elite" ||
        value === "caution" ||
        value === "danger" ||
        value === "muted";
}

/** @schema-exempt — frontend-only rendering contract, no Pydantic equivalent */
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

/** @schema-exempt — frontend-only rendering contract, no Pydantic equivalent */
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

/** @schema-exempt — frontend-only rendering contract, no Pydantic equivalent */
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

// ── Landing Page — Format Selection Types & Constants ────────────────────────

/** @schema-exempt — frontend-only landing page selection, no Pydantic equivalent */
export type LandingGender = "mens" | "womens";

/** @schema-exempt — frontend-only landing page selection, no Pydantic equivalent */
export type LandingCategory = "internationals" | "domestic";

/** @schema-exempt — frontend-only landing page format slug, no Pydantic equivalent */
export type LandingFormatSlug =
  | "odi" | "t20i" | "test"
  | "ipl" | "bbl" | "psl" | "cpl" | "the-hundred"
  | "wbbl" | "wpl";

/** @schema-exempt — frontend-only landing page format option, no Pydantic equivalent */
export interface LandingFormatOption {
  label: string;
  slug: LandingFormatSlug;
}

/** @schema-exempt — static format options for landing page selector */
export const LANDING_FORMAT_OPTIONS: Record<LandingGender, Record<LandingCategory, LandingFormatOption[]>> = {
  mens: {
    internationals: [
      { label: "ODI", slug: "odi" },
      { label: "T20I", slug: "t20i" },
      { label: "Test", slug: "test" },
    ],
    domestic: [
      { label: "IPL", slug: "ipl" },
      { label: "BBL", slug: "bbl" },
      { label: "PSL", slug: "psl" },
      { label: "CPL", slug: "cpl" },
      { label: "The Hundred", slug: "the-hundred" },
    ],
  },
  womens: {
    internationals: [
      { label: "ODI", slug: "odi" },
      { label: "T20I", slug: "t20i" },
      { label: "Test", slug: "test" },
    ],
    domestic: [
      { label: "WBBL", slug: "wbbl" },
      { label: "WPL", slug: "wpl" },
    ],
  },
};

/** @schema-exempt — display labels for landing gender selection */
export const LANDING_GENDER_LABELS: Record<LandingGender, string> = {
  mens: "Men's",
  womens: "Women's",
};

/** @schema-exempt — display labels for landing category selection */
export const LANDING_CATEGORY_LABELS: Record<LandingCategory, string> = {
  internationals: "Internationals",
  domestic: "Domestic Leagues",
};
