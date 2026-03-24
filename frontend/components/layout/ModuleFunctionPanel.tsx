"use client";

import { useState, useCallback, useMemo } from "react";
import { useSearchParams } from "next/navigation";
import { Zap } from "lucide-react";
import { useAppContext } from "@/lib/context";
import { executeFunction, type ManifestFunction, type ExecuteResponse } from "@/lib/api";
import { Button } from "@/components/common/Button";
import {
    resolveSquadBuilderConfig,
    getExtraInputFields,
    getMissingContext,
    buildExecuteParams,
    formatExecuteError,
} from "@/lib/executeHelpers";
import { PreExecPanel } from "./PreExecPanel";
import { PostExecPanel } from "./PostExecPanel";

// ── Types ─────────────────────────────────────────────────────────────

interface ModuleFunctionPanelProps {
    activeFn: ManifestFunction;
}

// ── Execute Error Banner ──────────────────────────────────────────────

function ExecuteError({ error, onRetry }: { error: string; onRetry: () => void }) {
    return (
        <div role="alert" className="module-error animate-fade-in">
            <p className="module-error-title">Execution Failed</p>
            <p className="module-error-body">{error}</p>
            <Button variant="ghost" onClick={onRetry} aria-label="Retry execution">
                <Zap size={14} />
                Retry
            </Button>
        </div>
    );
}

// ── Module Function Panel (orchestrator) ──────────────────────────────
// Keyed by activeFn.key from parent — state auto-resets on tab change.

export function ModuleFunctionPanel({ activeFn }: ModuleFunctionPanelProps) {
    const { manifest, activeFormat, venues } = useAppContext();
    const searchParams = useSearchParams();

    const contextValues = useMemo<Record<string, string>>(() => {
        if (!manifest) return {};
        return Object.fromEntries(
            Object.keys(manifest.context_fields).map((k) => [k, searchParams.get(k) ?? ""])
        );
    }, [manifest, searchParams]);

    const [result, setResult] = useState<ExecuteResponse | null>(null);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [homeXI, setHomeXI] = useState<string[]>([]);
    const [awayXI, setAwayXI] = useState<string[]>([]);
    const [extraInputValues, setExtraInputValues] = useState<Record<string, string>>({});
    const [activeView, setActiveView] = useState<string>("");

    const squadConfig = useMemo(() => resolveSquadBuilderConfig(activeFn.extra_inputs), [activeFn.extra_inputs]);
    const extraFields = useMemo(() => getExtraInputFields(activeFn.extra_inputs), [activeFn.extra_inputs]);
    const missingContext = useMemo(() => getMissingContext(activeFn.required_context, contextValues), [activeFn.required_context, contextValues]);
    const missingInputLabels = useMemo(
        () => Object.entries(extraFields)
            .filter(([key, field]) => Boolean(field.required) && !extraInputValues[key])
            .map(([, field]) => field.label),
        [extraFields, extraInputValues]
    );

    const canExecute = missingContext.length === 0;
    const squadReady = !squadConfig.enabled || (homeXI.length > 0 && awayXI.length > 0);
    const canRun = canExecute && squadReady && missingInputLabels.length === 0;

    const getContextLabel = useCallback(
        (key: string) => manifest?.context_fields?.[key]?.label ?? key.replace(/_/g, " "),
        [manifest]
    );

    const handleExtraInputChange = useCallback(
        (key: string, val: string) => setExtraInputValues((prev) => ({ ...prev, [key]: val })),
        []
    );

    const runExecute = useCallback(async (view = "") => {
        if (!activeFormat) return;
        setIsLoading(true);
        setError(null);
        setResult(null);
        if (view) setActiveView(view);

        try {
            const params = buildExecuteParams({
                requiredContext: activeFn.required_context,
                optionalContext: activeFn.optional_context ?? [],
                contextValues,
                needsSquadBuilder: squadConfig.enabled,
                homeXI,
                awayXI,
                extraInputValues,
            });
            const res = await executeFunction(activeFormat, activeFn.key, params);

            if (view) {
                const venueLabel = venues.find((v) => v.id === extraInputValues["venue_id"])?.label ?? "";
                const rawData =
                    typeof res.data === "object" && res.data !== null && !Array.isArray(res.data)
                        ? (res.data as Record<string, unknown>)
                        : {};
                setResult({ ...res, data: { ...rawData, _view: view, _venue_label: venueLabel, _years_input: extraInputValues["years"] ?? "" } });
            } else {
                setResult(res);
            }
        } catch (err) {
            setError(formatExecuteError(err));
        } finally {
            setIsLoading(false);
        }
    }, [activeFormat, activeFn, contextValues, squadConfig.enabled, homeXI, awayXI, extraInputValues, venues]);

    const execHint = !canExecute
        ? `Select ${missingContext.map(getContextLabel).join(" and ")} in the Context Bar to enable`
        : !squadReady
        ? "Select both squads to continue"
        : missingInputLabels.length > 0
        ? `Select ${missingInputLabels[0]} to continue`
        : "";

    const sharedProps = {
        activeFn,
        contextValues,
        extraFields,
        squadConfig,
        isLoading,
        canRun,
        activeView,
        homeXI,
        awayXI,
        extraInputValues,
        onExtraInputChange: handleExtraInputChange,
        onHomeXIChange: setHomeXI,
        onAwayXIChange: setAwayXI,
        onExecute: runExecute,
        activeFormat: activeFormat ?? "",
    };

    return (
        <div className="module-panel animate-fade-in">

            {!result && !isLoading && (
                <PreExecPanel {...sharedProps} execHint={execHint} getContextLabel={getContextLabel} />
            )}

            {result !== null && (
                <PostExecPanel {...sharedProps} result={result} />
            )}

            {error && (
                <ExecuteError error={error} onRetry={() => runExecute(activeView)} />
            )}

            {isLoading && (
                <div
                    className="skeleton module-result-skeleton"
                    role="status"
                    aria-live="polite"
                    aria-label="Loading analysis results"
                />
            )}
        </div>
    );
}
