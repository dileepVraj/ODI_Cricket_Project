"use client";

import { AccessibleCombobox } from "@/components/common/AccessibleCombobox";
import { useAppContext } from "@/lib/context";
import { SlidersHorizontal } from "lucide-react";

export default function ContextBar() {
    const {
        manifest,
        contextValues,
        setContextValue,
        teams,
        venues,
        isLoadingContext,
        isLoadingManifest,
    } = useAppContext();

    if (isLoadingManifest || !manifest) {
        return (
            <div
                id="context-bar"
                className="[height:var(--context-bar-height)] [background:var(--bg-surface)] [border-bottom:1px_solid_var(--border-subtle)] [display:flex] [align-items:center] [padding:0_20px] [gap:12px]"
            >
                {[1, 2, 3, 4].map((i) => (
                    <div key={i} className="skeleton [width:140px] [height:36px]" />
                ))}
            </div>
        );
    }

    const fields = manifest.context_fields;
    const fieldEntries = Object.entries(fields);
    const teamFieldKeys = new Set(
        fieldEntries
            .filter(([, field]) => field.type === "dropdown" && field.source === "teams")
            .map(([key]) => key)
    );
    const venueOptions = venues.map((venue) => ({
        label: venue.label,
        value: venue.id,
    }));

    const getFieldPlaceholder = (field: (typeof fields)[string]): string | undefined => {
        const placeholder = (field as (typeof field) & { placeholder?: unknown }).placeholder;
        return typeof placeholder === "string" ? placeholder : undefined;
    };

    const getComboboxOptions = (field: (typeof fields)[string]) => {
        if (field.source === "venues") {
            return venueOptions;
        }

        return (field.options || []).map((option) => ({
            label: option,
            value: option,
        }));
    };

    return (
        <div
            id="context-bar"
            className="animate-fade-in [height:var(--context-bar-height)] [background:var(--bg-surface)] [border-bottom:1px_solid_var(--border-subtle)] [display:flex] [align-items:center] [padding:0_20px] [gap:12px] [overflow-x:auto]"
        >
            <SlidersHorizontal size={16} className="[color:var(--text-disabled)] [flex-shrink:0]" />

            {fieldEntries.map(([key, field]) => {
                if (field.type === "dropdown") {
                    let dropdownOptions = field.options || [];

                    if (teamFieldKeys.has(key)) {
                        // TODO: drive entirely from manifest when team selector primitive is available.
                        dropdownOptions = ["All", ...teams];
                    }

                    return (
                        <DropdownField
                            key={key}
                            fieldKey={key}
                            label={field.label}
                            value={String(contextValues[key] || "")}
                            onChange={(val) => setContextValue(key, val)}
                            options={dropdownOptions}
                            isLoading={isLoadingContext}
                        />
                    );
                }

                if (field.type === "combobox") {
                    return (
                        <ComboboxField
                            key={key}
                            label={field.label}
                            value={String(contextValues[key] || "")}
                            onChange={(val) => setContextValue(key, val)}
                            options={getComboboxOptions(field)}
                            placeholder={
                                getFieldPlaceholder(field) ||
                                `Select ${field.label.toLowerCase()}...`
                            }
                            isLoading={isLoadingContext}
                        />
                    );
                }

                if (field.type === "slider") {
                    return (
                        <SliderField
                            key={key}
                            fieldKey={key}
                            label={field.label}
                            value={Number(contextValues[key]) || field.default || 5}
                            onChange={(val) => setContextValue(key, val)}
                            min={field.min || 1}
                            max={field.max || 50}
                        />
                    );
                }

                return null;
            })}
        </div>
    );
}

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
        <div className="[display:flex] [flex-direction:column] [gap:2px] [min-width:140px]">
            <label
                htmlFor={`context-${fieldKey}`}
                className="[font-size:0.65rem] [font-weight:600] [color:var(--text-disabled)] [text-transform:uppercase] [letter-spacing:0.05em]"
            >
                {label}
            </label>
            <select
                id={`context-${fieldKey}`}
                className="context-input [cursor:pointer] [appearance:auto]"
                value={value}
                onChange={(e) => onChange(e.target.value)}
                disabled={isLoading}
            >
                <option value="">Select...</option>
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
    isLoading,
}: {
    label: string;
    value: string;
    onChange: (val: string) => void;
    options: { label: string; value: string }[];
    placeholder: string;
    isLoading: boolean;
}) {
    return (
        <div className="[display:flex] [flex-direction:column] [gap:2px] [min-width:170px]">
            <label className="[display:flex] [flex-direction:column] [gap:2px]">
                <span className="[font-size:0.65rem] [font-weight:600] [color:var(--text-disabled)] [text-transform:uppercase] [letter-spacing:0.05em]">
                    {label}
                </span>
                <AccessibleCombobox
                    value={value}
                    onChange={onChange}
                    options={isLoading ? [] : options}
                    placeholder={isLoading ? "Loading..." : placeholder}
                />
            </label>
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
        <div className="[display:flex] [flex-direction:column] [gap:2px] [min-width:130px]">
            <label
                htmlFor={`context-${fieldKey}`}
                className="[font-size:0.65rem] [font-weight:600] [color:var(--text-disabled)] [text-transform:uppercase] [letter-spacing:0.05em]"
            >
                {label}:{" "}
                <span className="[color:var(--accent-primary)] [font-weight:700]">{value}</span>
            </label>
            <div className="[display:flex] [align-items:center] [gap:8px]">
                <span className="[font-size:0.7rem] [color:var(--text-disabled)]">{min}</span>
                <input
                    id={`context-${fieldKey}`}
                    type="range"
                    min={min}
                    max={max}
                    value={value}
                    onChange={(e) => onChange(Number(e.target.value))}
                    className="[flex:1] [accent-color:var(--accent-primary)] [cursor:pointer]"
                />
                <span className="[font-size:0.7rem] [color:var(--text-disabled)]">{max}</span>
            </div>
        </div>
    );
}
