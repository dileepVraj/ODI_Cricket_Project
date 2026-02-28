/**
 * components/inputs/ExtraInputRenderer.tsx
 * 
 * Renders manifest-driven extra_inputs fields (combobox, text, etc.)
 * Currently supports:
 *   - "combobox" type: searchable dropdown, loads options from API source
 */
"use client";

import { useState, useEffect, useRef, useMemo } from "react";
import { Search, ChevronDown, X } from "lucide-react";
import { fetchPlayers, fetchHostCountries } from "@/lib/api";

interface ExtraInputField {
    type: string;
    label: string;
    required?: boolean;
    source?: string;
    options?: string[];
}

interface ExtraInputRendererProps {
    formatKey: string;
    extraInputs: Record<string, ExtraInputField>;
    contextValues: Record<string, string | number>;
    values: Record<string, string>;
    onChange: (key: string, value: string) => void;
}

export default function ExtraInputRenderer({
    formatKey,
    extraInputs,
    contextValues,
    values,
    onChange,
}: ExtraInputRendererProps) {
    // Filter out squad_builder (handled separately)
    const fields = Object.entries(extraInputs).filter(
        ([key, val]) => key !== "squad_builder" && typeof val === "object" && val.type
    );

    if (fields.length === 0) return null;

    return (
        <div
            className="[display:flex] [flex-direction:column] [gap:12px] [margin-bottom:16px]"
        >
            {fields.map(([key, field]) => (
                <ExtraInputField
                    key={key}
                    fieldKey={key}
                    field={field}
                    formatKey={formatKey}
                    contextValues={contextValues}
                    value={values[key] || ""}
                    onChange={(val) => onChange(key, val)}
                />
            ))}
        </div>
    );
}

// ═══════════════════════════════════════════════════════════════════════════
// COMBOBOX FIELD
// ═══════════════════════════════════════════════════════════════════════════

function ExtraInputField({
    fieldKey,
    field,
    formatKey,
    contextValues,
    value,
    onChange,
}: {
    fieldKey: string;
    field: ExtraInputField;
    formatKey: string;
    contextValues: Record<string, string | number>;
    value: string;
    onChange: (val: string) => void;
}) {
    const [comboOptions, setComboOptions] = useState<string[]>([]);
    const [remoteDropdownOptions, setRemoteDropdownOptions] = useState<string[]>([]);
    const [search, setSearch] = useState("");
    const [isOpen, setIsOpen] = useState(false);
    const [isLoading, setIsLoading] = useState(false);
    const inputRef = useRef<HTMLInputElement>(null);
    const dropdownRef = useRef<HTMLDivElement>(null);

    // Determine team source for player combobox.
    // Supports:
    //   - template source: /api/{fmt}/context/players/{team}
    //   - fixed source:    /api/{fmt}/context/players/All
    const sourceTeam = useMemo(() => {
        if (!field.source) return "";
        if (field.source.includes("{team}")) {
            // Try team_a first, then team_b
            const teamA = contextValues.team_a;
            const teamB = contextValues.team_b;
            return String(teamA || teamB || "");
        }
        const marker = "/context/players/";
        if (field.source.includes(marker)) {
            const tail = field.source.split(marker)[1] || "";
            return decodeURIComponent(tail.split("?")[0]).trim();
        }
        return "";
    }, [field.source, contextValues.team_a, contextValues.team_b]);

    // Load options when team changes
    useEffect(() => {
        if (field.type !== "combobox" || !sourceTeam) return;
        queueMicrotask(() => setIsLoading(true));
        fetchPlayers(formatKey, sourceTeam)
            .then((players) => {
                setComboOptions(players);
                setIsLoading(false);
            })
            .catch(() => setIsLoading(false));
    }, [field.type, formatKey, sourceTeam]);

    // Load options for dropdown fields
    useEffect(() => {
        if (field.type !== "dropdown") return;
        if (field.source?.includes("/context/host_countries")) {
            queueMicrotask(() => setIsLoading(true));
            fetchHostCountries(formatKey)
                .then((countries) => {
                    setRemoteDropdownOptions(countries);
                    setIsLoading(false);
                })
                .catch(() => setIsLoading(false));
            return;
        }
    }, [field.type, field.source, field.options, formatKey]);

    const dropdownOptions = useMemo(() => {
        if (field.source?.includes("/context/host_countries")) {
            return remoteDropdownOptions;
        }
        return Array.isArray(field.options) ? field.options : [];
    }, [field.source, field.options, remoteDropdownOptions]);

    // Close dropdown on outside click
    useEffect(() => {
        function handleClick(e: MouseEvent) {
            if (
                dropdownRef.current &&
                !dropdownRef.current.contains(e.target as Node) &&
                inputRef.current &&
                !inputRef.current.contains(e.target as Node)
            ) {
                setIsOpen(false);
            }
        }
        document.addEventListener("mousedown", handleClick);
        return () => document.removeEventListener("mousedown", handleClick);
    }, []);

    const filtered = comboOptions.filter((o) =>
        o.toLowerCase().includes(search.toLowerCase())
    );

    if (field.type === "dropdown") {
        const isCountryField = fieldKey === "country_name";
        return (
            <div>
                <label
                    className="[display:block] [font-size:0.8rem] [font-weight:600] [color:var(--text-secondary)] [margin-bottom:6px]"
                >
                    {field.label}
                    {field.required && (
                        <span className="[color:var(--tier-danger)] [margin-left:4px]">*</span>
                    )}
                </label>
                <select
                    value={value}
                    onChange={(e) => onChange(e.target.value)}
                    disabled={isLoading}
                    className="[width:100%] [padding:8px_12px] [background:var(--bg-surface)] [border:1px_solid_var(--border)] [border-radius:var(--radius-md)] [color:var(--text-primary)] [font-size:0.85rem] [outline:none] [cursor:pointer]"
                >
                    <option value="">
                        {isCountryField ? "Home Team Country (Default)" : "Select..."}
                    </option>
                    {dropdownOptions.map((opt) => (
                        <option key={opt} value={opt}>
                            {opt}
                        </option>
                    ))}
                </select>
            </div>
        );
    }

    if (field.type === "combobox") {
        return (
            <div className="[position:relative]">
                <label
                    className="[display:block] [font-size:0.8rem] [font-weight:600] [color:var(--text-secondary)] [margin-bottom:6px]"
                >
                    {field.label}
                    {field.required && (
                        <span className="[color:var(--tier-danger)] [margin-left:4px]">*</span>
                    )}
                </label>

                {/* Selected value or search input */}
                <div
                    className="[display:flex] [align-items:center] [gap:8px] [padding:8px_12px] [background:var(--bg-surface)] [border:1px_solid_var(--border)] [border-radius:var(--radius-md)] [cursor:pointer]"
                    onClick={() => {
                        setIsOpen(!isOpen);
                        setTimeout(() => inputRef.current?.focus(), 50);
                    }}
                >
                    <Search size={14} className="[color:var(--text-muted)] [flex-shrink:0]" />
                    {value && !isOpen ? (
                        <div
                            className="[flex:1] [display:flex] [align-items:center] [justify-content:space-between]"
                        >
                            <span className="[color:var(--text-primary)] [font-size:0.85rem]">
                                {value}
                            </span>
                            <X
                                size={14}
                                className="[color:var(--text-muted)] [cursor:pointer]"
                                onClick={(e) => {
                                    e.stopPropagation();
                                    onChange("");
                                    setSearch("");
                                }}
                            />
                        </div>
                    ) : (
                        <input
                            ref={inputRef}
                            type="text"
                            placeholder={
                                sourceTeam
                                    ? (sourceTeam.toLowerCase() === "all"
                                        ? "Search players..."
                                        : `Search ${sourceTeam} players...`)
                                    : "Select a team first"
                            }
                            value={search}
                            onChange={(e) => {
                                setSearch(e.target.value);
                                setIsOpen(true);
                            }}
                            onFocus={() => setIsOpen(true)}
                            disabled={!sourceTeam}
                            className="[flex:1] [background:transparent] [border:none] [outline:none] [color:var(--text-primary)] [font-size:0.85rem]"
                        />
                    )}
                    <ChevronDown
                        size={14}
                        className={`[color:var(--text-muted)] [transition:transform_0.2s] ${isOpen ? "[transform:rotate(180deg)]" : "[transform:rotate(0deg)]"}`}
                    />
                </div>

                {/* Dropdown */}
                {isOpen && sourceTeam && (
                    <div
                        ref={dropdownRef}
                        className="[position:absolute] [top:100%] [left:0px] [right:0px] [z-index:100] [margin-top:4px] [background:var(--bg-surface)] [border:1px_solid_var(--border)] [border-radius:var(--radius-md)] [max-height:200px] [overflow-y:auto] [box-shadow:0_8px_24px_rgba(0,0,0,0.3)]"
                    >
                        {isLoading ? (
                            <div
                                className="[padding:12px_16px] [color:var(--text-muted)] [font-size:0.82rem] [text-align:center]"
                            >
                                Loading players...
                            </div>
                        ) : filtered.length === 0 ? (
                            <div
                                className="[padding:12px_16px] [color:var(--text-muted)] [font-size:0.82rem] [text-align:center]"
                            >
                                No players found
                            </div>
                        ) : (
                            filtered.slice(0, 50).map((player) => (
                                <div
                                    key={player}
                                    onClick={() => {
                                        onChange(player);
                                        setSearch("");
                                        setIsOpen(false);
                                    }}
                                    className={`[padding:8px_14px] [font-size:0.82rem] [cursor:pointer] [transition:background_0.15s] ${player === value ? "[color:var(--accent-blue)] [background:rgba(96,_165,_250,_0.08)]" : "[color:var(--text-primary)] [background:transparent]"}`}
                                    onMouseEnter={(e) =>
                                    (e.currentTarget.style.background =
                                        "rgba(255,255,255,0.05)")
                                    }
                                    onMouseLeave={(e) =>
                                    (e.currentTarget.style.background =
                                        player === value
                                            ? "rgba(96, 165, 250, 0.08)"
                                            : "transparent")
                                    }
                                >
                                    {player}
                                </div>
                            ))
                        )}
                    </div>
                )}
            </div>
        );
    }

    // Fallback: basic text input
    return (
        <div>
            <label
                className="[display:block] [font-size:0.8rem] [font-weight:600] [color:var(--text-secondary)] [margin-bottom:6px]"
            >
                {field.label}
            </label>
            <input
                type="text"
                value={value}
                onChange={(e) => onChange(e.target.value)}
                placeholder={`Enter ${field.label.replace(/[^\w\s]/g, "").trim()}`}
                className="[width:100%] [padding:8px_12px] [background:var(--bg-surface)] [border:1px_solid_var(--border)] [border-radius:var(--radius-md)] [color:var(--text-primary)] [font-size:0.85rem] [outline:none]"
            />
        </div>
    );
}
