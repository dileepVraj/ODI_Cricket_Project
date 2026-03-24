"use client";

import { Zap } from "lucide-react";
import { type ManifestFunction, type ExecuteResponse } from "@/lib/api";
import { type ExtraInputFieldConfig, type SquadBuilderConfig } from "@/lib/executeHelpers";
import { Button } from "@/components/common/Button";
import { ErrorBoundary } from "@/components/common/ErrorBoundary";
import FunctionRenderer from "@/components/renderers/FunctionRenderer";
import ExtraInputRenderer from "@/components/inputs/ExtraInputRenderer";
import SquadBuilder from "@/components/inputs/SquadBuilder";

interface PostExecPanelProps {
    activeFn: ManifestFunction;
    contextValues: Record<string, string>;
    extraFields: Record<string, ExtraInputFieldConfig>;
    squadConfig: SquadBuilderConfig;
    isLoading: boolean;
    canRun: boolean;
    activeView: string;
    homeXI: string[];
    awayXI: string[];
    extraInputValues: Record<string, string>;
    onExtraInputChange: (key: string, val: string) => void;
    onHomeXIChange: (players: string[]) => void;
    onAwayXIChange: (players: string[]) => void;
    onExecute: (view?: string) => void;
    result: ExecuteResponse;
    activeFormat: string;
}

export function PostExecPanel({
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
    onExtraInputChange,
    onHomeXIChange,
    onAwayXIChange,
    onExecute,
    result,
    activeFormat,
}: PostExecPanelProps) {
    const executeBtns = activeFn.execute_buttons ?? [];
    const hasMultiButtons = executeBtns.length > 0;

    return (
        <>
            {Object.keys(extraFields).length > 0 && (
                <ExtraInputRenderer
                    formatKey={activeFormat}
                    extraInputs={extraFields}
                    contextValues={contextValues}
                    values={extraInputValues}
                    onChange={onExtraInputChange}
                />
            )}

            {squadConfig.enabled && (
                <SquadBuilder
                    formatKey={activeFormat}
                    teamA={contextValues.team_a ?? ""}
                    teamB={contextValues.team_b ?? ""}
                    maxPlayers={squadConfig.maxPlayers}
                    homeXI={homeXI}
                    awayXI={awayXI}
                    onHomeXIChange={onHomeXIChange}
                    onAwayXIChange={onAwayXIChange}
                />
            )}

            <div className="module-execute-row">
                {hasMultiButtons ? (
                    executeBtns.map((btn) => (
                        <Button
                            key={btn.key}
                            variant="primary"
                            isLoading={isLoading && activeView === btn.key}
                            loadingLabel="Analysing..."
                            disabled={isLoading || !canRun}
                            onClick={() => onExecute(btn.key)}
                            aria-label={`Execute ${btn.label} analysis`}
                        >
                            <Zap size={14} />
                            {btn.label}
                        </Button>
                    ))
                ) : (
                    <Button
                        variant="ghost"
                        isLoading={isLoading}
                        loadingLabel="Analysing..."
                        disabled={isLoading || !canRun}
                        onClick={() => onExecute()}
                        aria-label="Re-run analysis"
                    >
                        <Zap size={14} />
                        Re-run Analysis
                    </Button>
                )}
            </div>

            {/* Results */}
            {!isLoading && (
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
        </>
    );
}
