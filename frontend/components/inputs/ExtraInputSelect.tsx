"use client";

import { useEffect, useId, useState } from "react";
import { fetchHostCountries } from "@/lib/api";

interface ExtraInputFieldDefinition {
    type: string;
    label: string;
    required?: boolean;
    source?: string;
    options?: string[];
}

interface ExtraInputSelectProps {
    formatKey: string;
    field: ExtraInputFieldDefinition;
    value: string;
    onChange: (value: string) => void;
}

function sanitizeLabel(label: string): string {
    return label.replace(/[^\w\s]/g, "").trim() || "option";
}

export default function ExtraInputSelect({
    formatKey,
    field,
    value,
    onChange,
}: ExtraInputSelectProps) {
    const [options, setOptions] = useState<string[]>(Array.isArray(field.options) ? field.options : []);
    const [isLoading, setIsLoading] = useState(false);
    const usesHostCountrySource = Boolean(field.source?.includes("/context/host_countries"));

    useEffect(() => {
        if (!usesHostCountrySource) {
            setOptions(Array.isArray(field.options) ? field.options : []);
            return;
        }

        let cancelled = false;
        setIsLoading(true);

        fetchHostCountries(formatKey)
            .then((countries) => {
                if (cancelled) {
                    return;
                }

                setOptions(countries);
                setIsLoading(false);
            })
            .catch(() => {
                if (cancelled) {
                    return;
                }

                setOptions([]);
                setIsLoading(false);
            });

        return () => {
            cancelled = true;
        };
    }, [field.options, field.source, formatKey, usesHostCountrySource]);

    // TODO: Drive remote select sources from a manifest source registry when that config slot exists.
    const selectId = useId();
    const placeholder = `Select ${sanitizeLabel(field.label)}`;

    return (
        <div className="[display:flex] [flex-direction:column] [gap:6px]">
            <label htmlFor={selectId} className="[font-size:0.8rem] [font-weight:600] [color:var(--text-secondary)]">
                {field.label}
                {field.required ? (
                    <span className="[color:var(--tier-danger)] [margin-left:4px]">*</span>
                ) : null}
            </label>

            <select
                id={selectId}
                value={value}
                onChange={(event) => onChange(event.target.value)}
                disabled={isLoading}
                className="context-input [cursor:pointer]"
            >
                <option value="">
                    {isLoading ? "Loading options..." : placeholder}
                </option>
                {options.map((option) => (
                    <option key={option} value={option}>
                        {option}
                    </option>
                ))}
            </select>
        </div>
    );
}
