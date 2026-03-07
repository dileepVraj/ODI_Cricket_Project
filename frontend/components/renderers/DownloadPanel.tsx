"use client";

import { useState } from "react";
import { Check, ChevronDown, ChevronUp, Copy, Download, FileText } from "lucide-react";
import EmptyState from "@/components/common/EmptyState";

interface DownloadPanelProps {
    data: Record<string, unknown>;
}

export default function DownloadPanel({ data }: DownloadPanelProps) {
    const [showPreview, setShowPreview] = useState(false);
    const [copied, setCopied] = useState(false);

    if (!data || typeof data !== "object") {
        return <EmptyState message="No download data available." />;
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
        <div className="[display:flex] [flex-direction:column] [gap:16px]">
            <div className="glass-card [padding:20px_24px] [display:flex] [justify-content:space-between] [align-items:center] [flex-wrap:wrap] [gap:12px] [border:1px_solid_var(--border-accent)]">
                <div className="[display:flex] [align-items:center] [gap:14px]">
                    <div className="[width:44px] [height:44px] [border-radius:var(--radius-md)] [background:linear-gradient(135deg,_var(--accent-primary),_var(--accent-secondary))] [display:flex] [align-items:center] [justify-content:center]">
                        <FileText size={22} className="[color:white]" />
                    </div>
                    <div>
                        <div className="[font-size:1rem] [font-weight:700] [color:var(--text-primary)]">Match Intelligence Report</div>
                        <div className="[font-size:0.78rem] [color:var(--text-muted)]">{chapters.length} sections - {sizeKB} KB</div>
                    </div>
                </div>

                <div className="[display:flex] [gap:8px]">
                    <button
                        className="btn-ghost [display:flex] [align-items:center] [gap:6px] [padding:8px_14px] [font-size:0.8rem]"
                        onClick={handleCopy}
                    >
                        {copied ? <Check size={14} /> : <Copy size={14} />}
                        {copied ? "Copied!" : "Copy"}
                    </button>
                    <button
                        className="btn-primary [display:flex] [align-items:center] [gap:6px] [padding:8px_16px] [font-size:0.8rem]"
                        onClick={handleDownload}
                    >
                        <Download size={14} />
                        Download JSON
                    </button>
                </div>
            </div>

            <div className="[background:var(--bg-elevated)] [border-radius:var(--radius-md)] [padding:16px_20px] [border:1px_solid_var(--border-subtle)]">
                <h4 className="[font-size:0.78rem] [font-weight:600] [color:var(--text-secondary)] [text-transform:uppercase] [letter-spacing:0.04em] [margin-bottom:10px]">
                    Report Sections
                </h4>
                <div className="[display:flex] [flex-direction:column] [gap:6px]">
                    {chapters.map((ch, i) => {
                        const hasData = data[ch] !== null && data[ch] !== undefined;
                        return (
                            <div
                                key={i}
                                className="[display:flex] [align-items:center] [gap:10px] [padding:6px_8px] [border-radius:var(--radius-sm)] [transition:background_var(--transition-fast)] hover:[background:var(--bg-hover)]"
                            >
                                <div className={`[width:20px] [height:20px] [border-radius:4px] [display:flex] [align-items:center] [justify-content:center] ${hasData ? "[background:var(--tier-elite)]" : "[background:var(--bg-active)]"}`}>
                                    {hasData && <Check size={12} className="[color:white]" />}
                                </div>
                                <span className={`[font-size:0.84rem] ${hasData ? "[color:var(--text-primary)] [font-weight:500]" : "[color:var(--text-disabled)] [font-weight:400]"}`}>
                                    {ch.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase())}
                                </span>
                            </div>
                        );
                    })}
                </div>
            </div>

            <button
                className="btn-ghost [display:flex] [align-items:center] [gap:6px] [width:fit-content] [font-size:0.8rem] [padding:6px_12px]"
                onClick={() => setShowPreview((v) => !v)}
            >
                {showPreview ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
                {showPreview ? "Hide Preview" : "Show JSON Preview"}
            </button>

            {showPreview && (
                <pre className="[background:var(--bg-elevated)] [padding:16px] [border-radius:var(--radius-md)] [font-size:0.75rem] [color:var(--text-secondary)] [overflow:auto] [max-height:500px] [border:1px_solid_var(--border-subtle)] [line-height:1.5]">
                    {jsonStr}
                </pre>
            )}
        </div>
    );
}
