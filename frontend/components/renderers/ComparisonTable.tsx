/**
 * ComparisonTable.tsx - Side-by-Side Team Comparison
 *
 * Used by: venue_matchup, home_fortress, global_h2h, country_h2h
 *
 * Data shape: List of { Metric: string, Value: string|number } with backend UI metadata.
 */
"use client";

import EmptyState from "@/components/common/EmptyState";
import {
    ComparisonRow,
    ComparisonSectionTone,
    ComparisonValueTone,
    toComparisonRows,
} from "@/lib/comparison-types";

interface ComparisonTableProps {
    data: Record<string, unknown>[];
}

const HIDDEN_METRICS = new Set(["MATCH_IDS"]);

export default function ComparisonTable({ data }: ComparisonTableProps) {
    if (!data || data.length === 0) {
        return <EmptyState message="No comparison data available." />;
    }

    const rows = toComparisonRows(data);
    const sections: { header: string; tone: ComparisonSectionTone; rows: ComparisonRow[] }[] = [];
    let currentSection: { header: string; tone: ComparisonSectionTone; rows: ComparisonRow[] } = {
        header: "Overview",
        tone: "muted",
        rows: [],
    };

    for (const row of rows) {
        const metric = String(row["Metric"] ?? "");
        if (HIDDEN_METRICS.has(metric)) continue;

        if (row.row_kind === "section") {
            if (currentSection.rows.length > 0) {
                sections.push(currentSection);
            }
            currentSection = {
                header: String(row.display_metric ?? row.section_label ?? "Section"),
                tone: row.section_tone ?? "muted",
                rows: [],
            };
        } else {
            currentSection.rows.push(row);
        }
    }

    if (currentSection.rows.length > 0) {
        sections.push(currentSection);
    }

    return (
        <div className="[display:flex] [flex-direction:column] [gap:20px]">
            {sections.map((section, si) => (
                <div key={si}>
                    <div className="[display:flex] [align-items:center] [gap:10px] [margin-bottom:10px]">
                        <div
                            className={`[width:4px] [height:20px] [border-radius:2px] [background:${sectionToneToCss(section.tone)}]`}
                        />
                        <h4 className="[font-size:0.8rem] [font-weight:700] [color:var(--text-secondary)] [text-transform:uppercase] [letter-spacing:0.06em]">
                            {section.header}
                        </h4>
                    </div>

                    <div className="[background:var(--bg-elevated)] [border-radius:var(--radius-md)] [border:1px_solid_var(--border-subtle)] [overflow:hidden]">
                        {section.rows.map((row, ri) => {
                            const metric = String(row.display_metric ?? row["Metric"] ?? "");
                            const value = row["Value"];
                            const isZeroOrEmpty = Boolean(row.is_zero_or_empty);
                            const valueTone = row.value_tone ?? "default";

                            return (
                                <div
                                    key={ri}
                                    className={`[display:flex] [justify-content:space-between] [align-items:center] [padding:10px_16px] [transition:background_var(--transition-fast)] ${ri < section.rows.length - 1 ? "[border-bottom:1px_solid_var(--border-subtle)]" : "[border-bottom:none]"}`}
                                    onMouseEnter={(e) => {
                                        e.currentTarget.style.background = "var(--bg-hover)";
                                    }}
                                    onMouseLeave={(e) => {
                                        e.currentTarget.style.background = "transparent";
                                    }}
                                >
                                    <span className="[font-size:0.84rem] [color:var(--text-secondary)] [font-weight:500]">
                                        {metric}
                                    </span>

                                    <span
                                        className={`[font-size:0.9rem] [font-weight:700] font-numeric [text-align:right] [min-width:60px] [color:${resolveValueColor(valueTone, isZeroOrEmpty)}]`}
                                    >
                                        {value === null || value === undefined ? "-" : String(value)}
                                    </span>
                                </div>
                            );
                        })}
                    </div>
                </div>
            ))}
        </div>
    );
}

function sectionToneToCss(tone: ComparisonSectionTone): string {
    if (tone === "primary") return "var(--accent-primary)";
    if (tone === "secondary") return "var(--accent-secondary)";
    if (tone === "tertiary") return "var(--accent-tertiary)";
    if (tone === "muted") return "var(--text-muted)";
    return "var(--text-muted)";
}

function resolveValueColor(tone: ComparisonValueTone, isZeroOrEmpty: boolean): string {
    if (isZeroOrEmpty || tone === "muted") return "var(--text-disabled)";
    if (tone === "elite") return "var(--tier-elite)";
    if (tone === "strong") return "var(--tier-strong)";
    if (tone === "caution") return "var(--tier-caution)";
    if (tone === "danger") return "var(--tier-danger)";
    return "var(--text-primary)";
}
