/**
 * ComparisonTable.tsx — Side-by-Side Team Comparison
 * 
 * Used by: venue_matchup, home_fortress, global_h2h, country_h2h
 * 
 * Data shape: List of { Metric: string, Value: string|number }
 * Section headers are rows where Metric contains "---" 
 * (e.g., "--- HOME PERFORMANCE ---")
 * 
 * Renders as a premium card with section dividers and 
 * highlighted headers for each team's stats.
 */
"use client";

interface ComparisonTableProps {
    data: Record<string, unknown>[];
}

// Hidden internal columns
const HIDDEN_METRICS = new Set(["MATCH_IDS"]);

export default function ComparisonTable({ data }: ComparisonTableProps) {
    if (!data || data.length === 0) {
        return (
            <div style={{ padding: "20px", textAlign: "center", color: "var(--text-muted)" }}>
                No comparison data available.
            </div>
        );
    }

    // Group rows by sections (rows starting with "---")
    const sections: { header: string; rows: Record<string, unknown>[] }[] = [];
    let currentSection: { header: string; rows: Record<string, unknown>[] } = {
        header: "Overview",
        rows: [],
    };

    for (const row of data) {
        const metric = String(row["Metric"] ?? "");
        if (HIDDEN_METRICS.has(metric)) continue;

        if (metric.startsWith("---")) {
            // Push previous section if it has rows
            if (currentSection.rows.length > 0) {
                sections.push(currentSection);
            }
            // Start new section — extract label between dashes
            const label = metric.replace(/^-+\s*/, "").replace(/\s*-+$/, "").trim();
            currentSection = { header: label, rows: [] };
        } else {
            currentSection.rows.push(row);
        }
    }
    // Push final section
    if (currentSection.rows.length > 0) {
        sections.push(currentSection);
    }

    return (
        <div style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
            {sections.map((section, si) => (
                <div key={si}>
                    {/* Section header */}
                    <div
                        style={{
                            display: "flex",
                            alignItems: "center",
                            gap: "10px",
                            marginBottom: "10px",
                        }}
                    >
                        <div
                            style={{
                                width: 4,
                                height: 20,
                                borderRadius: 2,
                                background: getSectionColor(section.header),
                            }}
                        />
                        <h4
                            style={{
                                fontSize: "0.8rem",
                                fontWeight: 700,
                                color: "var(--text-secondary)",
                                textTransform: "uppercase",
                                letterSpacing: "0.06em",
                            }}
                        >
                            {section.header}
                        </h4>
                    </div>

                    {/* Metric rows */}
                    <div
                        style={{
                            background: "var(--bg-elevated)",
                            borderRadius: "var(--radius-md)",
                            border: "1px solid var(--border-subtle)",
                            overflow: "hidden",
                        }}
                    >
                        {section.rows.map((row, ri) => {
                            const metric = String(row["Metric"] ?? "");
                            const value = row["Value"];
                            const isWinPct = metric.toLowerCase().includes("win %");
                            const isZeroOrEmpty = value === "" || value === 0 || value === "0";

                            return (
                                <div
                                    key={ri}
                                    style={{
                                        display: "flex",
                                        justifyContent: "space-between",
                                        alignItems: "center",
                                        padding: "10px 16px",
                                        borderBottom:
                                            ri < section.rows.length - 1
                                                ? "1px solid var(--border-subtle)"
                                                : "none",
                                        transition: "background var(--transition-fast)",
                                    }}
                                    onMouseEnter={(e) => {
                                        (e.currentTarget).style.background = "var(--bg-hover)";
                                    }}
                                    onMouseLeave={(e) => {
                                        (e.currentTarget).style.background = "transparent";
                                    }}
                                >
                                    {/* Metric name */}
                                    <span
                                        style={{
                                            fontSize: "0.84rem",
                                            color: "var(--text-secondary)",
                                            fontWeight: 500,
                                        }}
                                    >
                                        {metric}
                                    </span>

                                    {/* Value */}
                                    <span
                                        style={{
                                            fontSize: "0.9rem",
                                            fontWeight: 700,
                                            color: isZeroOrEmpty
                                                ? "var(--text-disabled)"
                                                : isWinPct
                                                    ? getWinPctColor(value)
                                                    : "var(--text-primary)",
                                            fontVariantNumeric: "tabular-nums",
                                            textAlign: "right",
                                            minWidth: 60,
                                        }}
                                    >
                                        {value === null || value === undefined ? "—" : String(value)}
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

// ── Helpers ──────────────────────────────────────────────────────────────

function getSectionColor(header: string): string {
    const h = header.toLowerCase();
    if (h.includes("home") || h.includes("batting 1st")) return "var(--accent-primary)";
    if (h.includes("visitor") || h.includes("chasing")) return "var(--accent-secondary)";
    if (h.includes("venue") || h.includes("overall")) return "var(--accent-tertiary)";
    return "var(--text-muted)";
}

function getWinPctColor(val: unknown): string {
    const n = parseFloat(String(val).replace("%", ""));
    if (isNaN(n)) return "var(--text-primary)";
    if (n >= 60) return "var(--tier-elite)";
    if (n >= 45) return "var(--tier-strong)";
    if (n >= 30) return "var(--tier-caution)";
    return "var(--tier-danger)";
}
