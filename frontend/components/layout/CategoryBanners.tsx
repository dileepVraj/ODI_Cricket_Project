"use client";

import { AlertCircle, Users, Zap } from "lucide-react";

export function MissingContextBanner({ missingContextLabels }: { missingContextLabels: string[] }) {
    return (
        <div className="animate-fade-in [padding:16px] [background:var(--bg-caution)] [border:1px_solid_var(--border-caution)] [border-radius:var(--radius-md)] [margin-bottom:16px] [display:flex] [gap:12px] [align-items:flex-start]">
            <AlertCircle size={20} className="[color:var(--tier-caution)] [flex-shrink:0] [margin-top:2px]" />
            <div>
                <p className="[color:var(--tier-caution)] [font-size:0.9rem] [font-weight:600] [margin-bottom:6px]">
                    Missing Required Context
                </p>
                <p className="[color:var(--text-secondary)] [font-size:0.82rem] [line-height:1.5]">
                    Please fill in the following fields in the Context Bar above:{" "}
                    <strong className="[color:var(--text-primary)]">
                        {missingContextLabels.join(", ")}
                    </strong>
                </p>
            </div>
        </div>
    );
}

export function SquadHintBanner() {
    return (
        <div className="animate-fade-in [padding:14px] [background:var(--bg-info)] [border:1px_solid_var(--border-info)] [border-radius:var(--radius-md)] [margin-bottom:16px] [display:flex] [gap:12px] [align-items:center]">
            <Users size={18} className="[color:var(--accent-blue)] [flex-shrink:0]" />
            <p className="[color:var(--text-secondary)] [font-size:0.82rem]">
                Select players for <strong className="[color:var(--text-primary)]">Home XI</strong> and{" "}
                <strong className="[color:var(--text-primary)]">Away XI</strong> above, or click{" "}
                <strong className="[color:var(--accent-blue)]">Load Squad</strong> to auto-fill.
            </p>
        </div>
    );
}

export function MissingInputsBanner({ missingInputLabels }: { missingInputLabels: string[] }) {
    return (
        <div className="animate-fade-in [padding:14px] [background:var(--bg-info)] [border:1px_solid_var(--border-info)] [border-radius:var(--radius-md)] [margin-bottom:16px] [display:flex] [gap:12px] [align-items:center]">
            <AlertCircle size={18} className="[color:var(--accent-blue)] [flex-shrink:0]" />
            <p className="[color:var(--text-secondary)] [font-size:0.82rem]">
                Please select{" "}
                <strong className="[color:var(--text-primary)]">{missingInputLabels.join(", ")}</strong>{" "}
                to proceed.
            </p>
        </div>
    );
}

export function ExecuteErrorPanel({ error, onRetry }: { error: string; onRetry: () => void }) {
    return (
        <div
            role="alert"
            className="animate-fade-in [padding:14px] [background:var(--bg-danger)] [border:1px_solid_var(--border-danger)] [border-radius:var(--radius-md)] [margin-bottom:16px]"
        >
            <div className="[display:flex] [gap:10px] [align-items:flex-start]">
                <AlertCircle size={18} className="[color:var(--tier-danger)] [flex-shrink:0] [margin-top:2px]" />
                <div className="[flex:1]">
                    <p className="[color:var(--tier-danger)] [font-size:0.9rem] [font-weight:600] [margin-bottom:4px]">
                        Execution Failed
                    </p>
                    <p className="[color:var(--text-secondary)] [font-size:0.82rem] [line-height:1.5]">
                        {error}
                    </p>
                </div>
            </div>
            <button
                className="btn-ghost [margin-top:10px] [font-size:0.8rem] [display:flex] [align-items:center] [gap:6px]"
                onClick={onRetry}
            >
                <Zap size={14} />
                Retry
            </button>
        </div>
    );
}
