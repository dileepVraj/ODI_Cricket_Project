/**
 * @schema-exempt frontend-only — display utility types for player intel renderers
 */
export type SectionTone = "primary" | "secondary" | "tertiary";

/**
 * @schema-exempt frontend-only — display utility types for player intel renderers
 */
export type Scalar = string | number | null | undefined;

/**
 * @schema-exempt frontend-only — display utility types for player intel renderers
 */
export type DataRow = Record<string, unknown>;

export const PHASE_LABELS: Record<string, string> = { pp: "Powerplay", mid: "Middle", dth: "Death Overs" };
export const PHASE_ORDER = ["pp", "mid", "dth"] as const;

export function toneBarClass(tone: SectionTone): string {
    if (tone === "primary") return "[background:var(--accent-primary)]";
    if (tone === "secondary") return "[background:var(--accent-secondary)]";
    return "[background:var(--accent-tertiary)]";
}

export function rowValue(row: DataRow, key: string): Scalar {
    const value = row[key];
    return typeof value === "string" || typeof value === "number" || value === null || value === undefined ? value : undefined;
}

export function numericValue(value: Scalar): number | null {
    if (typeof value === "number") return Number.isFinite(value) ? value : null;
    if (typeof value !== "string") return value === null ? null : null;
    const trimmed = value.trim();
    if (trimmed === "") return null;
    const parsed = Number(trimmed);
    return Number.isFinite(parsed) ? parsed : null;
}

export function metricText(value: Scalar): string {
    const numeric = numericValue(value);
    if (numeric === null) return "–";
    return Number.isInteger(numeric) ? String(numeric) : numeric.toFixed(1);
}

export function labelText(value: Scalar): string {
    if (value === null || value === undefined) return "";
    return String(value).trim();
}

export function barWidth(value: number | null, maxValue: number): string {
    if (value === null || maxValue <= 0) return "0%";
    return `${Math.min(100, Math.max(0, (value / maxValue) * 100))}%`;
}

export function buildIntelHeaderMsg(name: string, venueLabel: string, yearsInput: string): string {
    if (venueLabel && yearsInput) return `${name} at ${venueLabel} - Last ${yearsInput} Years`;
    if (venueLabel) return `${name} at ${venueLabel} - All Time`;
    if (yearsInput) return `${name} - Last ${yearsInput} Years`;
    return `${name} - Overall`;
}
