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
import { AlertCircle } from "lucide-react";

interface FunctionRendererProps {
    outputType: string;
    data: unknown;
}

export default function FunctionRenderer({ outputType, data }: FunctionRendererProps) {
    // Null / undefined data
    if (data === null || data === undefined) {
        return (
            <div style={{
                padding: "24px", textAlign: "center",
                color: "var(--text-muted)", fontSize: "0.9rem",
            }}>
                No data returned from the engine.
            </div>
        );
    }

    // Route to the correct renderer based on output_type
    switch (outputType) {
        case "report":
            // Report expects a dict
            if (typeof data === "object" && !Array.isArray(data)) {
                return <ReportCard data={data as Record<string, unknown>} />;
            }
            // If API returned an array for report type, render as generic table
            if (Array.isArray(data)) {
                return <DataTable data={data as Record<string, unknown>[]} />;
            }
            break;

        case "comparison_table":
            // Comparison table expects a list of {Metric, Value} dicts
            if (Array.isArray(data)) {
                return <ComparisonTable data={data as Record<string, unknown>[]} />;
            }
            break;

        case "matrix_table":
            // Matrix table expects a list of per-opponent dicts
            if (Array.isArray(data)) {
                return <MatrixTable data={data as Record<string, unknown>[]} />;
            }
            break;

        case "form_table":
            // Form table expects a list of match records
            if (Array.isArray(data)) {
                return <FormTable data={data as Record<string, unknown>[]} />;
            }
            break;

        case "table":
            // Generic table expects an array of dicts
            if (Array.isArray(data)) {
                return <DataTable data={data as Record<string, unknown>[]} />;
            }
            break;

        case "prediction_card":
            // Prediction card expects a dict
            if (typeof data === "object" && !Array.isArray(data)) {
                return <PredictionCard data={data as Record<string, unknown>} />;
            }
            break;

        case "profile_card":
            // Profile card expects a dict
            if (typeof data === "object" && !Array.isArray(data)) {
                return <PlayerProfileCard data={data as Record<string, unknown>} />;
            }
            break;

        case "matchup_table":
            // Matchup table expects a list of matchup dicts
            if (Array.isArray(data)) {
                return <MatchupTable data={data as Record<string, unknown>[]} />;
            }
            break;

        case "download_json":
            // Download panel expects a dict
            if (typeof data === "object" && !Array.isArray(data)) {
                return <DownloadPanel data={data as Record<string, unknown>} />;
            }
            break;
    }

    // ── Fallback: Smart Auto-Detection ──────────────────────────────────
    // If output_type doesn't match or data shape is unexpected,
    // try to render intelligently.
    if (Array.isArray(data) && data.length > 0 && typeof data[0] === "object") {
        return (
            <div>
                <FallbackBanner outputType={outputType} />
                <DataTable data={data as Record<string, unknown>[]} />
            </div>
        );
    }

    if (typeof data === "object" && !Array.isArray(data)) {
        return (
            <div>
                <FallbackBanner outputType={outputType} />
                <ReportCard data={data as Record<string, unknown>} />
            </div>
        );
    }

    // Last resort: raw JSON
    return (
        <div>
            <FallbackBanner outputType={outputType} />
            <pre style={{
                background: "var(--bg-elevated)", padding: "16px",
                borderRadius: "var(--radius-md)", fontSize: "0.8rem",
                color: "var(--text-secondary)", overflow: "auto",
                maxHeight: 400, border: "1px solid var(--border-subtle)",
            }}>
                {JSON.stringify(data, null, 2)}
            </pre>
        </div>
    );
}

// ── Fallback Banner ─────────────────────────────────────────────────────

function FallbackBanner({ outputType }: { outputType: string }) {
    return (
        <div style={{
            display: "flex", alignItems: "center", gap: "8px",
            padding: "8px 14px", marginBottom: "12px",
            background: "rgba(245, 158, 11, 0.08)",
            border: "1px solid rgba(245, 158, 11, 0.2)",
            borderRadius: "var(--radius-md)",
            fontSize: "0.78rem", color: "var(--tier-caution)",
        }}>
            <AlertCircle size={14} />
            <span>
                Rendering as fallback for output type <strong>&quot;{outputType}&quot;</strong>.
                Data shape may not match expected renderer.
            </span>
        </div>
    );
}
