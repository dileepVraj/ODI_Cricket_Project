/**
 * lib/api.ts — API Client for the Cricket Algo-Trading Platform
 * 
 * Centralized API layer. All components call these functions
 * instead of raw fetch() — single source of truth for API URLs.
 */

const API_BASE = "";  // Empty = same origin (proxied by Next.js rewrites)

// ── Types ───────────────────────────────────────────────────────────────

export interface FormatInfo {
    key: string;
    label: string;
    icon: string;
    has_manifest: boolean;
}

export interface ContextField {
    type: "combobox" | "dropdown" | "slider" | "text" | "textarea";
    label: string;
    required: boolean;
    source?: string;
    options?: string[];
    min?: number;
    max?: number;
    default?: number;
}

export interface ManifestFunction {
    key: string;
    label: string;
    icon: string;
    engine_class: string;
    engine_method: string;
    required_context: string[];
    output_type: string;
    output_schema?: Record<string, unknown>;
    extra_inputs?: Record<string, unknown>;
}

export interface ManifestCategory {
    key: string;
    label: string;
    icon: string;
    group: string;
    description: string;
    functions: ManifestFunction[];
}

export interface Manifest {
    format_key: string;
    format_label: string;
    format_icon: string;
    context_fields: Record<string, ContextField>;
    categories: ManifestCategory[];
    output_types: string[];
}

export interface HealthStatus {
    status: string;
    formats_loaded: string[];
    total_matches: Record<string, number>;
}

export interface VenueItem {
    id: string;
    label: string;
}

export interface ExecuteResponse {
    function_key: string;
    output_type: string;
    data: unknown;
    metadata: Record<string, string>;
}

// ── API Functions ───────────────────────────────────────────────────────

export async function fetchHealth(): Promise<HealthStatus> {
    const res = await fetch(`${API_BASE}/health`);
    if (!res.ok) throw new Error(`Health check failed: ${res.status}`);
    return res.json();
}

export async function fetchFormats(): Promise<FormatInfo[]> {
    const res = await fetch(`${API_BASE}/api/formats`);
    if (!res.ok) throw new Error(`Failed to fetch formats: ${res.status}`);
    return res.json();
}

export async function fetchManifest(formatKey: string): Promise<Manifest> {
    const res = await fetch(`${API_BASE}/api/${formatKey}/manifest`);
    if (!res.ok) throw new Error(`Failed to fetch manifest for ${formatKey}: ${res.status}`);
    return res.json();
}

export async function fetchTeams(formatKey: string): Promise<string[]> {
    const res = await fetch(`${API_BASE}/api/${formatKey}/context/teams`);
    if (!res.ok) throw new Error(`Failed to fetch teams: ${res.status}`);
    const data = await res.json();
    return data.teams;
}

export async function fetchVenues(formatKey: string): Promise<VenueItem[]> {
    const res = await fetch(`${API_BASE}/api/${formatKey}/context/venues`);
    if (!res.ok) throw new Error(`Failed to fetch venues: ${res.status}`);
    const data = await res.json();
    return data.venues;
}

export async function fetchPlayers(formatKey: string, team: string): Promise<string[]> {
    const res = await fetch(`${API_BASE}/api/${formatKey}/context/players/${encodeURIComponent(team)}`);
    if (!res.ok) throw new Error(`Failed to fetch players for ${team}: ${res.status}`);
    const data = await res.json();
    return data.players;
}

export async function fetchRegions(formatKey: string): Promise<string[]> {
    const res = await fetch(`${API_BASE}/api/${formatKey}/context/regions`);
    if (!res.ok) throw new Error(`Failed to fetch regions: ${res.status}`);
    const data = await res.json();
    return data.regions;
}

export async function executeFunction(
    formatKey: string,
    functionKey: string,
    params: Record<string, unknown>
): Promise<ExecuteResponse> {
    const res = await fetch(`${API_BASE}/api/${formatKey}/execute/${functionKey}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ params }),
    });
    if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: res.statusText }));
        throw new Error(err.detail || `Execute failed: ${res.status}`);
    }
    return res.json();
}
