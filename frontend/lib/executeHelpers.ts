export type ExtraInputFieldConfig = {
    type: string;
    label: string;
    required?: boolean;
    source?: string;
};

export type SquadBuilderConfig = {
    enabled: boolean;
    maxPlayers: number;
};

function isRecord(value: unknown): value is Record<string, unknown> {
    return Boolean(value) && typeof value === "object" && !Array.isArray(value);
}

function isExtraInputFieldConfig(value: unknown): value is ExtraInputFieldConfig {
    if (!isRecord(value)) return false;
    return typeof value.type === "string" && typeof value.label === "string";
}

export function parsePositiveInteger(value: unknown): number | null {
    if (typeof value === "number" && Number.isInteger(value) && value > 0) return value;
    if (typeof value === "string") {
        const trimmed = value.trim();
        if (!trimmed) return null;
        const parsed = Number(trimmed);
        if (Number.isInteger(parsed) && parsed > 0) return parsed;
    }
    return null;
}

export function resolveSquadBuilderConfig(extraInputs: unknown): SquadBuilderConfig {
    const defaultConfig: SquadBuilderConfig = { enabled: false, maxPlayers: 11 };
    if (!isRecord(extraInputs)) return defaultConfig;

    const rawSquadBuilder = extraInputs.squad_builder;
    if (rawSquadBuilder === undefined || rawSquadBuilder === null || rawSquadBuilder === false) {
        return defaultConfig;
    }

    const fallbackMaxPlayers =
        parsePositiveInteger(extraInputs.squad_max_players) ??
        parsePositiveInteger(extraInputs.max_players) ??
        parsePositiveInteger(extraInputs.max_xi) ??
        defaultConfig.maxPlayers;

    if (rawSquadBuilder === true) {
        return { enabled: true, maxPlayers: fallbackMaxPlayers };
    }

    if (isRecord(rawSquadBuilder)) {
        const enabled = typeof rawSquadBuilder.enabled === "boolean" ? rawSquadBuilder.enabled : true;
        const maxPlayers =
            parsePositiveInteger(rawSquadBuilder.max_players) ??
            parsePositiveInteger(rawSquadBuilder.squad_max_players) ??
            parsePositiveInteger(rawSquadBuilder.max_xi) ??
            fallbackMaxPlayers;
        return { enabled, maxPlayers };
    }

    return { enabled: Boolean(rawSquadBuilder), maxPlayers: fallbackMaxPlayers };
}

export function getExtraInputFields(extraInputs: unknown): Record<string, ExtraInputFieldConfig> {
    if (!isRecord(extraInputs)) return {};
    const fields: Record<string, ExtraInputFieldConfig> = {};

    for (const [key, raw] of Object.entries(extraInputs)) {
        if (key === "squad_builder") continue;
        if (isExtraInputFieldConfig(raw)) {
            fields[key] = raw;
        }
    }

    return fields;
}

export function getMissingContext(
    requiredContext: string[],
    contextValues: Record<string, string | number>
): string[] {
    return requiredContext.filter((key) => {
        const val = contextValues[key];
        return !val || val === "" || val === "All";
    });
}

export function buildExecuteParams(args: {
    requiredContext: string[];
    contextValues: Record<string, string | number>;
    needsSquadBuilder: boolean;
    homeXI: string[];
    awayXI: string[];
    extraInputValues: Record<string, string>;
}): Record<string, unknown> {
    const {
        requiredContext,
        contextValues,
        needsSquadBuilder,
        homeXI,
        awayXI,
        extraInputValues,
    } = args;

    const params: Record<string, unknown> = {};

    for (const key of requiredContext) {
        const val = contextValues[key];
        if (val && val !== "" && val !== "All") {
            params[key] = val;
        }
    }

    if (needsSquadBuilder) {
        params.home_xi = homeXI;
        params.away_xi = awayXI;
    }

    Object.entries(extraInputValues).forEach(([key, val]) => {
        if (val) params[key] = val;
    });

    return params;
}

export function formatExecuteError(err: unknown): string {
    const fallback = "Execution failed. Please try again.";
    if (!(err instanceof Error)) return fallback;

    const maybeStatus = (err as Error & { status?: number }).status;
    const message = err.message?.trim();
    if (message && !message.startsWith("[") && !message.startsWith("{")) {
        return message;
    }

    if (maybeStatus === 422) {
        return "Validation Error: Please verify the selected context and required inputs.";
    }
    if (typeof maybeStatus === "number" && maybeStatus >= 500) {
        return "Server Error: Backend execution failed. Please retry in a moment.";
    }
    return fallback;
}
