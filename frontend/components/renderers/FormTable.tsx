"use client";

import { Calendar, MapPin, Swords } from "lucide-react";
import EmptyState from "@/components/common/EmptyState";

interface FormTableProps {
    data: Record<string, unknown>[];
}

interface FormRow extends Record<string, unknown> {
    ResultTone?: string;
    ResultSymbol?: string;
    form_summary?: {
        wins: number;
        losses: number;
        ties_or_nr: number;
        total: number;
    };
}

function resultClasses(resultTone: string | undefined): {
    dotBg: string;
    dotText: string;
    borderLeft: string;
    badge: string;
    score: string;
} {
    if (resultTone === "elite") {
        return {
            dotBg: "bg-emerald-500/15 border-2 border-emerald-400/40",
            dotText: "text-emerald-300",
            borderLeft: "border-l-4 border-l-emerald-400",
            badge: "badge-elite",
            score: "text-emerald-300",
        };
    }
    if (resultTone === "danger") {
        return {
            dotBg: "bg-rose-500/15 border-2 border-rose-400/40",
            dotText: "text-rose-300",
            borderLeft: "border-l-4 border-l-rose-400",
            badge: "badge-danger",
            score: "text-slate-100",
        };
    }
    return {
        dotBg: "bg-amber-500/15 border-2 border-amber-400/40",
        dotText: "text-amber-300",
        borderLeft: "border-l-4 border-l-amber-400",
        badge: "badge-caution",
        score: "text-slate-100",
    };
}

export default function FormTable({ data }: FormTableProps) {
    if (!data || data.length === 0) {
        return <EmptyState message="No recent form data available." />;
    }

    const rows = data as FormRow[];
    const summary = rows[0]?.form_summary;
    const wins = summary?.wins ?? 0;
    const losses = summary?.losses ?? 0;
    const ties = summary?.ties_or_nr ?? 0;

    return (
        <div className="[display:flex] [flex-direction:column] [gap:16px]">
            <div className="glass-card [padding:16px_20px] [display:flex] [justify-content:space-between] [align-items:center] [gap:20px] [flex-wrap:wrap]">
                <div className="[display:flex] [gap:6px] [align-items:center]">
                    {rows.map((row, i) => {
                        const result = String(row["Result"] ?? "-");
                        const tone = resultClasses(row.ResultTone);
                        const symbol = String(row.ResultSymbol ?? "-");
                        return (
                            <div
                                key={i}
                                title={`${row["Opponent"]} - ${result}`}
                                className={`[width:28px] [height:28px] [border-radius:50%] [display:flex] [align-items:center] [justify-content:center] [font-size:0.75rem] [font-weight:800] [cursor:default] ${tone.dotBg} ${tone.dotText}`}
                            >
                                {symbol}
                            </div>
                        );
                    })}
                </div>

                <div className="[display:flex] [gap:16px] [font-size:0.85rem]">
                    <span className="[font-weight:700] [color:var(--tier-elite)]">{wins}W</span>
                    <span className="[font-weight:700] [color:var(--tier-danger)]">{losses}L</span>
                    {ties > 0 && <span className="[font-weight:700] [color:var(--text-muted)]">{ties}NR</span>}
                </div>
            </div>

            {rows.map((row, i) => {
                const result = String(row["Result"] ?? "-");
                const tone = resultClasses(row.ResultTone);
                return (
                    <div
                        key={i}
                        className={`[display:flex] [align-items:center] [gap:16px] [padding:14px_18px] [background:var(--bg-elevated)] [border-radius:var(--radius-md)] [border:1px_solid_var(--border-subtle)] [transition:background_var(--transition-fast),_border-color_var(--transition-fast)] hover:[background:var(--bg-hover)] ${tone.borderLeft}`}
                    >
                        <div className={`[width:36px] [height:36px] [border-radius:var(--radius-md)] [display:flex] [align-items:center] [justify-content:center] [font-size:1.1rem] [flex-shrink:0] ${tone.dotBg}`}>
                            {String(row.ResultSymbol ?? "-")}
                        </div>

                        <div className="[flex:1] [min-width:0px]">
                            <div className="[display:flex] [align-items:center] [gap:8px] [margin-bottom:4px] [flex-wrap:wrap]">
                                <span className="[font-size:0.92rem] [font-weight:700] [color:var(--text-primary)]">vs {String(row["Opponent"] ?? "-")}</span>
                                <span className={`badge ${tone.badge} [font-size:0.65rem]`}>{result}</span>
                            </div>
                            <div className="[display:flex] [gap:12px] [font-size:0.78rem] [color:var(--text-muted)] [flex-wrap:wrap]">
                                <span className="[display:inline-flex] [align-items:center] [gap:4px]">
                                    <Calendar size={12} />
                                    {String(row["Date"] ?? "-")}
                                </span>
                                <span className="[display:inline-flex] [align-items:center] [gap:4px]">
                                    <MapPin size={12} />
                                    {String(row["Venue"] ?? "-")}
                                </span>
                            </div>
                        </div>

                        <div className="[text-align:right] [flex-shrink:0]">
                            <div className="[display:flex] [align-items:center] [gap:8px] [justify-content:flex-end]">
                                <span className={`[font-size:0.9rem] [font-weight:700] font-numeric ${tone.score}`}>
                                    {String(row["TeamScore"] ?? "-")}
                                </span>
                                <Swords size={12} className="[color:var(--text-disabled)]" />
                                <span className="[font-size:0.9rem] [font-weight:500] [color:var(--text-secondary)] font-numeric">
                                    {String(row["OppScore"] ?? "-")}
                                </span>
                            </div>
                        </div>
                    </div>
                );
            })}
        </div>
    );
}
