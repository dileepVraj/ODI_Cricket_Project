"use client";

import { useEffect, useState } from "react";
import { X } from "lucide-react";
import { fetchPlayers, fetchVenues, type VenueItem } from "@/lib/api";
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
    const [options, setOptions] = useState<Array<{ label: string; value: string }>>([]);
    const [isLoading, setIsLoading] = useState(false);
    const sourceTeam = resolveSourceTeam(field.source, field.source_params, contextValues);

    useEffect(() => {
        if (field.source === "venues") {
            let cancelled = false;
            setIsLoading(true);
            fetchVenues(formatKey)
                .then((venueItems: VenueItem[]) => {
                    if (cancelled) return;
                    setOptions(venueItems.map((v) => ({ label: v.label, value: v.id })));
                    setIsLoading(false);
                })
                .catch(() => {
                    if (cancelled) return;
                    setOptions([]);
                    setIsLoading(false);
                });
            return () => {
                cancelled = true;
            };
        }

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

                setOptions(players.map((p) => ({ label: p, value: p })));
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
    }, [formatKey, sourceTeam, field.source]);

    const allOptions = options;
    const label = sanitizeLabel(field.label);
    const helperText =
        field.source === "venues"
            ? isLoading
                ? "Loading venue options..."
                : options.length === 0
                    ? "No venues available."
                    : `${options.length} venue options ready`
            : !sourceTeam
                ? "Select a team in the Context Bar before choosing a player."
                : isLoading
                    ? `Loading ${label.toLowerCase()} options...`
                    : options.length === 0
                        ? "No players available."
                        : "";

    return (
        <div className="[display:flex] [flex-direction:column] [gap:6px]">
            <div className="[display:flex] [align-items:center] [justify-content:space-between]">
                <span className="[font-size:0.8rem] [font-weight:600] [color:var(--text-secondary)]">
                    {field.label}
                    {field.required ? (
                        <span className="[color:var(--tier-danger)] [margin-left:4px]">*</span>
                    ) : null}
                </span>
                {value ? (
                    <button
                        type="button"
                        className="btn-ghost [padding:4px]"
                        onClick={() => onChange("")}
                        aria-label={`Clear selected ${label}`}
                    >
                        <X size={14} />
                    </button>
                ) : null}
            </div>

            <AccessibleCombobox
                value={value}
                onChange={onChange}
                options={allOptions}
                placeholder={
                    field.source === "venues"
                        ? "Search venue..."
                        : !sourceTeam
                            ? "Select a team first"
                            : `Search ${label}...`
                }
            />

            <p className="[font-size:0.74rem] [color:var(--text-muted)]">
                {helperText}
            </p>
        </div>
    );
}
