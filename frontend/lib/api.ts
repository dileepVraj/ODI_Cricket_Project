/**
 * lib/api.ts — API Client for the Cricket Algo-Trading Platform
 * 
 * Centralized API layer. All components call these functions
 * instead of raw fetch() — single source of truth for API URLs.
 */

const API_BASE = "";  // Empty = same origin (proxied by Next.js rewrites)

type ApiErrorCode = "validation" | "server" | "http" | "network";

export class ApiClientError extends Error {
    status: number;
    code: ApiErrorCode;
    details?: unknown;

    constructor(message: string, status: number, code: ApiErrorCode, details?: unknown) {
        super(message);
        this.name = "ApiClientError";
        this.status = status;
        this.code = code;
        this.details = details;
    }
}

// ── Types ───────────────────────────────────────────────────────────────

export interface FormatInfo {
    key: string;
    label: string;
    icon: string;
    has_manifest: boolean;
}

export interface SourceRegistryEntry {
    path: string;
    preload: boolean;
}

export interface NavigationRoot {
    key: string;
    label: string;
    icon: string;
}

export interface QuickLink {
    label: string;
    category_key: string;
}

export interface ContextField {
    type: "combobox" | "dropdown" | "slider" | "text" | "textarea";
    label: string;
    required: boolean;
    source?: string;
    source_params?: Record<string, string | number>;
    options?: string[];
    min?: number;
    max?: number;
    default?: number;
    placeholder?: string;
}

export interface ManifestFunction {
    key: string;
    label: string;
    icon: string;
    engine_class: string;
    engine_method: string;
    required_context: string[];
    optional_context?: string[];
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
    quick_links?: QuickLink[];
}

export interface Manifest {
    format_key: string;
    format_label: string;
    format_icon: string;
    context_fields: Record<string, ContextField>;
    categories: ManifestCategory[];
    output_types: string[];
    source_registry?: Record<string, SourceRegistryEntry>;
    navigation_root?: NavigationRoot;
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

function getErrorCode(status: number): ApiErrorCode {
    if (status === 422) return "validation";
    if (status >= 500) return "server";
    return "http";
}

function toUserMessage(status: number, statusText: string, payload: unknown): string {
    const defaultText = statusText || "Request failed";
    let detail: unknown = payload;

    if (payload && typeof payload === "object" && "detail" in (payload as Record<string, unknown>)) {
        detail = (payload as Record<string, unknown>).detail;
    }

    const normalizeDetail = (value: unknown): string | null => {
        if (typeof value === "string" && value.trim()) {
            return value.trim();
        }

        if (Array.isArray(value) && value.length > 0) {
            const pieces = value
                .map((item) => {
                    if (!item || typeof item !== "object") return String(item ?? "").trim();
                    const obj = item as Record<string, unknown>;
                    const msg = typeof obj.msg === "string"
                        ? obj.msg
                        : typeof obj.message === "string"
                            ? obj.message
                            : "";
                    const loc = Array.isArray(obj.loc)
                        ? obj.loc
                            .map((part) => String(part))
                            .filter((part) => part !== "body" && part !== "params")
                            .join(" > ")
                        : "";
                    if (loc && msg) return `${loc}: ${msg}`;
                    return msg || JSON.stringify(obj);
                })
                .filter((part) => part && part !== "undefined");
            if (pieces.length > 0) return pieces.join("; ");
        }

        if (value && typeof value === "object") {
            const obj = value as Record<string, unknown>;
            if (typeof obj.message === "string" && obj.message.trim()) {
                return obj.message.trim();
            }
        }

        return null;
    };

    const detailText = normalizeDetail(detail) || defaultText;

    if (status === 422) return `Validation Error: ${detailText}`;
    if (status >= 500) return `Server Error: ${detailText}`;
    return `Request Error: ${detailText}`;
}

async function parseErrorPayload(res: Response): Promise<unknown> {
    try {
        return await res.json();
    } catch {
        try {
            const text = await res.text();
            return text || res.statusText;
        } catch {
            return res.statusText;
        }
    }
}

async function requestJson<T>(path: string, init?: RequestInit): Promise<T> {
    let res: Response;
    try {
        res = await fetch(`${API_BASE}${path}`, init);
    } catch {
        throw new ApiClientError(
            "Network Error: Could not reach the backend service.",
            0,
            "network"
        );
    }

    if (!res.ok) {
        const payload = await parseErrorPayload(res);
        const message = toUserMessage(res.status, res.statusText, payload);
        throw new ApiClientError(message, res.status, getErrorCode(res.status), payload);
    }

    return res.json() as Promise<T>;
}

export async function fetchHealth(): Promise<HealthStatus> {
    return requestJson<HealthStatus>("/health");
}

export async function fetchFormats(): Promise<FormatInfo[]> {
    return requestJson<FormatInfo[]>("/api/v1/formats");
}

export async function fetchManifest(formatKey: string): Promise<Manifest> {
    return requestJson<Manifest>(`/api/v1/${formatKey}/manifest`);
}

export async function fetchTeams(formatKey: string): Promise<string[]> {
    const data = await requestJson<{ teams: string[] }>(`/api/v1/${formatKey}/context/teams`);
    return data.teams;
}

export async function fetchVenues(formatKey: string): Promise<VenueItem[]> {
    const data = await requestJson<{ venues: VenueItem[] }>(`/api/v1/${formatKey}/context/venues`);
    return data.venues;
}

export async function fetchPlayers(formatKey: string, team: string): Promise<string[]> {
    const data = await requestJson<{ players: string[] }>(
        `/api/v1/${formatKey}/context/players/${encodeURIComponent(team)}`
    );
    return data.players;
}

export async function fetchRegions(formatKey: string): Promise<string[]> {
    const data = await requestJson<{ regions: string[] }>(`/api/v1/${formatKey}/context/regions`);
    return data.regions;
}

export async function fetchHostCountries(formatKey: string): Promise<string[]> {
    const data = await requestJson<{ countries: string[] }>(`/api/v1/${formatKey}/context/host_countries`);
    return data.countries;
}

export async function executeFunction(
    formatKey: string,
    functionKey: string,
    params: Record<string, unknown>
): Promise<ExecuteResponse> {
    return requestJson<ExecuteResponse>(`/api/v1/${formatKey}/execute/${functionKey}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ params }),
    });
}
