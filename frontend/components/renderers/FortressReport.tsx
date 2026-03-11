"use client";

import React from "react";
import { AlertCircle, BarChart3, Dna, MapPin, ShieldCheck, Target, Trophy } from "lucide-react";
import EmptyState from "@/components/common/EmptyState";
import type { TeamTone } from "@/lib/comparison-types";
import { getHomeFortressData } from "@/lib/fortress-types";
import type { FortressData, FortressTeam } from "@/lib/fortress-types";

type ToneClasses = { border: string; overlay: string };

const TONE_CLASS_MAP: Record<TeamTone, ToneClasses> = {
    blue: { border: "[border-color:var(--border-accent)]", overlay: "[background:linear-gradient(180deg,_var(--accent-primary),_transparent)] [opacity:0.18]" },
    emerald: { border: "[border-color:var(--tier-elite)]", overlay: "[background:linear-gradient(180deg,_var(--tier-elite),_transparent)] [opacity:0.18]" },
    amber: { border: "[border-color:var(--tier-caution)]", overlay: "[background:linear-gradient(180deg,_var(--tier-caution),_transparent)] [opacity:0.2]" },
    rose: { border: "[border-color:var(--tier-danger)]", overlay: "[background:linear-gradient(180deg,_var(--tier-danger),_transparent)] [opacity:0.18]" },
    violet: { border: "[border-color:var(--accent-secondary)]", overlay: "[background:linear-gradient(180deg,_var(--accent-secondary),_transparent)] [opacity:0.2]" },
    slate: { border: "[border-color:var(--glass-border)]", overlay: "[background:linear-gradient(180deg,_var(--text-secondary),_transparent)] [opacity:0.16]" },
};

function toneClasses(tone: TeamTone): ToneClasses {
    return TONE_CLASS_MAP[tone];
}

function toTeamColorVarName(teamName: string): string {
    return `--venue-team-${teamName.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/(^-|-$)/g, "")}-color`;
}

export default function FortressReport({ data }: { data: Record<string, unknown> }) {
    const payload: FortressData | null = getHomeFortressData(data);
    if (!payload) return <EmptyState message="No fortress report data available." />;
    const { summary, home, visitor, venue_avg } = payload;
    const lowSampleWarnings = payload.low_sample_warnings ?? [];
    React.useEffect(() => {
        const root = document.documentElement;
        const injected: string[] = [];
        [home, visitor]
            .filter((team) => team.name && team.stats.team_color)
            .forEach((team) => {
                const varName = toTeamColorVarName(team.name);
                root.style.setProperty(varName, team.stats.team_color);
                injected.push(varName);
            });
        Object.entries(payload.team_colors ?? {}).forEach(([teamName, color]) => {
            if (!teamName || !color) return;
            const varName = toTeamColorVarName(teamName);
            root.style.setProperty(varName, color);
            injected.push(varName);
        });
        return () => {
            for (const varName of injected) root.style.removeProperty(varName);
        };
    }, [home, visitor, payload.team_colors]);
    return (
        <div
            className="mx-auto flex w-full max-w-5xl animate-fade-in flex-col gap-7 px-4 py-2 sm:px-5 lg:px-6"
        >
            <div
                className="grid grid-cols-3 overflow-hidden rounded-xl [background:var(--glass-bg)] [border:1px_solid_var(--glass-border)] backdrop-blur-sm [box-shadow:var(--shadow-md)]"
            >
                <SummaryItem
                    label="MATCHES"
                    value={summary.matches}
                    icon={<BarChart3 size={16} />}
                />
                <SummaryItem
                    label="HOME WIN %"
                    value={`${summary.home_win_pct}%`}
                    highlight
                    icon={<Trophy size={16} className="[color:var(--tier-caution)]" />}
                />
                <SummaryItem
                    label="TIED/NR"
                    value={summary.tie_nr}
                    icon={<Dna size={16} />}
                />
            </div>
            <div className="grid grid-cols-1 gap-7 md:grid-cols-2">
                <TeamCard
                    team={home}
                    isHome
                />
                <TeamCard
                    team={visitor}
                    isHome={false}
                />
            </div>
            <div className="flex flex-col gap-4">
                <div
                    className="flex flex-wrap items-center justify-center gap-x-12 gap-y-4 rounded-xl p-5 [background:var(--glass-bg)] [border:1px_solid_var(--glass-border)] backdrop-blur-sm [box-shadow:var(--shadow-md)]"
                >
                    <div
                        className="flex items-center gap-2 text-sm font-bold tracking-tight [color:var(--text-secondary)]"
                    >
                        <MapPin
                            size={16}
                            className="[color:var(--accent-primary)]"
                        />
                        <span>VENUE AVERAGES</span>
                    </div>
                    <FooterItem
                        label="1st Inn Avg"
                        value={venue_avg.avg_1st}
                    />
                    <FooterItem
                        label="2nd Inn Avg"
                        value={venue_avg.avg_2nd}
                    />
                    <FooterItem
                        label="Avg Winning Score"
                        value={venue_avg.avg_win_score}
                    />
                </div>
                {lowSampleWarnings.length > 0 && (
                    <div
                        className="flex items-start justify-center gap-3 rounded-xl border-l-4 px-5 py-3 [background:var(--bg-elevated)] [border-top:1px_solid_var(--border-default)] [border-right:1px_solid_var(--border-default)] [border-bottom:1px_solid_var(--border-default)] [border-left-color:var(--tier-caution)]"
                    >
                        <AlertCircle
                            size={14}
                            className="mt-0.5 shrink-0 [color:var(--tier-caution)] opacity-85"
                        />
                        <div className="flex flex-col gap-0.5">
                            <p className="text-[10px] font-bold uppercase tracking-[0.15em] [color:var(--tier-caution)]">
                                Accuracy Notice: Sparse Data Detected
                            </p>
                            <p className="text-[12px] italic leading-tight [color:var(--text-secondary)]">
                                <span>Low sample for: </span>
                                <span className="font-medium [color:var(--text-primary)]">
                                    {lowSampleWarnings.join(", ")}
                                </span>
                                <span>. Use with caution.</span>
                            </p>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}

function SummaryItem({ label, value, highlight = false, icon }: { label: string; value: string | number; highlight?: boolean; icon: React.ReactNode }) {
    return (
        <div
            className="flex flex-col items-center justify-center border-r p-5 [border-color:var(--glass-border)] last:border-0"
        >
            <span className={`font-numeric text-[2rem] font-black leading-none ${highlight ? "[color:var(--accent-primary)]" : "[color:var(--text-primary)]"}`}>
                {value}
            </span>
            <div className="mt-1.5 flex items-center gap-1.5">
                {icon}
                <span className="text-[10px] font-semibold uppercase tracking-[0.14em] [color:var(--text-secondary)]">
                    {label}
                </span>
            </div>
        </div>
    );
}

function TeamCard({ team, isHome }: { team: FortressTeam; isHome: boolean }) {
    const stats = team.stats;
    const tone = toneClasses(stats.team_tone ?? "slate");
    const teamAccentClass = isHome
        ? "border-l-4 [border-left-color:var(--accent-primary)]"
        : "border-l-4 [border-left-color:var(--tier-danger)]";
    const teamHeadingStyle: React.CSSProperties = {
        ...(stats.team_color ? { color: `var(${toTeamColorVarName(team.name)})` } : {}),
        textShadow: "0 0 1px var(--text-primary), 0 0 1px var(--text-primary)",
    };
    return (
        <div
            className={`relative overflow-hidden rounded-md border [background:var(--bg-surface)] backdrop-blur-sm [box-shadow:var(--shadow-lg)] ${tone.border} ${teamAccentClass}`}
        >
            <div className={`pointer-events-none absolute inset-x-0 top-0 h-16 opacity-25 ${tone.overlay}`} />
            <div className="flex flex-col items-center gap-3.5 border-b px-5 py-4 [border-color:var(--glass-border)]">
                <h3
                    className="text-center text-[1.65rem] font-black uppercase tracking-tight"
                    style={teamHeadingStyle}
                >
                    {team.name || "-"}
                </h3>
                <div className="flex justify-center gap-2">
                    <StatBadge
                        icon={<Trophy size={12} className="[color:var(--tier-caution)]" />}
                        label="Wins"
                        value={stats.wins}
                    />
                    <StatBadge
                        icon={<ShieldCheck size={12} className="[color:var(--accent-primary)]" />}
                        label="Def"
                        value={stats.defended}
                    />
                    <StatBadge
                        icon={<Target size={12} className="[color:var(--tier-danger)]" />}
                        label="Chs"
                        value={stats.chased}
                    />
                </div>
            </div>
            <div className="flex flex-col gap-5 px-5 py-5 sm:px-6">
                <div>
                    <SectionHeader
                        label="BATTING 1ST"
                        activeColor="[color:var(--tier-elite)]"
                    />
                    <div className="mt-3 flex flex-col gap-1">
                        <DataRow label="Avg Score:" value={stats.bat1.avg} />
                        <DataRow label="High / Low:" value={`${stats.bat1.high} / ${stats.bat1.low}`} />
                        <DataRow label="Avg Win Score:" value={stats.bat1.avg_win} />
                        <DataRow label="Lowest Defended:" value={stats.bat1.low_def} />
                    </div>
                </div>
                <div>
                    <SectionHeader
                        label="CHASING"
                        activeColor="[color:var(--accent-primary)]"
                    />
                    <div className="mt-3 flex flex-col gap-1">
                        <DataRow label="Avg Score:" value={stats.chase.avg} />
                        <DataRow label="Highest Chased:" value={stats.chase.high} />
                        <DataRow label="Avg Succ. Chase:" value={stats.chase.succ} />
                        <DataRow label="Avg Fail Chase:" value={stats.chase.fail} />
                    </div>
                </div>
            </div>
        </div>
    );
}

function StatBadge({ icon, label, value }: { icon: React.ReactNode; label: string; value: string | number }) {
    return (
        <div
            className="flex items-center gap-2 rounded-full px-3 py-1.5 [background:var(--glass-bg)] [border:1px_solid_var(--glass-border)] [box-shadow:var(--shadow-sm)] transition-colors hover:[background:var(--bg-hover)]"
        >
            {icon}
            <span className="font-numeric text-sm font-black leading-none [color:var(--text-primary)]">
                {value}
            </span>
            <span className="mb-[-1px] text-[10px] font-bold uppercase tracking-[0.12em] leading-none [color:var(--text-secondary)]">
                {label}
            </span>
        </div>
    );
}

function SectionHeader({ label, activeColor }: { label: string; activeColor: string }) {
    return (
        <div className="mb-1 border-b-2 pb-2 [border-color:var(--glass-border)]">
            <span className={`text-xs font-black uppercase tracking-[0.2em] ${activeColor}`}>{label}</span>
        </div>
    );
}

function DataRow({ label, value }: { label: string; value: string }) {
    const renderValue = (displayValue: string) => {
        if (displayValue === "" || displayValue === "-") return "-";
        const parts = displayValue.split(/(\[.*?\])/);
        if (parts.length === 1) return displayValue;
        return parts.map((part, index) => {
            if (part.startsWith("[") && part.endsWith("]")) {
                return (
                    <span
                        key={index}
                        className="ml-1.5 text-[0.8em] font-medium [color:var(--text-muted)]"
                    >
                        {part}
                    </span>
                );
            }
            return part;
        });
    };

    return (
        <div
            className="group grid grid-cols-[minmax(0,1fr)_minmax(max-content,auto)] items-start gap-x-4 border-b py-1.5 [border-color:var(--border-subtle)] last:border-0"
        >
            <span className="min-w-0 pl-1 text-[12px] font-medium tracking-tight leading-[1.3] [color:var(--text-secondary)] transition-colors group-hover:[color:var(--text-primary)]">
                {label}
            </span>
            <span className="min-w-0 break-words pr-3 text-right text-[12px] font-medium tracking-tight leading-[1.3] whitespace-normal [color:var(--text-primary)]">
                {renderValue(value)}
            </span>
        </div>
    );
}

function FooterItem({ label, value }: { label: string; value: string }) {
    return (
        <div className="flex items-center gap-2">
            <span className="text-xs font-semibold whitespace-nowrap [color:var(--text-secondary)]">{label}:</span>
            <span className="font-numeric text-sm font-black tracking-tight [color:var(--text-primary)]">{value}</span>
        </div>
    );
}
