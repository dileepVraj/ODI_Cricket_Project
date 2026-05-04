import { FMT_ODI, FMT_IPL } from "@/lib/api";

export type HistoryLeague = "all" | typeof FMT_ODI | typeof FMT_IPL;
export type HistoryDateRangeMode = "days" | "months" | "all" | "custom";

/** @schema none -- frontend-only filter state */
export interface HistoryFilters {
    league: HistoryLeague;
    year: string;
    dateRangeMode: HistoryDateRangeMode;
    dateRangeValue: string;
    dateFrom: string;
    dateTo: string;
}

export const HISTORY_LEAGUE_OPTIONS = [
    { key: "all", label: "All leagues" },
    { key: FMT_ODI, label: "ODI" },
    { key: FMT_IPL, label: "IPL" },
] as const;

export const HISTORY_DATE_RANGE_MODE_OPTIONS = [
    { key: "days", label: "Days" },
    { key: "months", label: "Months" },
    { key: "all", label: "All Time" },
    { key: "custom", label: "Custom dates" },
] as const;

/** @schema none -- frontend-only UI primitive */
export interface HistorySelectOption {
    key: string;
    label: string;
}

const DEFAULT_FILTERS: HistoryFilters = {
    league: "all",
    year: "",
    dateRangeMode: "days",
    dateRangeValue: "7",
    dateFrom: "",
    dateTo: "",
};

const RELATIVE_RANGE_PATTERN = /^(\d+)([dm])$/;
const LEGACY_RANGE_MAP: Record<string, { dateRangeMode: HistoryDateRangeMode; dateRangeValue: string }> = {
    "7d": { dateRangeMode: "days", dateRangeValue: "7" },
    "15d": { dateRangeMode: "days", dateRangeValue: "15" },
    "30d": { dateRangeMode: "days", dateRangeValue: "30" },
    "3m": { dateRangeMode: "months", dateRangeValue: "3" },
    "6m": { dateRangeMode: "months", dateRangeValue: "6" },
    "12m": { dateRangeMode: "months", dateRangeValue: "12" },
};

type SearchParamReader = {
    get(name: string): string | null;
};

function isValidCalendarDate(value: string): boolean {
    if (!/^\d{4}-\d{2}-\d{2}$/.test(value)) {
        return false;
    }

    const parsed = new Date(`${value}T00:00:00Z`);
    return !Number.isNaN(parsed.getTime()) && parsed.toISOString().slice(0, 10) === value;
}

function normalizeLeague(value: string | null, searchParams: SearchParamReader): HistoryLeague {
    const candidate = value?.trim().toLowerCase() ?? "";
    if (candidate === "all" || candidate === FMT_ODI || candidate === FMT_IPL) {
        return candidate;
    }

    const legacyScope = searchParams.get("format_scope")?.trim().toLowerCase() ?? "";
    if (legacyScope === "all") {
        return "all";
    }
    if (legacyScope === "single") {
        const legacyFormat = searchParams.get("format")?.trim().toLowerCase() ?? "";
        if (legacyFormat === FMT_ODI || legacyFormat === FMT_IPL) {
            return legacyFormat;
        }
    }

    return DEFAULT_FILTERS.league;
}

function normalizeYear(value: string | null): string {
    const candidate = value?.trim() ?? "";
    return /^\d{4}$/.test(candidate) ? candidate : "";
}

function normalizePositiveIntegerText(value: string | null): string {
    const candidate = value?.trim() ?? "";
    return /^\d+$/.test(candidate) && Number(candidate) > 0 ? candidate : DEFAULT_FILTERS.dateRangeValue;
}

function normalizeCalendarDate(value: string | null): string {
    const candidate = value?.trim() ?? "";
    return isValidCalendarDate(candidate) ? candidate : "";
}

function parseRelativeRange(value: string | null): { dateRangeMode: HistoryDateRangeMode; dateRangeValue: string } | null {
    const candidate = value?.trim().toLowerCase() ?? "";
    const match = RELATIVE_RANGE_PATTERN.exec(candidate);
    if (!match) {
        return null;
    }

    const count = Number.parseInt(match[1], 10);
    if (!Number.isInteger(count) || count <= 0) {
        return null;
    }

    return {
        dateRangeMode: match[2] === "m" ? "months" : "days",
        dateRangeValue: String(count),
    };
}

function parseLegacyDateRange(searchParams: SearchParamReader): { dateRangeMode: HistoryDateRangeMode; dateRangeValue: string } | null {
    const rangeType = searchParams.get("date_range_type")?.trim().toLowerCase() ?? "";
    if (rangeType === "custom") {
        return {
            dateRangeMode: "custom",
            dateRangeValue: DEFAULT_FILTERS.dateRangeValue,
        };
    }

    if (rangeType !== "preset") {
        return null;
    }

    const preset = searchParams.get("date_preset")?.trim().toLowerCase() ?? "";
    return LEGACY_RANGE_MAP[preset] ?? null;
}

export function getDefaultHistoryFilters(): HistoryFilters {
    return { ...DEFAULT_FILTERS };
}

export function getHistoryYearOptions(currentYear: number = new Date().getFullYear(), count: number = 10): HistorySelectOption[] {
    const options: HistorySelectOption[] = [{ key: "", label: "Any year" }];
    for (let year = currentYear; year >= currentYear - (count - 1); year -= 1) {
        options.push({ key: String(year), label: String(year) });
    }
    return options;
}

export function parseHistoryFilters(searchParams: SearchParamReader): HistoryFilters {
    const league = normalizeLeague(searchParams.get("league"), searchParams);
    const year = normalizeYear(searchParams.get("season") ?? searchParams.get("year"));

    const dateRange = searchParams.get("date_range");
    const legacyRange = parseLegacyDateRange(searchParams);
    const parsedRange = parseRelativeRange(dateRange) ?? legacyRange;

    if (dateRange === "custom" || legacyRange?.dateRangeMode === "custom") {
        return {
            league,
            year,
            dateRangeMode: "custom",
            dateRangeValue: DEFAULT_FILTERS.dateRangeValue,
            dateFrom: normalizeCalendarDate(searchParams.get("date_from")),
            dateTo: normalizeCalendarDate(searchParams.get("date_to")),
        };
    }

    if (parsedRange) {
        return {
            league,
            year,
            dateRangeMode: parsedRange.dateRangeMode,
            dateRangeValue: normalizePositiveIntegerText(parsedRange.dateRangeValue),
            dateFrom: "",
            dateTo: "",
        };
    }

    return { ...DEFAULT_FILTERS, league, year };
}

export function isDefaultHistoryFilters(filters: HistoryFilters): boolean {
    return (
        filters.league === DEFAULT_FILTERS.league &&
        filters.year === DEFAULT_FILTERS.year &&
        filters.dateRangeMode === DEFAULT_FILTERS.dateRangeMode &&
        filters.dateRangeValue === DEFAULT_FILTERS.dateRangeValue &&
        filters.dateFrom === DEFAULT_FILTERS.dateFrom &&
        filters.dateTo === DEFAULT_FILTERS.dateTo
    );
}

export function buildHistoryDateRangeParam(filters: HistoryFilters): string {
    if (filters.dateRangeMode === "custom") {
        return "custom";
    }

    if (filters.dateRangeMode === "all") {
        return "all";
    }

    const normalizedValue = normalizePositiveIntegerText(filters.dateRangeValue);
    return `${normalizedValue}${filters.dateRangeMode === "months" ? "m" : "d"}`;
}

export function isHistoryCustomRangeIncomplete(filters: HistoryFilters): boolean {
    return filters.dateRangeMode === "custom" && (!filters.dateFrom || !filters.dateTo);
}

export function isHistoryCustomRangeInvalid(filters: HistoryFilters): boolean {
    if (filters.dateRangeMode !== "custom" || !filters.dateFrom || !filters.dateTo) {
        return false;
    }

    return filters.dateFrom > filters.dateTo;
}
