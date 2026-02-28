"use client";

import React from "react";
import { AlertCircle, BarChart3, Dna, MapPin, ShieldCheck, Target, Trophy } from "lucide-react";

interface TeamStats {
    wins: number;
    defended: number;
    chased: number;
    bat1: {
        avg: string;
        high: string;
        low: string;
        avg_win: string;
        low_def: string;
    };
    chase: {
        avg: string;
        high: string;
        succ: string;
        fail: string;
    };
    team_color: string;
    team_tone?: TeamTone;
}

interface VenueMatchupData {
    summary: {
        matches: number;
        win_pct: number;
        tie_nr: number;
        last_5_home?: string;
        last_5_away?: string;
    };
    team_a: {
        name: string;
        stats: TeamStats;
    };
    team_b: {
        name: string;
        stats: TeamStats;
    };
    venue_avg: {
        avg_1st: string;
        avg_2nd: string;
        avg_win_score: string;
    };
    low_sample_warnings?: string[];
    highlight_flags?: Record<string, boolean>;
    derived_badges?: string[];
}

interface SummaryItemProps {
    label: string;
    value: string | number;
    highlight?: boolean;
    icon: React.ReactNode;
}

interface TeamCardProps {
    team: {
        name: string;
        stats: TeamStats;
    };
}

interface StatBadgeProps {
    icon: React.ReactNode;
    label: string;
    value: string | number;
}

interface VenueMatchupReportProps {
    data: VenueMatchupData;
    averagesTitle?: string;
}

type TeamTone = "blue" | "emerald" | "amber" | "rose" | "violet" | "slate";

function toneClasses(tone: TeamTone): { border: string; overlay: string; title: string } {
    if (tone === "blue") {
        return {
            border: "border-sky-400/35",
            overlay: "[background:linear-gradient(180deg,rgba(56,189,248,0.18),transparent)]",
            title: "text-sky-300",
        };
    }
    if (tone === "emerald") {
        return {
            border: "border-emerald-400/35",
            overlay: "[background:linear-gradient(180deg,rgba(52,211,153,0.18),transparent)]",
            title: "text-emerald-300",
        };
    }
    if (tone === "amber") {
        return {
            border: "border-amber-400/35",
            overlay: "[background:linear-gradient(180deg,rgba(251,191,36,0.2),transparent)]",
            title: "text-amber-300",
        };
    }
    if (tone === "rose") {
        return {
            border: "border-rose-400/35",
            overlay: "[background:linear-gradient(180deg,rgba(251,113,133,0.18),transparent)]",
            title: "text-rose-300",
        };
    }
    if (tone === "violet") {
        return {
            border: "border-violet-400/35",
            overlay: "[background:linear-gradient(180deg,rgba(167,139,250,0.2),transparent)]",
            title: "text-violet-300",
        };
    }
    return {
        border: "border-slate-400/30",
        overlay: "[background:linear-gradient(180deg,rgba(148,163,184,0.16),transparent)]",
        title: "text-slate-200",
    };
}

export default function VenueMatchupReport({ data, averagesTitle = "VENUE AVERAGES" }: VenueMatchupReportProps) {
    if (!data || !data.team_a || !data.team_b) return null;

    const { summary, team_a, team_b, venue_avg } = data;
    const hasFormGuide = Boolean(data.highlight_flags?.has_form_guide);
    const lowSampleWarnings = Array.isArray(data.low_sample_warnings) ? data.low_sample_warnings : [];

    return (
        <div className="flex flex-col gap-7 w-full max-w-5xl mx-auto p-2 animate-fade-in">
            <div className="grid grid-cols-3 bg-slate-800/35 border border-white/10 rounded-xl overflow-hidden backdrop-blur-sm shadow-[0_10px_28px_rgba(2,8,23,0.28)]">
                <SummaryItem label="MATCHES" value={summary.matches} icon={<BarChart3 size={16} />} />
                <SummaryItem
                    label={`${team_a.name} WIN %`}
                    value={`${summary.win_pct}%`}
                    highlight
                    icon={<Trophy size={16} className="text-amber-400" />}
                />
                <SummaryItem label="TIE/NR" value={summary.tie_nr} icon={<Dna size={16} />} />
            </div>

            {hasFormGuide && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 bg-slate-800/25 border border-white/10 rounded-xl p-4">
                    <FooterItem label={`${team_a.name} Last 5`} value={summary.last_5_home || "-"} />
                    <FooterItem label={`${team_b.name} Last 5`} value={summary.last_5_away || "-"} />
                </div>
            )}

            <div className="grid grid-cols-1 md:grid-cols-2 gap-7">
                <TeamCard team={team_a} />
                <TeamCard team={team_b} />
            </div>

            <div className="flex flex-col gap-4">
                <div className="bg-slate-800/35 border border-white/10 rounded-xl p-5 flex flex-wrap justify-center items-center gap-x-12 gap-y-4 backdrop-blur-sm shadow-[0_8px_24px_rgba(2,8,23,0.22)]">
                    <div className="flex items-center gap-2 text-slate-300 text-sm font-bold tracking-tight">
                        <MapPin size={16} className="text-blue-400" /> {averagesTitle}
                    </div>
                    <FooterItem label="1st Inn Avg" value={venue_avg.avg_1st} />
                    <FooterItem label="2nd Inn Avg" value={venue_avg.avg_2nd} />
                    <FooterItem label="Avg Winning Score" value={venue_avg.avg_win_score} />
                </div>

                {lowSampleWarnings.length > 0 && (
                    <div className="flex items-start justify-center gap-3 px-6 py-3.5 bg-amber-500/5 border border-amber-500/20 rounded-xl">
                        <AlertCircle size={16} className="text-amber-500 mt-0.5 shrink-0" />
                        <div className="flex flex-col gap-1">
                            <p className="text-[11px] font-bold text-amber-500 uppercase tracking-widest">
                                Accuracy Notice: Sparse Data Detected
                            </p>
                            <p className="text-[12px] text-amber-200/70 italic leading-relaxed">
                                The statistical sample is currently low for: <span className="text-amber-100 font-semibold">{lowSampleWarnings.join(", ")}</span>. Averages
                                derived from fewer than 3 matches may not represent long-term trends.
                            </p>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}

function SummaryItem({ label, value, highlight = false, icon }: SummaryItemProps) {
    return (
        <div className="flex flex-col items-center justify-center p-5 border-r border-white/10 last:border-0">
            <span className={`text-[2rem] leading-none font-black font-numeric ${highlight ? "text-blue-400" : "text-white"}`}>
                {value}
            </span>
            <div className="flex items-center gap-1.5 mt-1.5">
                {icon}
                <span className="text-[10px] font-semibold tracking-[0.14em] text-slate-400 uppercase">{label}</span>
            </div>
        </div>
    );
}

function TeamCard({ team }: TeamCardProps) {
    const s = team.stats;
    if (!s) {
        return (
            <div className="p-10 text-center text-slate-500 bg-slate-800/20 rounded-xl border border-dashed border-slate-700">
                No data for {team.name}
            </div>
        );
    }

    const tone = toneClasses((s.team_tone as TeamTone) ?? "slate");

    return (
        <div className={`relative bg-slate-900/78 border rounded-2xl overflow-hidden backdrop-blur-sm shadow-[0_14px_34px_rgba(2,8,23,0.42)] ${tone.border}`}>
            <div className={`pointer-events-none absolute inset-x-0 top-0 h-20 opacity-25 ${tone.overlay}`} />

            <div className="p-6 border-b border-white/10 flex flex-col items-center gap-5">
                <h3 className={`text-2xl font-black tracking-tight uppercase text-center ${tone.title}`}>{team.name}</h3>

                <div className="flex justify-center gap-2.5">
                    <StatBadge icon={<Trophy size={12} className="text-amber-400" />} label="Wins" value={s.wins} />
                    <StatBadge icon={<ShieldCheck size={12} className="text-blue-400" />} label="Def" value={s.defended} />
                    <StatBadge icon={<Target size={12} className="text-rose-400" />} label="Chs" value={s.chased} />
                </div>
            </div>

            <div className="p-7 flex flex-col gap-10">
                <div>
                    <SectionHeader label="BATTING 1ST" activeColor="text-emerald-400" />
                    <div className="flex flex-col gap-1.5 mt-3">
                        <DataRow label="Avg Score:" value={s.bat1.avg} labelColor="text-emerald-100/70" />
                        <DataRow label="High / Low:" value={`${s.bat1.high} / ${s.bat1.low}`} labelColor="text-emerald-100/70" />
                        <DataRow label="Avg Win Score:" value={s.bat1.avg_win} labelColor="text-emerald-100/70" />
                        <DataRow label="Lowest Defended:" value={s.bat1.low_def} labelColor="text-emerald-100/70" />
                    </div>
                </div>

                <div>
                    <SectionHeader label="CHASING" activeColor="text-sky-400" />
                    <div className="flex flex-col gap-1.5 mt-3">
                        <DataRow label="Avg Score:" value={s.chase.avg} labelColor="text-sky-100/70" />
                        <DataRow label="Highest Chased:" value={s.chase.high} labelColor="text-sky-100/70" />
                        <DataRow label="Avg Succ. Chase:" value={s.chase.succ} labelColor="text-sky-100/70" />
                        <DataRow label="Avg Fail Chase:" value={s.chase.fail} labelColor="text-sky-100/70" />
                    </div>
                </div>
            </div>
        </div>
    );
}

function StatBadge({ icon, label, value }: StatBadgeProps) {
    return (
        <div className="flex items-center gap-2 bg-slate-800/45 px-3.5 py-1.5 rounded-full border border-white/10">
            {icon}
            <span className="text-xs font-extrabold text-slate-100 font-numeric">{value}</span>
            <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-[0.1em]">{label}</span>
        </div>
    );
}

function SectionHeader({ label, activeColor }: { label: string; activeColor: string }) {
    return (
        <div className="border-b border-white/10 pb-1.5">
            <span className={`text-[11px] font-black tracking-[0.18em] uppercase ${activeColor}`}>{label}</span>
        </div>
    );
}

function DataRow({ label, value, labelColor }: { label: string; value: string; labelColor: string }) {
    return (
        <div className="flex items-center justify-between group py-1.5 border-b border-white/[0.05] last:border-0">
            <span className={`pl-1.5 text-[12px] font-semibold tracking-tight ${labelColor} group-hover:text-white transition-colors`}>
                {label}
            </span>
            <span className="pr-1 text-[15px] leading-none font-extrabold text-white font-numeric tracking-tight text-right">
                {value === null || value === undefined || value === "" || value === "-" ? "-" : value}
            </span>
        </div>
    );
}

function FooterItem({ label, value }: { label: string; value: string }) {
    return (
        <div className="flex items-center gap-2">
            <span className="text-xs font-semibold text-slate-400 whitespace-nowrap">{label}:</span>
            <span className="text-sm font-black text-white font-numeric tracking-tight">{value}</span>
        </div>
    );
}
