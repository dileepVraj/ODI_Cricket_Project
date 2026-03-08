"use client";

import { useEffect, useId, useState } from "react";
import { Search, X } from "lucide-react";
import { fetchPlayers } from "@/lib/api";
import { AccessibleCombobox } from "@/components/common/AccessibleCombobox";

interface ExtraInputFieldDefinition {
    type: string;
    label: string;
    required?: boolean;
    source?: string;
    source_params?: Record<string, string | number>;
}

interface ExtraInputComboboxProps {
    formatKey: string;
    field: ExtraInputFieldDefinition;
    contextValues: Record<string, string | number>;
    value: string;
    onChange: (value: string) => void;
}

function sanitizeLabel(label: string): string {
    return label.replace(/[^\w\s]/g, "").trim() || "player";
}

function resolveSourceTeam(
    source: string | undefined,
    sourceParams: Record<string, string | number> | undefined,
    contextValues: Record<string, string | number>
): string {
    if (source !== "players") {
        return "";
    }

    const teamParam = sourceParams?.team;
    if (teamParam === undefined || teamParam === null) {
        return "";
    }

    const teamStr = String(teamParam);
    if (teamStr === "{team}") {
        const teamA = contextValues.team_a;
        const teamB = contextValues.team_b;
        return String(teamA || teamB || "");
    }

    return teamStr;
}

export default function ExtraInputCombobox({
    formatKey,
    field,
    contextValues,
    value,
    onChange,
}: ExtraInputComboboxProps) {
    const filterId = useId();
    const [options, setOptions] = useState<string[]>([]);
    const [searchTerm, setSearchTerm] = useState("");
    const [isLoading, setIsLoading] = useState(false);
    const sourceTeam = resolveSourceTeam(field.source, field.source_params, contextValues);

    useEffect(() => {
        if (!sourceTeam) {
            setOptions([]);
            return;
        }

        let cancelled = false;
        setIsLoading(true);

        fetchPlayers(formatKey, sourceTeam)
            .then((players) => {
                if (cancelled) {
                    return;
                }

                setOptions(players);
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
    }, [formatKey, sourceTeam]);

    const filteredOptions = options
        .filter((option) => option.toLowerCase().includes(searchTerm.toLowerCase()))
        .slice(0, 50)
        .map((option) => ({
            label: option,
            value: option,
        }));
    const label = sanitizeLabel(field.label);
    const helperText = !sourceTeam
        ? "Select a team in the Context Bar before choosing a player."
        : isLoading
            ? `Loading ${label.toLowerCase()} options...`
            : filteredOptions.length === 0
                ? "No players match this search."
                : `${filteredOptions.length} player options ready`;

    return (
        <div className="[display:flex] [flex-direction:column] [gap:6px]">
            <label htmlFor={filterId} className="[font-size:0.8rem] [font-weight:600] [color:var(--text-secondary)]">
                {field.label}
                {field.required ? (
                    <span className="[color:var(--tier-danger)] [margin-left:4px]">*</span>
                ) : null}
            </label>

            <div className="[display:flex] [align-items:center] [gap:8px]">
                <Search size={14} className="[color:var(--text-muted)] [flex-shrink:0]" />
                <input
                    id={filterId}
                    type="text"
                    value={searchTerm}
                    onChange={(event) => setSearchTerm(event.target.value)}
                    placeholder={`Filter ${label}`}
                    disabled={!sourceTeam}
                    className="context-input"
                    aria-label={`Filter ${label} combobox options`}
                />
                {value ? (
                    <button
                        type="button"
                        className="btn-ghost [padding:8px]"
                        onClick={() => onChange("")}
                        aria-label={`Clear selected ${label}`}
                    >
                        <X size={14} />
                    </button>
                ) : null}
            </div>

            <AccessibleCombobox
                value={value}
                onChange={(nextValue) => {
                    onChange(nextValue);
                    setSearchTerm("");
                }}
                options={filteredOptions}
                placeholder={!sourceTeam ? "Select a team first" : `Choose ${label}`}
            />

            <p className="[font-size:0.74rem] [color:var(--text-muted)]">
                {helperText}
            </p>
        </div>
    );
}
