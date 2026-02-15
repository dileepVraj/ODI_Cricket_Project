/**
 * DownloadPanel.tsx — File Download + Preview Panel
 * 
 * Used by: generate_pack (output_type: "download_json")
 * 
 * Data shape: Dict containing report chapters/sections.
 * 
 * Features:
 *   - Download JSON button
 *   - Chapter completion checklist
 *   - Collapsible JSON preview
 *   - File size indicator
 */
"use client";

import { useState } from "react";
import { Download, Check, ChevronDown, ChevronUp, FileText, Copy } from "lucide-react";

interface DownloadPanelProps {
    data: Record<string, unknown>;
}

export default function DownloadPanel({ data }: DownloadPanelProps) {
    const [showPreview, setShowPreview] = useState(false);
    const [copied, setCopied] = useState(false);

    if (!data || typeof data !== "object") {
        return (
            <div style={{ padding: "20px", textAlign: "center", color: "var(--text-muted)" }}>
                No data to download.
            </div>
        );
    }

    const jsonStr = JSON.stringify(data, null, 2);
    const sizeKB = Math.ceil(new TextEncoder().encode(jsonStr).byteLength / 1024);
    const chapters = Object.keys(data);

    function handleDownload() {
        const blob = new Blob([jsonStr], { type: "application/json" });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `match_report_${new Date().toISOString().split("T")[0]}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }

    function handleCopy() {
        navigator.clipboard.writeText(jsonStr).then(() => {
            setCopied(true);
            setTimeout(() => setCopied(false), 2000);
        });
    }

    return (
        <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
            {/* ── Download Header ──────────────────────────────────────────── */}
            <div
                className="glass-card"
                style={{
                    padding: "20px 24px",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "space-between",
                    flexWrap: "wrap",
                    gap: "12px",
                    border: "1px solid var(--border-accent)",
                }}
            >
                <div style={{ display: "flex", alignItems: "center", gap: "14px" }}>
                    <div style={{
                        width: 44, height: 44, borderRadius: "var(--radius-md)",
                        background: "linear-gradient(135deg, var(--accent-primary), var(--accent-secondary))",
                        display: "flex", alignItems: "center", justifyContent: "center",
                    }}>
                        <FileText size={22} style={{ color: "white" }} />
                    </div>
                    <div>
                        <div style={{
                            fontSize: "1rem", fontWeight: 700, color: "var(--text-primary)",
                        }}>
                            Match Intelligence Report
                        </div>
                        <div style={{
                            fontSize: "0.78rem", color: "var(--text-muted)",
                        }}>
                            {chapters.length} sections • {sizeKB} KB
                        </div>
                    </div>
                </div>

                <div style={{ display: "flex", gap: "8px" }}>
                    <button
                        className="btn-ghost"
                        onClick={handleCopy}
                        style={{
                            display: "flex", alignItems: "center", gap: "6px",
                            padding: "8px 14px", fontSize: "0.8rem",
                        }}
                    >
                        {copied ? <Check size={14} /> : <Copy size={14} />}
                        {copied ? "Copied!" : "Copy"}
                    </button>
                    <button
                        className="btn-primary"
                        onClick={handleDownload}
                        style={{
                            display: "flex", alignItems: "center", gap: "6px",
                            padding: "8px 16px", fontSize: "0.8rem",
                        }}
                    >
                        <Download size={14} />
                        Download JSON
                    </button>
                </div>
            </div>

            {/* ── Chapter Checklist ─────────────────────────────────────────── */}
            <div style={{
                background: "var(--bg-elevated)", borderRadius: "var(--radius-md)",
                padding: "16px 20px", border: "1px solid var(--border-subtle)",
            }}>
                <h4 style={{
                    fontSize: "0.78rem", fontWeight: 600, color: "var(--text-secondary)",
                    textTransform: "uppercase", letterSpacing: "0.04em", marginBottom: "10px",
                }}>
                    Report Sections
                </h4>
                <div style={{ display: "flex", flexDirection: "column", gap: "6px" }}>
                    {chapters.map((ch, i) => {
                        const hasData = data[ch] !== null && data[ch] !== undefined;
                        return (
                            <div
                                key={i}
                                style={{
                                    display: "flex", alignItems: "center", gap: "10px",
                                    padding: "6px 8px", borderRadius: "var(--radius-sm)",
                                    transition: "background var(--transition-fast)",
                                }}
                                onMouseEnter={(e) => { (e.currentTarget).style.background = "var(--bg-hover)"; }}
                                onMouseLeave={(e) => { (e.currentTarget).style.background = "transparent"; }}
                            >
                                <div style={{
                                    width: 20, height: 20, borderRadius: 4,
                                    background: hasData ? "var(--tier-elite)" : "var(--bg-active)",
                                    display: "flex", alignItems: "center", justifyContent: "center",
                                }}>
                                    {hasData && <Check size={12} style={{ color: "white" }} />}
                                </div>
                                <span style={{
                                    fontSize: "0.84rem",
                                    color: hasData ? "var(--text-primary)" : "var(--text-disabled)",
                                    fontWeight: hasData ? 500 : 400,
                                }}>
                                    {ch.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase())}
                                </span>
                            </div>
                        );
                    })}
                </div>
            </div>

            {/* ── Preview Toggle ────────────────────────────────────────────── */}
            <button
                className="btn-ghost"
                onClick={() => setShowPreview(!showPreview)}
                style={{
                    display: "flex", alignItems: "center", gap: "6px", width: "fit-content",
                    fontSize: "0.8rem", padding: "6px 12px",
                }}
            >
                {showPreview ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
                {showPreview ? "Hide Preview" : "Show JSON Preview"}
            </button>

            {showPreview && (
                <pre style={{
                    background: "var(--bg-elevated)", padding: "16px",
                    borderRadius: "var(--radius-md)", fontSize: "0.75rem",
                    color: "var(--text-secondary)", overflow: "auto",
                    maxHeight: 500, border: "1px solid var(--border-subtle)",
                    lineHeight: 1.5,
                }}>
                    {jsonStr}
                </pre>
            )}
        </div>
    );
}
