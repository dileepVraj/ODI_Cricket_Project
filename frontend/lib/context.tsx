/**
 * lib/context.tsx — Global App State (React Context)
 * 
 * Stores:
 *   - Active format (odi, t20i, etc.)
 *   - Loaded manifest for the active format
 *   - Context bar values (venue, team_a, team_b, years, region)
 *   - Format metadata (available formats list)
 */
"use client";

import React, {
    createContext,
    useContext,
    useState,
    useCallback,
    useEffect,
    type ReactNode,
} from "react";
import {
    fetchFormats,
    fetchManifest,
    fetchTeams,
    fetchVenues,
    type FormatInfo,
    type Manifest,
    type VenueItem,
} from "./api";

// ── Types ───────────────────────────────────────────────────────────────

export interface ContextValues {
    venue: string;
    team_a: string;
    team_b: string;
    years: number;
    region: string;
    [key: string]: string | number;
}

interface AppState {
    // Format
    formats: FormatInfo[];
    activeFormat: string;
    manifest: Manifest | null;
    isLoadingManifest: boolean;

    // Context bar values
    contextValues: ContextValues;
    setContextValue: (key: string, value: string | number) => void;

    // Context data (for populating dropdowns)
    teams: string[];
    venues: VenueItem[];
    isLoadingContext: boolean;

    // Actions
    switchFormat: (formatKey: string) => void;
}

const defaultContextValues: ContextValues = {
    venue: "",
    team_a: "",
    team_b: "",
    years: 5,
    region: "All",
};

// ── Context ─────────────────────────────────────────────────────────────

const AppContext = createContext<AppState | null>(null);

export function useAppContext(): AppState {
    const ctx = useContext(AppContext);
    if (!ctx) throw new Error("useAppContext must be used inside AppProvider");
    return ctx;
}

// ── Provider ────────────────────────────────────────────────────────────

export function AppProvider({ children }: { children: ReactNode }) {
    const [formats, setFormats] = useState<FormatInfo[]>([]);
    const [activeFormat, setActiveFormat] = useState<string>("");
    const [manifest, setManifest] = useState<Manifest | null>(null);
    const [isLoadingManifest, setIsLoadingManifest] = useState(false);

    const [contextValues, setContextValues] = useState<ContextValues>(defaultContextValues);
    const [teams, setTeams] = useState<string[]>([]);
    const [venues, setVenues] = useState<VenueItem[]>([]);
    const [isLoadingContext, setIsLoadingContext] = useState(false);

    // ── Initial load: fetch available formats ─────────────────────────
    useEffect(() => {
        let cancelled = false;
        fetchFormats()
            .then((fmts) => {
                if (cancelled) return;
                setFormats(fmts);
                // Auto-select first format with manifest
                const active = fmts.find((f) => f.has_manifest);
                if (active) {
                    setActiveFormat(active.key);
                }
            })
            .catch((err) => console.error("Failed to fetch formats:", err));
        return () => { cancelled = true; };
    }, []);

    // ── Load manifest when format changes ─────────────────────────────
    useEffect(() => {
        if (!activeFormat) return;
        let cancelled = false;

        setIsLoadingManifest(true);
        setManifest(null);

        fetchManifest(activeFormat)
            .then((m) => {
                if (cancelled) return;
                setManifest(m);
                // Reset context values with manifest defaults
                const years = m.context_fields?.years?.default ?? 5;
                setContextValues({ ...defaultContextValues, years });
            })
            .catch((err) => console.error("Failed to fetch manifest:", err))
            .finally(() => { if (!cancelled) setIsLoadingManifest(false); });

        return () => { cancelled = true; };
    }, [activeFormat]);

    // ── Load context data (teams, venues) when format changes ─────────
    useEffect(() => {
        if (!activeFormat) return;
        let cancelled = false;

        setIsLoadingContext(true);
        Promise.all([fetchTeams(activeFormat), fetchVenues(activeFormat)])
            .then(([t, v]) => {
                if (cancelled) return;
                setTeams(t);
                setVenues(v);
            })
            .catch((err) => console.error("Failed to fetch context:", err))
            .finally(() => { if (!cancelled) setIsLoadingContext(false); });

        return () => { cancelled = true; };
    }, [activeFormat]);

    // ── Set a single context value ────────────────────────────────────
    const setContextValue = useCallback((key: string, value: string | number) => {
        setContextValues((prev) => ({ ...prev, [key]: value }));
    }, []);

    // ── Switch format ─────────────────────────────────────────────────
    const switchFormat = useCallback((formatKey: string) => {
        const fmt = formats.find((f) => f.key === formatKey);
        if (fmt && fmt.has_manifest) {
            setActiveFormat(formatKey);
        }
    }, [formats]);

    return (
        <AppContext.Provider
            value={{
                formats,
                activeFormat,
                manifest,
                isLoadingManifest,
                contextValues,
                setContextValue,
                teams,
                venues,
                isLoadingContext,
                switchFormat,
            }}
        >
            {children}
        </AppContext.Provider>
    );
}
