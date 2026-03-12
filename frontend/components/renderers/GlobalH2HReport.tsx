"use client";

import React from "react";
import { AlertCircle, BarChart3, Dna, MapPin, ShieldCheck, Target, Trophy } from "lucide-react";
import EmptyState from "@/components/common/EmptyState";
import { TeamTone, getTeamTone } from "@/lib/comparison-types";
import { GlobalH2HData, getGlobalH2HData } from "@/lib/global-h2h-types";

interface SummaryItemProps { label: string; value: string | number; highlight?: boolean; icon: React.ReactNode; }
interface TeamCardProps { team: { name: string; stats: GlobalH2HData["team_a"]["stats"] }; isHome?: boolean; }
interface StatBadgeProps { icon: React.ReactNode; label: string; value: string | number; }
interface GlobalH2HReportProps { data: Record<string, unknown>; }

function toneClasses(tone: TeamTone): { border: string; overlay: string; title: string } {
    if (tone === "blue") {
        return {
            border: "[border-color:var(--border-accent)]",
            overlay: "[background:linear-gradient(180deg,_var(--accent-primary),_transparent)] [opacity:0.18]",
            title: "[color:var(--accent-primary)]",
        };
    }
    if (tone === "emerald") {
        return {
            border: "[border-color:var(--tier-elite)]",
            overlay: "[background:linear-gradient(180deg,_var(--tier-elite),_transparent)] [opacity:0.18]",
            title: "[color:var(--tier-elite)]",
        };
    }
    if (tone === "amber") {
        return {
            border: "[border-color:var(--tier-caution)]",
            overlay: "[background:linear-gradient(180deg,_var(--tier-caution),_transparent)] [opacity:0.2]",
            title: "[color:var(--tier-caution)]",
        };
    }
    if (tone === "rose") {
        return {
            border: "[border-color:var(--tier-danger)]",
            overlay: "[background:linear-gradient(180deg,_var(--tier-danger),_transparent)] [opacity:0.18]",
            title: "[color:var(--tier-danger)]",
        };
    }
    if (tone === "violet") {
        return {
            border: "[border-color:var(--accent-secondary)]",
            overlay: "[background:linear-gradient(180deg,_var(--accent-secondary),_transparent)] [opacity:0.2]",
            title: "[color:var(--accent-secondary)]",
        };
    }
    return {
        border: "[border-color:var(--glass-border)]",
        overlay: "[background:linear-gradient(180deg,_var(--text-secondary),_transparent)] [opacity:0.16]",
        title: "[color:var(--text-secondary)]",
    };
}

function toTeamColorVarName(teamName: string): string {
    return `--venue-team-${teamName.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/(^-|-$)/g, "")}-color`;
}

export default function GlobalH2HReport({ data }: GlobalH2HReportProps): React.ReactElement {
    const payload = getGlobalH2HData(data);
    if (!payload) {
        return <EmptyState message="No Global H2H data available." />;
    }

    const { summary, team_a, team_b, venue_avg } = payload;
    const hasFormGuide = Boolean(payload.highlight_flags.has_form_guide);
    const lowSampleWarnings = payload.low_sample_warnings;

    React.useEffect(() => {
        const root = document.documentElement;
        const varNames = [team_a, team_b]
            .filter((team) => team.name && team.stats?.team_color)
            .map((team) => {
                const varName = toTeamColorVarName(team.name);
                root.style.setProperty(varName, team.stats.team_color);
                return varName;
            });

        return () => {
            for (const varName of varNames) {
                root.style.removeProperty(varName);
            }
        };
    }, [team_a, team_b]);

    const summaryWinPct = typeof summary.win_pct === "number" ? `${summary.win_pct}%` : summary.win_pct;

    return (
        <div className="mx-auto flex w-full max-w-5xl flex-col gap-7 px-4 py-2 sm:px-5 lg:px-6 animate-fade-in">
            <div className="flex items-center justify-center gap-2 text-sm font-bold tracking-[0.2em] uppercase [color:var(--text-secondary)]"><MapPin size={16} className="[color:var(--accent-primary)]" /><span>GLOBAL H2H</span></div>

            <div className="grid grid-cols-3 [background:var(--glass-bg)] [border:1px_solid_var(--glass-border)] rounded-xl overflow-hidden backdrop-blur-sm [box-shadow:var(--shadow-md)]">
                <SummaryItem label="MATCHES" value={summary.matches} icon={<BarChart3 size={16} />} />
                <SummaryItem
                    label={`${team_a.name} WIN %`}
                    value={summaryWinPct}
                    highlight
                    icon={<Trophy size={16} className="[color:var(--tier-caution)]" />}
                />
                <SummaryItem label="TIE/NR" value={summary.tie_nr} icon={<Dna size={16} />} />
            </div>

            {hasFormGuide && (
                <div className="grid grid-cols-1 gap-3 [background:var(--glass-bg)] [border:1px_solid_var(--glass-border)] rounded-xl p-4 md:grid-cols-2">
                    <FooterItem label={`${team_a.name} Last 5`} value={summary.last_5_home || "-"} />
                    <FooterItem label={`${team_b.name} Last 5`} value={summary.last_5_away || "-"} />
                </div>
            )}

            <div className="grid grid-cols-1 gap-7 md:grid-cols-2">
                <TeamCard team={team_a} isHome={true} />
                <TeamCard team={team_b} isHome={false} />
            </div>

            <div className="flex flex-col gap-4">
                <div className="[background:var(--glass-bg)] [border:1px_solid_var(--glass-border)] rounded-xl p-5 flex flex-wrap items-center justify-center gap-x-12 gap-y-4 backdrop-blur-sm [box-shadow:var(--shadow-md)]">
                    <div className="flex items-center gap-2 [color:var(--text-secondary)] text-sm font-bold tracking-tight">
                        <MapPin size={16} className="[color:var(--accent-primary)]" /> GLOBAL AVERAGES
                    </div>
                    <FooterItem label="1st Inn Avg" value={venue_avg.avg_1st} />
                    <FooterItem label="2nd Inn Avg" value={venue_avg.avg_2nd} />
                    <FooterItem label="Avg Winning Score" value={venue_avg.avg_win_score} />
                </div>

                {lowSampleWarnings.length > 0 && (
                    <div className="flex items-start justify-center gap-3 rounded-xl border-l-4 px-5 py-3 [background:var(--bg-elevated)] [border-top:1px_solid_var(--border-default)] [border-right:1px_solid_var(--border-default)] [border-bottom:1px_solid_var(--border-default)] [border-left-color:var(--tier-caution)]">
                        <AlertCircle size={14} className="mt-0.5 shrink-0 [color:var(--tier-caution)] opacity-85" />
                        <div className="flex flex-col gap-0.5">
                            <p className="text-[10px] font-bold [color:var(--tier-caution)] uppercase tracking-[0.15em]">
                                Accuracy Notice: Sparse Data Detected
                            </p>
                            <p className="text-[12px] [color:var(--text-secondary)] italic leading-tight">
                                Low sample for: <span className="[color:var(--text-primary)] font-medium">{lowSampleWarnings.join(", ")}</span>. Use with caution.
                            </p>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}

function SummaryItem({ label, value, highlight = false, icon }: SummaryItemProps): React.ReactElement {
    return (
        <div className="flex flex-col items-center justify-center border-r p-5 [border-color:var(--glass-border)] last:border-0">
            <span className={`text-[2rem] leading-none font-black font-numeric ${highlight ? "[color:var(--accent-primary)]" : "[color:var(--text-primary)]"}`}>
                {value}
            </span>
            <div className="mt-1.5 flex items-center gap-1.5">
                {icon}
                <span className="text-[10px] font-semibold tracking-[0.14em] uppercase [color:var(--text-secondary)]">{label}</span>
            </div>
        </div>
    );
}

function TeamCard({ team, isHome }: TeamCardProps): React.ReactElement {
    const stats = team.stats;
    if (!stats) {
        return <div className="rounded-md [background:var(--bg-surface)] p-7 text-center [border:1px_dashed_var(--border-default)] [color:var(--text-muted)]">No data for {team.name}</div>;
    }

    const tone = toneClasses(getTeamTone(stats.team_tone));
    const teamAccentClass = isHome
        ? "border-l-4 [border-left-color:var(--accent-primary)]"
        : "border-l-4 [border-left-color:var(--tier-danger)]";
    const roleLabel = isHome ? "HOME SIDE" : "AWAY SIDE";
    const teamHeadingStyle = {
        ...(stats.team_color ? { color: stats.team_color } : {}),
        textShadow: "0 0 1px var(--text-primary), 0 0 1px var(--text-primary)",
    };

    return (
        <div className={`relative overflow-hidden rounded-md border [background:var(--bg-surface)] backdrop-blur-sm [box-shadow:var(--shadow-lg)] ${tone.border} ${teamAccentClass}`}>
            <div className={`pointer-events-none absolute inset-x-0 top-0 h-16 opacity-25 ${tone.overlay}`} />

            <div className="flex flex-col items-center gap-3.5 border-b px-5 py-4 [border-color:var(--glass-border)]">
                <div className="text-[10px] font-bold tracking-[0.18em] uppercase [color:var(--text-secondary)]">
                    {roleLabel}
                </div>
                <h3 className="text-center text-[1.65rem] font-black tracking-tight uppercase" style={teamHeadingStyle}>
                    {team.name}
                </h3>

                <div className="flex justify-center gap-2">
                    <StatBadge icon={<Trophy size={12} className="[color:var(--tier-caution)]" />} label="Wins" value={stats.wins} />
                    <StatBadge icon={<ShieldCheck size={12} className="[color:var(--accent-primary)]" />} label="Def" value={stats.defended} />
                    <StatBadge icon={<Target size={12} className="[color:var(--tier-danger)]" />} label="Chs" value={stats.chased} />
                </div>
            </div>

            <div className="flex flex-col gap-5 px-5 py-5 sm:px-6">
                <div>
                    <SectionHeader label="BATTING 1ST" activeColor="[color:var(--tier-elite)]" />
                    <div className="mt-3 flex flex-col gap-1">
                        <DataRow label="Avg 1st Innings:" value={stats.bat1.avg} labelColor="[color:var(--text-secondary)]" />
                        <DataRow label="Highest:" value={stats.bat1.high} labelColor="[color:var(--text-secondary)]" />
                        <DataRow label="Lowest:" value={stats.bat1.low} labelColor="[color:var(--text-secondary)]" />
                        <DataRow label="Avg Winning Score:" value={stats.bat1.avg_win} labelColor="[color:var(--text-secondary)]" />
                        <DataRow label="Lowest Defended:" value={stats.bat1.low_def} labelColor="[color:var(--text-secondary)]" />
                    </div>
                </div>

                <div>
                    <SectionHeader label="CHASING" activeColor="[color:var(--accent-primary)]" />
                    <div className="mt-3 flex flex-col gap-1">
                        <DataRow label="Avg 2nd Innings:" value={stats.chase.avg} labelColor="[color:var(--text-secondary)]" />
                        <DataRow label="Highest Chased:" value={stats.chase.high} labelColor="[color:var(--text-secondary)]" />
                        <DataRow label="Avg Succ Chase:" value={stats.chase.succ} labelColor="[color:var(--text-secondary)]" />
                        <DataRow label="Avg Fail Chase:" value={stats.chase.fail} labelColor="[color:var(--text-secondary)]" />
                    </div>
                </div>
            </div>
        </div>
    );
}

function StatBadge({ icon, label, value }: StatBadgeProps): React.ReactElement {
    return (
        <div className="flex items-center gap-2 rounded-full px-3 py-1.5 [background:var(--glass-bg)] [border:1px_solid_var(--glass-border)] [box-shadow:var(--shadow-sm)] transition-colors hover:[background:var(--bg-hover)]">
            {icon}
            <span className="text-sm font-black leading-none font-numeric [color:var(--text-primary)]">{value}</span>
            <span className="mb-[-1px] text-[10px] font-bold leading-none tracking-[0.12em] uppercase [color:var(--text-secondary)]">{label}</span>
        </div>
    );
}

function SectionHeader({ label, activeColor }: { label: string; activeColor: string }): React.ReactElement {
    return (
        <div className="mb-1 border-b-2 pb-2 [border-color:var(--glass-border)]">
            <span className={`text-xs font-black tracking-[0.2em] uppercase ${activeColor}`}>{label}</span>
        </div>
    );
}

function DataRow({ label, value, labelColor }: { label: string; value: string; labelColor: string }): React.ReactElement {
    const renderValue = (entry: string): React.ReactNode => {
        if (entry === "" || entry === "-") {
            return "-";
        }

        const parts = entry.split(/(\[.*?\])/);
        if (parts.length === 1) {
            return entry;
        }

        return parts.map((part, index) => {
            if (part.startsWith("[") && part.endsWith("]")) {
                return (
                    <span key={index} className="ml-1.5 text-[0.8em] font-medium [color:var(--text-muted)]">
                        {part}
                    </span>
                );
            }
            return part;
        });
    };

    return (
        <div className="group grid grid-cols-[minmax(0,1fr)_minmax(max-content,auto)] items-start gap-x-4 border-b py-1.5 [border-color:var(--border-subtle)] last:border-0">
            <span className={`min-w-0 pl-1 text-[12px] font-medium leading-[1.3] tracking-tight transition-colors group-hover:[color:var(--text-primary)] ${labelColor}`}>
                {label}
            </span>
            <span className="min-w-0 break-words pr-3 text-right text-[12px] font-medium leading-[1.3] tracking-tight whitespace-normal font-numeric [color:var(--text-primary)]">
                {renderValue(value)}
            </span>
        </div>
    );
}

function FooterItem({ label, value }: { label: string; value: string }): React.ReactElement {
    return (
        <div className="flex items-center gap-2">
            <span className="text-xs font-semibold whitespace-nowrap [color:var(--text-secondary)]">{label}:</span>
            <span className="text-sm font-black tracking-tight font-numeric [color:var(--text-primary)]">{value}</span>
        </div>
    );
}
