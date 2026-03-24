"use client";

import { Lock, TrendingUp, Zap } from "lucide-react";
import { type ManifestFunction } from "@/lib/api";
import { type ExtraInputFieldConfig, type SquadBuilderConfig } from "@/lib/executeHelpers";
import { Button } from "@/components/common/Button";
import ExtraInputRenderer from "@/components/inputs/ExtraInputRenderer";
import SquadBuilder from "@/components/inputs/SquadBuilder";

interface PreExecPanelProps {
    activeFn: ManifestFunction;
    contextValues: Record<string, string>;
    extraFields: Record<string, ExtraInputFieldConfig>;
    squadConfig: SquadBuilderConfig;
    canRun: boolean;
    isLoading: boolean;
    activeView: string;
    homeXI: string[];
    awayXI: string[];
    extraInputValues: Record<string, string>;
    onExtraInputChange: (key: string, val: string) => void;
    onHomeXIChange: (players: string[]) => void;
    onAwayXIChange: (players: string[]) => void;
    onExecute: (view?: string) => void;
    execHint: string;
    getContextLabel: (key: string) => string;
    activeFormat: string;
}

export function PreExecPanel({
    activeFn,
    contextValues,
    extraFields,
    squadConfig,
    canRun,
    isLoading,
    activeView,
    homeXI,
    awayXI,
    extraInputValues,
    onExtraInputChange,
    onHomeXIChange,
    onAwayXIChange,
    onExecute,
    execHint,
    getContextLabel,
    activeFormat,
}: PreExecPanelProps) {
    const executeBtns = activeFn.execute_buttons ?? [];
    const hasMultiButtons = executeBtns.length > 0;

    return (
        <div className="pre-exec-card animate-fade-in">

            {/* NEEDED TO RUN */}
            <div>
                <div className="pre-exec-section-label">
                    <Lock size={11} aria-hidden="true" />
                    Needed to run
                </div>
                <div className="pre-exec-chips">
                    {activeFn.required_context.map((key) => {
                        const val = contextValues[key];
                        const isFilled = Boolean(val && val !== "" && val !== "All");
                        return (
                            <span
                                key={key}
                                className={`pre-exec-chip${isFilled ? " pre-exec-chip-filled" : ""}`}
                            >
                                {getContextLabel(key)}
                            </span>
                        );
                    })}
                    {Object.entries(extraFields)
                        .filter(([, field]) => Boolean(field.required))
                        .map(([key, field]) => {
                            const isFilled = Boolean(extraInputValues[key]);
                            return (
                                <span
                                    key={key}
                                    className={`pre-exec-chip${isFilled ? " pre-exec-chip-filled" : ""}`}
                                >
                                    {field.label}
                                </span>
                            );
                        })}
                </div>

                {Object.keys(extraFields).length > 0 && (
                    <div className="pre-exec-inputs">
                        <ExtraInputRenderer
                            formatKey={activeFormat}
                            extraInputs={extraFields}
                            contextValues={contextValues}
                            values={extraInputValues}
                            onChange={onExtraInputChange}
                        />
                    </div>
                )}

                {squadConfig.enabled && (
                    <div className="pre-exec-inputs">
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
                    </div>
                )}
            </div>

            <div className="pre-exec-divider" />

            {/* WHAT YOU'LL DISCOVER */}
            <div>
                <div className="pre-exec-section-label">
                    <TrendingUp size={11} aria-hidden="true" />
                    What you&apos;ll discover
                </div>
                {activeFn.discover_bullets && activeFn.discover_bullets.length > 0 ? (
                    <ul className="pre-exec-bullets" aria-label="Analysis insights">
                        {activeFn.discover_bullets.map((bullet, i) => (
                            <li key={i} className="pre-exec-bullet">
                                <span className="pre-exec-bullet-dot" aria-hidden="true" />
                                {bullet}
                            </li>
                        ))}
                    </ul>
                ) : (
                    <p className="pre-exec-hint">
                        Configure the required inputs above and execute to uncover insights for this analysis.
                    </p>
                )}
            </div>

            <div className="pre-exec-divider" />

            {/* EXECUTE FOOTER */}
            <div className="pre-exec-footer">
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
                        variant="primary"
                        isLoading={false}
                        disabled={!canRun}
                        onClick={() => onExecute()}
                        aria-label={canRun ? "Execute analysis" : "Fill required context to execute"}
                    >
                        <Zap size={14} />
                        Execute Analysis
                    </Button>
                )}
                {execHint && <span className="pre-exec-hint">{execHint}</span>}
            </div>
        </div>
    );
}
