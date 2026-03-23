"use client";

import { useState, useCallback, useMemo } from "react";
import { useSearchParams } from "next/navigation";
import { Zap } from "lucide-react";
import { useAppContext } from "@/lib/context";
import { executeFunction, type ManifestFunction, type ExecuteResponse } from "@/lib/api";
import { Button } from "@/components/common/Button";
import { FilterNotice } from "@/components/common/FilterNotice";
import { ErrorBoundary } from "@/components/common/ErrorBoundary";
import FunctionRenderer from "@/components/renderers/FunctionRenderer";
import ExtraInputRenderer from "@/components/inputs/ExtraInputRenderer";
import SquadBuilder from "@/components/inputs/SquadBuilder";
import {
    resolveSquadBuilderConfig,
    getExtraInputFields,
    getMissingContext,
    buildExecuteParams,
    formatExecuteError,
} from "@/lib/executeHelpers";

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

// ── Module Function Panel ─────────────────────────────────────────────
// Keyed by activeFn.key from parent — state auto-resets on tab change.

export function ModuleFunctionPanel({ activeFn }: ModuleFunctionPanelProps) {
    const { manifest, activeFormat, venues } = useAppContext();
    const searchParams = useSearchParams();

    // Context values live in URL search params (managed by ContextBar)
    const contextValues = useMemo<Record<string, string>>(() => {
        if (!manifest) return {};
        return Object.fromEntries(
            Object.keys(manifest.context_fields).map((k) => [k, searchParams.get(k) ?? ""])
        );
    }, [manifest, searchParams]);

    // Local UI state — strictly UI concerns only
    const [result, setResult] = useState<ExecuteResponse | null>(null);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [homeXI, setHomeXI] = useState<string[]>([]);
    const [awayXI, setAwayXI] = useState<string[]>([]);
    const [extraInputValues, setExtraInputValues] = useState<Record<string, string>>({});
    const [activeView, setActiveView] = useState<string>("");

    // Derived readiness
    const squadConfig = useMemo(
        () => resolveSquadBuilderConfig(activeFn.extra_inputs),
        [activeFn.extra_inputs]
    );
    const extraFields = useMemo(
        () => getExtraInputFields(activeFn.extra_inputs),
        [activeFn.extra_inputs]
    );
    const missingContext = useMemo(
        () => getMissingContext(activeFn.required_context, contextValues),
        [activeFn.required_context, contextValues]
    );
    const missingInputLabels = useMemo(
        () => Object.entries(extraFields)
            .filter(([key, field]) => Boolean(field.required) && !extraInputValues[key])
            .map(([, field]) => field.label),
        [extraFields, extraInputValues]
    );

    const canExecute = missingContext.length === 0;
    const squadReady = !squadConfig.enabled || (homeXI.length > 0 && awayXI.length > 0);
    const canRun = canExecute && squadReady && missingInputLabels.length === 0;

    const executeBtns = activeFn.execute_buttons ?? [];
    const hasMultiButtons = executeBtns.length > 0;

    const getContextLabel = useCallback(
        (key: string) => manifest?.context_fields?.[key]?.label ?? key.replace(/_/g, " "),
        [manifest]
    );

    // Execute handler — not a useEffect, so no cancellation guard needed
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
                setResult({
                    ...res,
                    data: {
                        ...rawData,
                        _view: view,
                        _venue_label: venueLabel,
                        _years_input: extraInputValues["years"] ?? "",
                    },
                });
            } else {
                setResult(res);
            }
        } catch (err) {
            setError(formatExecuteError(err));
        } finally {
            setIsLoading(false);
        }
    }, [activeFormat, activeFn, contextValues, squadConfig.enabled, homeXI, awayXI, extraInputValues, venues]);

    return (
        <div className="module-panel animate-fade-in">

            {/* Missing context notice */}
            {!canExecute && (
                <FilterNotice label="Missing Required Context">
                    Please fill in the following fields in the Context Bar:{" "}
                    <strong>{missingContext.map(getContextLabel).join(", ")}</strong>
                </FilterNotice>
            )}

            {/* Extra inputs (venue, years, etc.) */}
            {Object.keys(extraFields).length > 0 && activeFormat && (
                <ExtraInputRenderer
                    formatKey={activeFormat}
                    extraInputs={extraFields}
                    contextValues={contextValues}
                    values={extraInputValues}
                    onChange={(key, val) =>
                        setExtraInputValues((prev) => ({ ...prev, [key]: val }))
                    }
                />
            )}

            {/* Squad builder */}
            {squadConfig.enabled && activeFormat && (
                <SquadBuilder
                    formatKey={activeFormat}
                    teamA={contextValues.team_a ?? ""}
                    teamB={contextValues.team_b ?? ""}
                    maxPlayers={squadConfig.maxPlayers}
                    homeXI={homeXI}
                    awayXI={awayXI}
                    onHomeXIChange={setHomeXI}
                    onAwayXIChange={setAwayXI}
                />
            )}

            {/* Execute button(s) */}
            <div className="module-execute-row">
                {hasMultiButtons ? (
                    executeBtns.map((btn) => (
                        <Button
                            key={btn.key}
                            variant="primary"
                            isLoading={isLoading && activeView === btn.key}
                            loadingLabel="Analysing..."
                            disabled={isLoading || !canRun}
                            onClick={() => runExecute(btn.key)}
                            aria-label={`Execute ${btn.label} analysis`}
                        >
                            <Zap size={14} />
                            {btn.label}
                        </Button>
                    ))
                ) : (
                    <Button
                        variant={result && !isLoading ? "ghost" : "primary"}
                        isLoading={isLoading}
                        loadingLabel="Analysing..."
                        disabled={isLoading || !canRun}
                        onClick={() => runExecute()}
                        aria-label={canRun ? "Execute analysis" : "Fill required context to execute"}
                    >
                        <Zap size={14} />
                        {!canRun
                            ? (!canExecute
                                ? "Fill Required Context"
                                : !squadReady
                                ? "Select Squads"
                                : `Missing ${missingInputLabels[0]}`)
                            : result
                            ? "Re-run Analysis"
                            : "Execute Analysis"}
                    </Button>
                )}
            </div>

            {/* Execution error */}
            {error && (
                <ExecuteError
                    error={error}
                    onRetry={() => runExecute(activeView)}
                />
            )}

            {/* Loading state */}
            {isLoading && (
                <div
                    className="skeleton module-result-skeleton"
                    role="status"
                    aria-live="polite"
                    aria-label="Loading analysis results"
                />
            )}

            {/* Results */}
            {result && !isLoading && (
                <div aria-live="polite" className="animate-fade-in">
                    <ErrorBoundary fallbackMessage="Failed to render analysis results.">
                        <FunctionRenderer
                            outputType={result.output_type}
                            data={result.data}
                            homeXI={homeXI}
                            awayXI={awayXI}
                            homeTeamName={contextValues.team_a ?? ""}
                            awayTeamName={contextValues.team_b ?? ""}
                        />
                    </ErrorBoundary>
                </div>
            )}
        </div>
    );
}
