/**
 * EmptyState.tsx — Playful "No Data" Screen
 * 
 * Renders when an API returns no data, explaining WHY.
 * Features:
 *  - Format-aware messaging
 *  - Helpful suggestions ("Try changing the venue")
 *  - Premium "Glass" design to match the app
 */
"use client";

import { Ghost, SearchX, RefreshCcw } from "lucide-react";

interface EmptyStateProps {
    title?: string;
    message?: string;
    actionLabel?: string;
    onAction?: () => void;
    icon?: "ghost" | "search"; // can extend
}

export default function EmptyState({
    title = "No Data Found",
    message = "There are no matches matching your current filters.",
    actionLabel = "Clear Filters",
    onAction,
    icon = "ghost"
}: EmptyStateProps) {
    return (
        <div className="[display:flex] [flex-direction:column] [align-items:center] [justify-content:center] [padding:40px_20px] [min-height:300px] [text-align:center] [background:var(--bg-elevated)] [border-radius:var(--radius-lg)] [border:1px_dashed_var(--border-default)] [margin-top:20px]">
            <div className="[width:64px] [height:64px] [border-radius:50%] [background:var(--bg-hover)] [display:flex] [align-items:center] [justify-content:center] [margin-bottom:16px] [color:var(--text-disabled)]">
                {icon === "ghost" ? <Ghost size={32} /> : <SearchX size={32} />}
            </div>

            <h3 className="[font-size:1.1rem] [font-weight:700] [color:var(--text-primary)] [margin-bottom:8px]">
                {title}
            </h3>

            <p className="[font-size:0.9rem] [color:var(--text-secondary)] [max-width:400px] [line-height:1.5] [margin-bottom:24px]">
                {message}
            </p>

            {onAction && (
                <button
                    onClick={onAction}
                    className="btn-ghost [gap:8px]"
                >
                    <RefreshCcw size={14} />
                    {actionLabel}
                </button>
            )}
        </div>
    );
}
