/**
 * ContextBar.tsx — Global Context Inputs (Layer 2)
 * 
 * Renders context fields FROM the manifest dynamically:
 *   venue  → Combobox (searchable dropdown)
 *   team_a → Dropdown
 *   team_b → Dropdown
 *   years  → Slider
 *   region → Dropdown
 * 
 * Rule F3: No format-specific code.
 * The manifest declares what fields exist — we just render them.
 */
"use client";

import { useAppContext } from "@/lib/context";
import { SlidersHorizontal } from "lucide-react";
import { useState, useRef, useEffect } from "react";
import ReactDOM from "react-dom";

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
                style={{
                    height: "var(--context-bar-height)",
                    background: "var(--bg-surface)",
                    borderBottom: "1px solid var(--border-subtle)",
                    display: "flex",
                    alignItems: "center",
                    padding: "0 20px",
                    gap: "12px",
                }}
            >
                {[1, 2, 3, 4].map((i) => (
                    <div key={i} className="skeleton" style={{ width: 140, height: 36 }} />
                ))}
            </div>
        );
    }

    const fields = manifest.context_fields;

    return (
        <div
            id="context-bar"
            className="animate-fade-in"
            style={{
                height: "var(--context-bar-height)",
                background: "var(--bg-surface)",
                borderBottom: "1px solid var(--border-subtle)",
                display: "flex",
                alignItems: "center",
                padding: "0 20px",
                gap: "12px",
                overflowX: "auto",
            }}
        >
            <SlidersHorizontal
                size={16}
                style={{ color: "var(--text-disabled)", flexShrink: 0 }}
            />

            {Object.entries(fields).map(([key, field]) => {
                if (field.type === "dropdown") {
                    return (
                        <DropdownField
                            key={key}
                            fieldKey={key}
                            label={field.label}
                            value={String(contextValues[key] || "")}
                            onChange={(val) => setContextValue(key, val)}
                            options={
                                key === "team_a" || key === "team_b"
                                    ? ["All", ...teams]
                                    : field.options || []
                            }
                            isLoading={isLoadingContext}
                        />
                    );
                }

                if (field.type === "combobox") {
                    return (
                        <ComboboxField
                            key={key}
                            fieldKey={key}
                            label={field.label}
                            value={String(contextValues[key] || "")}
                            onChange={(val) => setContextValue(key, val)}
                            options={venues}
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

// ═══════════════════════════════════════════════════════════════════════
// SUB-COMPONENTS
// ═══════════════════════════════════════════════════════════════════════

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
        <div style={{ display: "flex", flexDirection: "column", gap: "2px", minWidth: 140 }}>
            <label
                htmlFor={`context-${fieldKey}`}
                style={{
                    fontSize: "0.65rem",
                    fontWeight: 600,
                    color: "var(--text-disabled)",
                    textTransform: "uppercase",
                    letterSpacing: "0.05em",
                }}
            >
                {label}
            </label>
            <select
                id={`context-${fieldKey}`}
                className="context-input"
                value={value}
                onChange={(e) => onChange(e.target.value)}
                disabled={isLoading}
                style={{ cursor: "pointer", appearance: "auto" }}
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
    options: { id: string; label: string }[];
    isLoading: boolean;
}) {
    const [search, setSearch] = useState("");
    const [isOpen, setIsOpen] = useState(false);
    const containerRef = useRef<HTMLDivElement>(null);
    const inputRef = useRef<HTMLInputElement>(null);
    const dropdownRef = useRef<HTMLDivElement>(null);
    const [dropdownStyle, setDropdownStyle] = useState<React.CSSProperties>({});

    // Debug: log options count
    useEffect(() => {
        console.log(`[ComboboxField:${fieldKey}] options loaded:`, options.length);
    }, [options, fieldKey]);

    // Close on outside click — check both container and portal dropdown
    useEffect(() => {
        function handleClick(e: MouseEvent) {
            const target = e.target as Node;
            const insideContainer = containerRef.current?.contains(target);
            const insideDropdown = dropdownRef.current?.contains(target);
            if (!insideContainer && !insideDropdown) {
                setIsOpen(false);
            }
        }
        document.addEventListener("mousedown", handleClick);
        return () => document.removeEventListener("mousedown", handleClick);
    }, []);

    // Recalculate dropdown position whenever it opens or search changes
    useEffect(() => {
        if (isOpen && inputRef.current) {
            const rect = inputRef.current.getBoundingClientRect();
            setDropdownStyle({
                position: "fixed" as const,
                top: rect.bottom + 4,
                left: rect.left,
                width: rect.width,
                maxHeight: 300,
                overflowY: "auto" as const,
                background: "var(--bg-elevated)",
                border: "1px solid var(--border-strong)",
                borderRadius: "var(--radius-md)",
                zIndex: 99999,
                boxShadow: "0 8px 32px rgba(0,0,0,0.6)",
            });
        }
    }, [isOpen, search]);

    const filtered = options.filter(
        (v) =>
            v.label.toLowerCase().includes(search.toLowerCase()) ||
            v.id.toLowerCase().includes(search.toLowerCase())
    );

    const displayValue = options.find((v) => v.id === value)?.label || "";

    // The portal dropdown — rendered directly in document.body
    const dropdownPortal =
        isOpen && filtered.length > 0
            ? ReactDOM.createPortal(
                <div ref={dropdownRef} style={dropdownStyle}>
                    <div
                        style={{
                            padding: "6px 12px",
                            fontSize: "0.7rem",
                            color: "var(--text-disabled)",
                            borderBottom: "1px solid var(--border-subtle)",
                            fontWeight: 500,
                            background: "var(--bg-elevated)",
                            borderRadius: "var(--radius-md) var(--radius-md) 0 0",
                        }}
                    >
                        {filtered.length} venue{filtered.length !== 1 ? "s" : ""} found
                    </div>
                    {filtered.slice(0, 50).map((v) => (
                        <button
                            key={v.id}
                            style={{
                                display: "block",
                                width: "100%",
                                padding: "8px 12px",
                                textAlign: "left",
                                background:
                                    v.id === value
                                        ? "var(--accent-glow)"
                                        : "transparent",
                                color:
                                    v.id === value
                                        ? "var(--accent-primary)"
                                        : "var(--text-secondary)",
                                border: "none",
                                cursor: "pointer",
                                fontSize: "0.825rem",
                                fontFamily: "inherit",
                                transition: "background 150ms",
                            }}
                            onMouseEnter={(e) => {
                                (e.target as HTMLElement).style.background =
                                    "var(--bg-hover)";
                            }}
                            onMouseLeave={(e) => {
                                (e.target as HTMLElement).style.background =
                                    v.id === value
                                        ? "var(--accent-glow)"
                                        : "transparent";
                            }}
                            onClick={() => {
                                onChange(v.id);
                                setIsOpen(false);
                                setSearch("");
                            }}
                        >
                            {v.label}
                        </button>
                    ))}
                </div>,
                document.body
            )
            : null;

    return (
        <div
            ref={containerRef}
            style={{
                display: "flex",
                flexDirection: "column",
                gap: "2px",
                minWidth: 170,
                position: "relative",
            }}
        >
            <label
                htmlFor={`context-${fieldKey}`}
                style={{
                    fontSize: "0.65rem",
                    fontWeight: 600,
                    color: "var(--text-disabled)",
                    textTransform: "uppercase",
                    letterSpacing: "0.05em",
                }}
            >
                {label}
            </label>
            <input
                ref={inputRef}
                id={`context-${fieldKey}`}
                className="context-input"
                type="text"
                value={isOpen ? search : displayValue}
                onChange={(e) => {
                    setSearch(e.target.value);
                    if (!isOpen) setIsOpen(true);
                }}
                onFocus={() => {
                    setIsOpen(true);
                    setSearch("");
                }}
                placeholder={isLoading ? "Loading..." : "Search venue..."}
                disabled={isLoading}
                autoComplete="off"
            />
            {dropdownPortal}
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
        <div style={{ display: "flex", flexDirection: "column", gap: "2px", minWidth: 130 }}>
            <label
                htmlFor={`context-${fieldKey}`}
                style={{
                    fontSize: "0.65rem",
                    fontWeight: 600,
                    color: "var(--text-disabled)",
                    textTransform: "uppercase",
                    letterSpacing: "0.05em",
                }}
            >
                {label}:{" "}
                <span style={{ color: "var(--accent-primary)", fontWeight: 700 }}>
                    {value}
                </span>
            </label>
            <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                <span style={{ fontSize: "0.7rem", color: "var(--text-disabled)" }}>
                    {min}
                </span>
                <input
                    id={`context-${fieldKey}`}
                    type="range"
                    min={min}
                    max={max}
                    value={value}
                    onChange={(e) => onChange(Number(e.target.value))}
                    style={{
                        flex: 1,
                        accentColor: "var(--accent-primary)",
                        cursor: "pointer",
                    }}
                />
                <span style={{ fontSize: "0.7rem", color: "var(--text-disabled)" }}>
                    {max}
                </span>
            </div>
        </div>
    );
}
