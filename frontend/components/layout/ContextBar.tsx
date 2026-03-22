"use client";

import { useCallback } from "react";
import { useRouter, useSearchParams, usePathname } from "next/navigation";
import { useAppContext } from "@/lib/context";
import { Combobox } from "@/components/common/Combobox";

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

    return (
        <div
            className="context-bar animate-fade-in"
            role="toolbar"
            aria-label="Analysis filters"
        >
            {fieldEntries.map(([key, field]) => {
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
                            label={field.label}
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
                    const placeholder =
                        typeof field.placeholder === "string"
                            ? field.placeholder
                            : `Select ${field.label.toLowerCase()}...`;
                    return (
                        <ComboboxField
                            key={key}
                            label={field.label}
                            value={value}
                            onChange={(val) => setParam(key, val)}
                            options={options}
                            placeholder={isLoadingContext ? "Loading..." : placeholder}
                            disabled={isLoadingContext}
                        />
                    );
                }

                if (field.type === "slider") {
                    const numValue = value ? Number(value) : (field.default ?? 5);
                    return (
                        <SliderField
                            key={key}
                            fieldKey={key}
                            label={field.label}
                            value={numValue}
                            onChange={(val) => setParam(key, String(val))}
                            min={field.min ?? 1}
                            max={field.max ?? 50}
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
}: {
    label: string;
    value: string;
    onChange: (val: string) => void;
    options: { label: string; value: string }[];
    placeholder: string;
    disabled: boolean;
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
