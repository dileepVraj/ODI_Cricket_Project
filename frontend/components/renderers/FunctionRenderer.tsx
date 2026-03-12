"use client";

import { lazy, Suspense, type ReactNode } from "react";
import { ErrorBoundary } from "@/components/common/ErrorBoundary";
import { isJsonRecordArray } from "@/lib/types";

const EmptyState = lazy(() => import("@/components/common/EmptyState"));
const FallbackBanner = lazy(() => import("@/components/common/FallbackBanner"));
const DataTable = lazy(() => import("./DataTable"));
const ComparisonTable = lazy(() => import("./ComparisonTable"));
const MatrixTable = lazy(() => import("./MatrixTable"));
const FormTable = lazy(() => import("./FormTable"));
const ReportCard = lazy(() => import("./ReportCard"));
const PredictionCard = lazy(() => import("./PredictionCard"));
const PlayerProfileCard = lazy(() => import("./PlayerProfileCard"));
const MatchupTable = lazy(() => import("./MatchupTable"));
const DownloadPanel = lazy(() => import("./DownloadPanel"));
const PhaseAnalysisCard = lazy(() => import("./PhaseAnalysisCard"));
const VenueMatchupReport = lazy(() => import("./VenueMatchupReport"));
const CountryH2HReport = lazy(() => import("./CountryH2HReport"));
const FortressReport = lazy(() => import("./FortressReport"));
const MatchAuditSection = lazy(() => import("./MatchAuditSection"));

interface FunctionRendererProps {
    outputType: string;
    data: unknown;
}

type JsonRecord = Record<string, unknown>;
type JsonRecordArray = JsonRecord[];

interface EnrichedDataResult {
    mainData: unknown;
    matchAudit: JsonRecordArray | null;
}

function isJsonRecord(value: unknown): value is JsonRecord {
    return typeof value === "object" && value !== null && !Array.isArray(value);
}

function extractEnrichedData(data: unknown): EnrichedDataResult {
    if (isJsonRecord(data)) {
        const stats = data.stats;
        const matchAudit = isJsonRecordArray(data.match_audit) ? data.match_audit : null;

        if (isJsonRecordArray(stats)) {
            return {
                mainData: stats,
                matchAudit,
            };
        }

        if ("match_audit" in data) {
            return {
                mainData: data,
                matchAudit,
            };
        }
    }

    return { mainData: data, matchAudit: null };
}

function wrapRenderer(renderer: ReactNode, fallbackMessage: string): ReactNode {
    return (
        <ErrorBoundary fallbackMessage={fallbackMessage}>
            {renderer}
        </ErrorBoundary>
    );
}

function renderMatchAudit(matchAudit: JsonRecordArray | null): ReactNode {
    if (!matchAudit) return null;

    return wrapRenderer(
        <MatchAuditSection records={matchAudit} />,
        "Unable to render match audit."
    );
}

function getSuspenseFallback(): ReactNode {
    return (
        <div className="skeleton" aria-hidden="true">
            &nbsp;
        </div>
    );
}

export default function FunctionRenderer({ outputType, data }: FunctionRendererProps) {
    if (data === null || data === undefined) {
        return (
            <Suspense fallback={<div className="skeleton [height:2rem]" />}>
                <EmptyState
                    title="No Analysis Data"
                    message="The engine returned no data for this query. This might be due to insufficient matches or missing context."
                    actionLabel="Try adjusting filters"
                />
            </Suspense>
        );
    }

    const { mainData, matchAudit } = extractEnrichedData(data);
    let renderedOutput: ReactNode | null = null;

    switch (outputType) {
        case "report":
            if (isJsonRecord(mainData)) {
                renderedOutput = (
                    <>
                        {wrapRenderer(
                            <ReportCard data={mainData} />,
                            "Unable to render report output."
                        )}
                        {renderMatchAudit(matchAudit)}
                    </>
                );
            } else if (isJsonRecordArray(mainData)) {
                renderedOutput = (
                    <>
                        {wrapRenderer(
                            <DataTable data={mainData} />,
                            "Unable to render table output."
                        )}
                        {renderMatchAudit(matchAudit)}
                    </>
                );
            }
            break;
        case "comparison_table":
            if (isJsonRecordArray(mainData)) {
                renderedOutput = (
                    <>
                        {wrapRenderer(
                            <ComparisonTable data={mainData} />,
                            "Unable to render comparison table."
                        )}
                        {renderMatchAudit(matchAudit)}
                    </>
                );
            }
            break;
        case "matrix_table":
            if (isJsonRecordArray(mainData)) {
                renderedOutput = (
                    <>
                        {wrapRenderer(
                            <MatrixTable data={mainData} />,
                            "Unable to render matrix table."
                        )}
                        {renderMatchAudit(matchAudit)}
                    </>
                );
            }
            break;
        case "form_table":
            if (isJsonRecordArray(mainData)) {
                renderedOutput = wrapRenderer(
                    <FormTable data={mainData} />,
                    "Unable to render form table."
                );
            }
            break;
        case "table":
            if (isJsonRecordArray(mainData)) {
                renderedOutput = (
                    <>
                        {wrapRenderer(
                            <DataTable data={mainData} />,
                            "Unable to render table output."
                        )}
                        {renderMatchAudit(matchAudit)}
                    </>
                );
            }
            break;
        case "phase_analysis":
            if (isJsonRecord(mainData)) {
                renderedOutput = wrapRenderer(
                    <PhaseAnalysisCard data={mainData} />,
                    "Unable to render phase analysis."
                );
            }
            break;
        case "venue_matchup_report":
            if (isJsonRecord(mainData)) {
                renderedOutput = (
                    <>
                        {wrapRenderer(
                            <VenueMatchupReport data={mainData} />,
                            "Unable to render venue matchup report."
                        )}
                        {renderMatchAudit(matchAudit)}
                    </>
                );
            }
            break;
        case "country_h2h_report":
            if (isJsonRecord(mainData)) {
                renderedOutput = (
                    <>
                        {wrapRenderer(
                            <CountryH2HReport data={mainData} />,
                            "Unable to render country H2H report."
                        )}
                        {renderMatchAudit(matchAudit)}
                    </>
                );
            }
            break;
        case "home_fortress":
            if (isJsonRecord(mainData)) {
                renderedOutput = (
                    <>
                        {wrapRenderer(
                            <FortressReport data={mainData} />,
                            "Unable to render fortress report."
                        )}
                        {renderMatchAudit(matchAudit)}
                    </>
                );
            }
            break;
        case "prediction_card":
            if (isJsonRecord(mainData)) {
                renderedOutput = wrapRenderer(
                    <PredictionCard data={mainData} />,
                    "Unable to render prediction card."
                );
            }
            break;
        case "profile_card":
            if (isJsonRecord(mainData)) {
                renderedOutput = wrapRenderer(
                    <PlayerProfileCard data={mainData} />,
                    "Unable to render profile card."
                );
            }
            break;
        case "matchup_table":
            if (isJsonRecordArray(mainData)) {
                renderedOutput = wrapRenderer(
                    <MatchupTable data={mainData} />,
                    "Unable to render matchup table."
                );
            }
            break;
        case "download_json":
            if (isJsonRecord(mainData)) {
                renderedOutput = wrapRenderer(
                    <DownloadPanel data={mainData} />,
                    "Unable to render download panel."
                );
            }
            break;
    }

    if (!renderedOutput) {
        if (isJsonRecordArray(mainData)) {
            renderedOutput = (
                <div>
                    <FallbackBanner message="Unknown renderer" />
                    {wrapRenderer(
                        <DataTable data={mainData} />,
                        "Unable to render fallback table output."
                    )}
                    {renderMatchAudit(matchAudit)}
                </div>
            );
        } else if (isJsonRecord(mainData)) {
            renderedOutput = (
                <div>
                    <FallbackBanner message="Unknown renderer" />
                    {wrapRenderer(
                        <ReportCard data={mainData} />,
                        "Unable to render fallback report output."
                    )}
                    {renderMatchAudit(matchAudit)}
                </div>
            );
        } else {
            renderedOutput = (
                <div>
                    <FallbackBanner message="Unknown renderer" />
                    <pre className="[background:var(--bg-elevated)] [padding:16px] [border-radius:var(--radius-md)] [font-size:0.8rem] [color:var(--text-secondary)] [overflow:auto] [max-height:400px] [border:1px_solid_var(--border-subtle)]">
                        {JSON.stringify(data, null, 2)}
                    </pre>
                </div>
            );
        }
    }

    return (
        <Suspense fallback={getSuspenseFallback()}>
            {renderedOutput}
        </Suspense>
    );
}
