/**
 * FunctionRenderer.tsx — The Universal Output Dispatcher
 * 
 * This is the SINGLE entry point for rendering ALL function outputs.
 * It reads the `output_type` from the manifest and dispatches to
 * the correct specialized renderer component.
 * 
 * Handles:
 *   - Loading/spinner state
 *   - Missing context alerts
 *   - API error display
 *   - Enriched data shapes (stats + match_audit from API enrichment)
 *   - Fallback for unknown output types (raw JSON)
 * 
 * Usage:
 *   <FunctionRenderer outputType="report" data={apiResponse.data} />
 */
"use client";

import DataTable from "./DataTable";
import ComparisonTable from "./ComparisonTable";
import MatrixTable from "./MatrixTable";
import FormTable from "./FormTable";
import ReportCard from "./ReportCard";
import PredictionCard from "./PredictionCard";
import PlayerProfileCard from "./PlayerProfileCard";
import MatchupTable from "./MatchupTable";
import DownloadPanel from "./DownloadPanel";
import PhaseAnalysisCard from "./PhaseAnalysisCard";
import VenueMatchupReport from "./VenueMatchupReport";
import MatchAuditSection from "./MatchAuditSection";
import EmptyState from "@/components/common/EmptyState";
import { AlertCircle } from "lucide-react";

interface FunctionRendererProps {
    outputType: string;
    data: unknown;
}

type VenueMatchupData = Parameters<typeof VenueMatchupReport>[0]["data"];

/**
 * Detects if the data has been enriched by the API's _enrich_with_match_audit.
 * Enriched comparison_table data looks like: { stats: [...], match_audit: [...] }
 * instead of the original raw array.
 */
function extractEnrichedData(data: unknown): {
    mainData: unknown;
    matchAudit: Record<string, unknown>[] | null;
} {
    if (
        typeof data === "object" &&
        data !== null &&
        !Array.isArray(data) &&
        "stats" in (data as Record<string, unknown>) &&
        Array.isArray((data as Record<string, unknown>)["stats"])
    ) {
        const obj = data as Record<string, unknown>;
        return {
            mainData: obj["stats"],
            matchAudit: Array.isArray(obj["match_audit"])
                ? (obj["match_audit"] as Record<string, unknown>[])
                : null,
        };
    }

    // Dict with match_audit (e.g., venue_bias after enrichment)
    if (
        typeof data === "object" &&
        data !== null &&
        !Array.isArray(data) &&
        "match_audit" in (data as Record<string, unknown>)
    ) {
        const obj = data as Record<string, unknown>;
        const audit = Array.isArray(obj["match_audit"])
            ? (obj["match_audit"] as Record<string, unknown>[])
            : null;
        return { mainData: data, matchAudit: audit };
    }

    return { mainData: data, matchAudit: null };
}

export default function FunctionRenderer({ outputType, data }: FunctionRendererProps) {
    // Null / undefined data
    if (data === null || data === undefined) {
        return (
            <EmptyState
                title="No Analysis Data"
                message="The engine returned no data for this query. This might be due to insufficient matches or missing context."
                actionLabel="Try adjusting filters"
            />
        );
    }

    // Extract enriched data (stats + optional match_audit)
    const { mainData, matchAudit } = extractEnrichedData(data);

    // Route to the correct renderer based on output_type
    switch (outputType) {
        case "report":
            // Report expects a dict
            if (typeof mainData === "object" && !Array.isArray(mainData)) {
                return (
                    <>
                        <ReportCard data={mainData as Record<string, unknown>} />
                        {matchAudit && <MatchAuditSection records={matchAudit} />}
                    </>
                );
            }
            // If API returned an array for report type, render as generic table
            if (Array.isArray(mainData)) {
                return (
                    <>
                        <DataTable data={mainData as Record<string, unknown>[]} />
                        {matchAudit && <MatchAuditSection records={matchAudit} />}
                    </>
                );
            }
            break;

        case "comparison_table":
            // Comparison table expects a list of {Metric, Value} dicts
            if (Array.isArray(mainData)) {
                return (
                    <>
                        <ComparisonTable data={mainData as Record<string, unknown>[]} />
                        {matchAudit && <MatchAuditSection records={matchAudit} />}
                    </>
                );
            }
            break;

        case "matrix_table":
            // Matrix table expects a list of per-opponent dicts
            if (Array.isArray(mainData)) {
                return (
                    <>
                        <MatrixTable data={mainData as Record<string, unknown>[]} />
                        {matchAudit && <MatchAuditSection records={matchAudit} />}
                    </>
                );
            }
            break;

        case "form_table":
            // Form table expects a list of match records
            if (Array.isArray(mainData)) {
                return <FormTable data={mainData as Record<string, unknown>[]} />;
            }
            break;

        case "table":
            // Generic table expects an array of dicts
            if (Array.isArray(mainData)) {
                return (
                    <>
                        <DataTable data={mainData as Record<string, unknown>[]} />
                        {matchAudit && <MatchAuditSection records={matchAudit} />}
                    </>
                );
            }
            break;

        case "phase_analysis":
            // Phase analysis expects a nested dict from venue_phases engine
            if (typeof mainData === "object" && !Array.isArray(mainData)) {
                return <PhaseAnalysisCard data={mainData as Record<string, unknown>} />;
            }
            break;

        case "venue_matchup_report":
            // Structured Venue Matchup report (V6.0)
            if (typeof mainData === "object" && !Array.isArray(mainData)) {
                return (
                    <>
                        <VenueMatchupReport data={mainData as VenueMatchupData} />
                        {matchAudit && <MatchAuditSection records={matchAudit} />}
                    </>
                );
            }
            break;

        case "prediction_card":
            // Prediction card expects a dict
            if (typeof mainData === "object" && !Array.isArray(mainData)) {
                return <PredictionCard data={mainData as Record<string, unknown>} />;
            }
            break;

        case "profile_card":
            // Profile card expects a dict
            if (typeof mainData === "object" && !Array.isArray(mainData)) {
                return <PlayerProfileCard data={mainData as Record<string, unknown>} />;
            }
            break;

        case "matchup_table":
            // Matchup table expects a list of matchup dicts
            if (Array.isArray(mainData)) {
                return <MatchupTable data={mainData as Record<string, unknown>[]} />;
            }
            break;

        case "download_json":
            // Download panel expects a dict
            if (typeof mainData === "object" && !Array.isArray(mainData)) {
                return <DownloadPanel data={mainData as Record<string, unknown>} />;
            }
            break;
    }

    // ── Fallback: Smart Auto-Detection ──────────────────────────────────
    // If output_type doesn't match or data shape is unexpected,
    // try to render intelligently.
    if (Array.isArray(mainData) && mainData.length > 0 && typeof mainData[0] === "object") {
        return (
            <div>
                <FallbackBanner outputType={outputType} />
                <DataTable data={mainData as Record<string, unknown>[]} />
                {matchAudit && <MatchAuditSection records={matchAudit} />}
            </div>
        );
    }

    if (typeof mainData === "object" && !Array.isArray(mainData)) {
        return (
            <div>
                <FallbackBanner outputType={outputType} />
                <ReportCard data={mainData as Record<string, unknown>} />
                {matchAudit && <MatchAuditSection records={matchAudit} />}
            </div>
        );
    }

    // Last resort: raw JSON
    return (
        <div>
            <FallbackBanner outputType={outputType} />
            <pre className="[background:var(--bg-elevated)] [padding:16px] [border-radius:var(--radius-md)] [font-size:0.8rem] [color:var(--text-secondary)] [overflow:auto] [max-height:400px] [border:1px_solid_var(--border-subtle)]">
                {JSON.stringify(data, null, 2)}
            </pre>
        </div>
    );
}

// ── Fallback Banner ─────────────────────────────────────────────────────

function FallbackBanner({ outputType }: { outputType: string }) {
    return (
        <div className="[display:flex] [align-items:center] [gap:8px] [padding:8px_14px] [margin-bottom:12px] [background:rgba(245,_158,_11,_0.08)] [border:1px_solid_rgba(245,_158,_11,_0.2)] [border-radius:var(--radius-md)] [font-size:0.78rem] [color:var(--tier-caution)]">
            <AlertCircle size={14} />
            <span>
                Rendering as fallback for output type <strong>&quot;{outputType}&quot;</strong>.
                Data shape may not match expected renderer.
            </span>
        </div>
    );
}
