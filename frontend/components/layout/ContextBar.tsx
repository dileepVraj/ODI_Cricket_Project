"use client";

import { useCallback } from "react";
import { useRouter, useSearchParams, usePathname } from "next/navigation";
import { useAppContext } from "@/lib/context";
import { Combobox } from "@/components/common/Combobox";

// Strip leading emoji + trailing space from manifest labels before display
function stripEmoji(label: string): string {
    return label.replace(/^[\u{1F000}-\u{1FFFF}\u{2600}-\u{27BF}]\uFE0F?\s*/u, "");
}

// ── Main Component ──────────────────────────────────────────────────────

export default function ContextBar() {
    const { manifest, teams, venues, isLoadingManifest, isLoadingContext } = useAppContext();
    const searchParams = useSearchParams();
    const pathname = usePathname();
    const router = useRouter();

    const setParam = useCallback(
        (key: string, value: string) => {
            const params = new URLSearchParams(searchParams.toString());
            if (value) {
                params.set(key, value);
            } else {
                params.delete(key);
            }
            router.replace(`${pathname}?${params.toString()}`, { scroll: false });
        },
        [searchParams, pathname, router],
    );

    if (isLoadingManifest || !manifest) {
        return (
            <div className="context-bar" role="toolbar" aria-label="Analysis filters">
                {[1, 2, 3, 4].map((i) => (
                    <div key={i} className="skeleton w-36 h-9" />
                ))}
            </div>
        );
    }

    const fieldEntries = Object.entries(manifest.context_fields);

    // On the dashboard route, show only team context — no venue, years, or region.
    const DASHBOARD_FIELDS = new Set(["team_a", "team_b"]);
    const visibleEntries = pathname === "/"
        ? fieldEntries.filter(([key]) => DASHBOARD_FIELDS.has(key))
        : fieldEntries;

    return (
        <div
            className="context-bar animate-fade-in"
            role="toolbar"
            aria-label="Analysis filters"
        >
            {visibleEntries.map(([key, field]) => {
                const value = searchParams.get(key) ?? "";

                if (field.type === "dropdown") {
                    const options =
                        field.source === "teams"
                            ? teams
                            : (field.options ?? []);
                    return (
                        <DropdownField
                            key={key}
                            fieldKey={key}
                            label={stripEmoji(field.label)}
                            value={value}
                            onChange={(val) => setParam(key, val)}
                            options={options}
                            isLoading={isLoadingContext}
                        />
                    );
                }

                if (field.type === "combobox") {
                    const options =
                        field.source === "venues"
                            ? venues.map((v) => ({ label: v.label, value: v.id }))
                            : (field.options ?? []).map((o) => ({ label: o, value: o }));
                    const cleanLabel = stripEmoji(field.label);
                    const placeholder =
                        typeof field.placeholder === "string"
                            ? field.placeholder
                            : `Select ${cleanLabel.toLowerCase()}...`;
                    return (
                        <ComboboxField
                            key={key}
                            label={cleanLabel}
                            value={value}
                            onChange={(val) => setParam(key, val)}
                            options={options}
                            placeholder={isLoadingContext ? "Loading..." : placeholder}
                            disabled={isLoadingContext}
                            tooltip={`Select ${cleanLabel.toLowerCase()}`}
                        />
                    );
                }

                if (field.type === "slider") {
                    const numValue = value ? Number(value) : (field.default ?? 5);
                    return (
                        <SliderField
                            key={key}
                            fieldKey={key}
                            label={stripEmoji(field.label)}
                            value={numValue}
                            onChange={(val) => setParam(key, String(val))}
                            min={field.min ?? 1}
                            max={field.max ?? 50}
                        />
                    );
                }

                if (field.type === "number") {
                    const defaultVal = typeof field.default === "number" ? field.default : 5;
                    const numValue = value ? Number(value) : defaultVal;
                    return (
                        <NumberField
                            key={key}
                            fieldKey={key}
                            label={stripEmoji(field.label)}
                            value={numValue}
                            onChange={(val) => setParam(key, String(val))}
                            min={field.min ?? 1}
                            max={field.max ?? 50}
                            defaultVal={defaultVal}
                        />
                    );
                }

                return null;
            })}
        </div>
    );
}

// ── Sub-components ──────────────────────────────────────────────────────

function DropdownField({
    fieldKey,
    label,
    value,
    onChange,
    options,
    isLoading,
}: {
    fieldKey: string;
    label: string;
    value: string;
    onChange: (val: string) => void;
    options: string[];
    isLoading: boolean;
}) {
    return (
        <div className="context-field min-w-36">
            <label htmlFor={`ctx-${fieldKey}`} className="context-field-label">
                {label}
            </label>
            <select
                id={`ctx-${fieldKey}`}
                className="context-input"
                value={value}
                onChange={(e) => onChange(e.target.value)}
                disabled={isLoading}
                aria-label={label}
            >
                <option value="">All</option>
                {options.map((opt) => (
                    <option key={opt} value={opt}>
                        {opt}
                    </option>
                ))}
            </select>
        </div>
    );
}

function ComboboxField({
    label,
    value,
    onChange,
    options,
    placeholder,
    disabled,
    tooltip,
}: {
    label: string;
    value: string;
    onChange: (val: string) => void;
    options: { label: string; value: string }[];
    placeholder: string;
    disabled: boolean;
    tooltip?: string;
}) {
    return (
        <div className="context-field min-w-44">
            <span className="context-field-label">{label}</span>
            <Combobox
                value={value}
                onChange={onChange}
                options={options}
                placeholder={placeholder}
                disabled={disabled}
                tooltip={tooltip}
            />
        </div>
    );
}

function NumberField({
    fieldKey,
    label,
    value,
    onChange,
    min,
    max,
    defaultVal,
}: {
    fieldKey: string;
    label: string;
    value: number;
    onChange: (val: number) => void;
    min: number;
    max: number;
    defaultVal: number;
}) {
    return (
        <div className="context-field min-w-24">
            <label htmlFor={`ctx-${fieldKey}`} className="context-field-label">
                {label}
            </label>
            <input
                id={`ctx-${fieldKey}`}
                type="number"
                min={min}
                max={max}
                value={value}
                onChange={(e) => {
                    const raw = Number(e.target.value);
                    if (!e.target.value) return;
                    const clamped = Math.min(max, Math.max(min, raw));
                    onChange(clamped);
                }}
                onBlur={(e) => {
                    if (!e.target.value || isNaN(Number(e.target.value))) {
                        onChange(defaultVal);
                    }
                }}
                className="context-input"
                aria-label={`${label}: enter a value between ${min} and ${max}`}
            />
        </div>
    );
}

function SliderField({
    fieldKey,
    label,
    value,
    onChange,
    min,
    max,
}: {
    fieldKey: string;
    label: string;
    value: number;
    onChange: (val: number) => void;
    min: number;
    max: number;
}) {
    return (
        <div className="context-field min-w-36">
            <label htmlFor={`ctx-${fieldKey}`} className="context-field-label">
                {label}:{" "}
                <span className="context-field-slider-value">{value}</span>
            </label>
            <div className="flex items-center gap-2">
                <span className="context-field-slider-bound">{min}</span>
                <input
                    id={`ctx-${fieldKey}`}
                    type="range"
                    min={min}
                    max={max}
                    value={value}
                    onChange={(e) => onChange(Number(e.target.value))}
                    className="context-range"
                    aria-label={`${label}: ${value}`}
                    aria-valuemin={min}
                    aria-valuemax={max}
                    aria-valuenow={value}
                />
                <span className="context-field-slider-bound">{max}</span>
            </div>
        </div>
    );
}
