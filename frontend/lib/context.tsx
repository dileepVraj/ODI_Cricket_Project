/**
 * lib/context.tsx — Global App State (React Context)
 *
 * Stores:
 *   - Active format (odi, t20i, etc.)
 *   - Loaded manifest for the active format
 *   - Format metadata (available formats list)
 *   - Teams and venues for the active format
 *
 * Filter values (venue, team_a, team_b, years, region) live in URL search
 * params and are managed by ContextBar — NOT stored here.
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

interface AppState {
    formats: FormatInfo[];
    activeFormat: string;
    manifest: Manifest | null;
    isLoadingManifest: boolean;
    teams: string[];
    venues: VenueItem[];
    isLoadingContext: boolean;
    switchFormat: (formatKey: string) => void;
}

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

        queueMicrotask(() => {
            if (cancelled) return;
            setIsLoadingManifest(true);
            setManifest(null);
        });

        fetchManifest(activeFormat)
            .then((m) => {
                if (cancelled) return;
                setManifest(m);
            })
            .catch((err) => console.error("Failed to fetch manifest:", err))
            .finally(() => { if (!cancelled) setIsLoadingManifest(false); });

        return () => { cancelled = true; };
    }, [activeFormat]);

    // ── Load context data (teams, venues) when format changes ─────────
    useEffect(() => {
        if (!activeFormat) return;
        let cancelled = false;

        queueMicrotask(() => {
            if (cancelled) return;
            setIsLoadingContext(true);
        });
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
