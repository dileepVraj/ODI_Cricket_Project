/**
 * FormatSelector.tsx — Top Bar Format Tabs (Layer 1)
 * 
 * Renders: [🏏 ODI] [⚡ T20I] [🏆 IPL] [🏏 WODI] [⚡ WT20I]
 * Data source: GET /api/formats (via AppContext)
 * Rule F3: No format-specific code — reads from API.
 */
"use client";

import { useAppContext } from "@/lib/context";
import { Activity, Zap } from "lucide-react";

export default function FormatSelector() {
    const { formats, activeFormat, switchFormat, manifest } = useAppContext();

    return (
        <header
            id="format-selector-bar"
            className="format-selector"
            style={{
                height: "var(--topbar-height)",
                background: "var(--bg-base)",
                borderBottom: "1px solid var(--border-subtle)",
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                padding: "0 20px",
                position: "sticky",
                top: 0,
                zIndex: 50,
            }}
        >
            {/* ── Logo / Brand ──────────────────────────────────────────────── */}
            <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
                <div
                    style={{
                        width: 32,
                        height: 32,
                        borderRadius: "var(--radius-md)",
                        background: "linear-gradient(135deg, var(--accent-primary), var(--accent-secondary))",
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                    }}
                >
                    <Activity size={18} color="white" />
                </div>
                <div>
                    <h1
                        className="gradient-text"
                        style={{
                            fontSize: "1rem",
                            fontWeight: 800,
                            lineHeight: 1.1,
                            letterSpacing: "-0.02em",
                        }}
                    >
                        CricketAlgo
                    </h1>
                    <span
                        style={{
                            fontSize: "0.65rem",
                            color: "var(--text-disabled)",
                            fontWeight: 500,
                            letterSpacing: "0.05em",
                            textTransform: "uppercase",
                        }}
                    >
                        Trading Platform
                    </span>
                </div>
            </div>

            {/* ── Format Tabs ───────────────────────────────────────────────── */}
            <nav
                style={{
                    display: "flex",
                    gap: "4px",
                    alignItems: "center",
                }}
            >
                {formats.map((fmt) => (
                    <button
                        key={fmt.key}
                        id={`format-tab-${fmt.key}`}
                        className={`format-tab ${fmt.key === activeFormat ? "active" : ""
                            } ${!fmt.has_manifest ? "disabled" : ""}`}
                        onClick={() => switchFormat(fmt.key)}
                        disabled={!fmt.has_manifest}
                        title={
                            fmt.has_manifest
                                ? fmt.label
                                : `${fmt.label} — coming soon`
                        }
                    >
                        <span style={{ fontSize: "1rem" }}>{fmt.icon}</span>
                        <span>{fmt.label}</span>
                    </button>
                ))}
            </nav>

            {/* ── Status Indicator ──────────────────────────────────────────── */}
            <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                {manifest && (
                    <span
                        style={{
                            display: "flex",
                            alignItems: "center",
                            gap: "6px",
                            fontSize: "0.75rem",
                            color: "var(--tier-elite)",
                            fontWeight: 500,
                        }}
                    >
                        <Zap size={12} />
                        <span>LIVE</span>
                    </span>
                )}
            </div>
        </header>
    );
}
