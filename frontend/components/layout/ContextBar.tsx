"use client";

import { useAppContext } from "@/lib/context";
import { SlidersHorizontal } from "lucide-react";
import { useEffect, useRef, useState } from "react";
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
                className="[height:var(--context-bar-height)] [background:var(--bg-surface)] [border-bottom:1px_solid_var(--border-subtle)] [display:flex] [align-items:center] [padding:0_20px] [gap:12px]"
            >
                {[1, 2, 3, 4].map((i) => (
                    <div key={i} className="skeleton [width:140px] [height:36px]" />
                ))}
            </div>
        );
    }

    const fields = manifest.context_fields;

    return (
        <div
            id="context-bar"
            className="animate-fade-in [height:var(--context-bar-height)] [background:var(--bg-surface)] [border-bottom:1px_solid_var(--border-subtle)] [display:flex] [align-items:center] [padding:0_20px] [gap:12px] [overflow-x:auto]"
        >
            <SlidersHorizontal size={16} className="[color:var(--text-disabled)] [flex-shrink:0]" />

            {Object.entries(fields).map(([key, field]) => {
                if (field.type === "dropdown") {
                    return (
                        <DropdownField
                            key={key}
                            fieldKey={key}
                            label={field.label}
                            value={String(contextValues[key] || "")}
                            onChange={(val) => setContextValue(key, val)}
                            options={key === "team_a" || key === "team_b" ? ["All", ...teams] : field.options || []}
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
    const [dropdownPos, setDropdownPos] = useState({ top: 0, left: 0, width: 0 });

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

    useEffect(() => {
        if (isOpen && inputRef.current) {
            const rect = inputRef.current.getBoundingClientRect();
            setDropdownPos({
                top: rect.bottom + 4,
                left: rect.left,
                width: rect.width,
            });
        }
    }, [isOpen, search]);

    const filtered = options.filter(
        (v) => v.label.toLowerCase().includes(search.toLowerCase()) || v.id.toLowerCase().includes(search.toLowerCase())
    );

    const displayValue = options.find((v) => v.id === value)?.label || "";

    const dropdownPortal =
        isOpen && filtered.length > 0
            ? ReactDOM.createPortal(
                  <div
                      ref={dropdownRef}
                      className="[position:fixed] [max-height:300px] [overflow-y:auto] [background:var(--bg-elevated)] [border:1px_solid_var(--border-strong)] [border-radius:var(--radius-md)] [z-index:99999] [box-shadow:0_8px_32px_rgba(0,_0,_0,_0.6)]"
                      style={{ top: dropdownPos.top, left: dropdownPos.left, width: dropdownPos.width }}
                  >
                      <div className="[padding:6px_12px] [font-size:0.7rem] [color:var(--text-disabled)] [border-bottom:1px_solid_var(--border-subtle)] [font-weight:500] [background:var(--bg-elevated)] [border-radius:var(--radius-md)_var(--radius-md)_0_0]">
                          {filtered.length} venue{filtered.length !== 1 ? "s" : ""} found
                      </div>
                      {filtered.slice(0, 50).map((v) => (
                          <button
                              key={v.id}
                              className={`[display:block] [width:100%] [padding:8px_12px] [text-align:left] [border:none] [cursor:pointer] [font-size:0.825rem] [font-family:inherit] [transition:background_150ms] hover:[background:var(--bg-hover)] ${v.id === value ? "[background:var(--accent-glow)] [color:var(--accent-primary)]" : "[background:transparent] [color:var(--text-secondary)]"}`}
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
        <div ref={containerRef} className="[display:flex] [flex-direction:column] [gap:2px] [min-width:170px] [position:relative]">
            <label
                htmlFor={`context-${fieldKey}`}
                className="[font-size:0.65rem] [font-weight:600] [color:var(--text-disabled)] [text-transform:uppercase] [letter-spacing:0.05em]"
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
