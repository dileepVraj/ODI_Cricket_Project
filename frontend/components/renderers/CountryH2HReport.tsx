"use client";

import React, { useEffect } from "react";
import { AlertCircle, BarChart3, Dna, MapPin, ShieldCheck, Target, Trophy } from "lucide-react";
import EmptyState from "@/components/common/EmptyState";
import { TeamTone, getTeamTone } from "@/lib/comparison-types";
import { CountryH2HData, getCountryH2HData } from "@/lib/country-h2h-types";

interface SummaryItemProps {
    label: string;
    value: string | number;
    highlight?: boolean;
    icon: React.ReactNode;
}

interface TeamCardProps {
    team: CountryH2HData["team_a"];
    isHome?: boolean;
}

interface StatBadgeProps {
    icon: React.ReactNode;
    label: string;
    value: string | number;
}

interface SectionHeaderProps {
    label: string;
    activeColor: string;
}

interface DataRowProps {
    label: string;
    value: string;
    labelColor: string;
}

interface FooterItemProps {
    label: string;
    value: string;
}

interface CountryH2HReportProps {
    data: Record<string, unknown>;
    averagesTitle?: string;
}

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

export default function CountryH2HReport({
    data,
    averagesTitle = "COUNTRY AVERAGES",
}: CountryH2HReportProps): React.ReactElement {
    const payload = getCountryH2HData(data);
    if (!payload) {
        return <EmptyState message="No country H2H data available." />;
    }

    const { summary, team_a, team_b, venue_avg } = payload;
    const hasFormGuide = Boolean(payload.highlight_flags?.has_form_guide);
    const lowSampleWarnings = payload.low_sample_warnings ?? [];

    useEffect(() => {
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

    return (
        <div className="mx-auto flex w-full max-w-5xl flex-col gap-7 px-4 py-2 sm:px-5 lg:px-6 animate-fade-in">
            <div className="grid grid-cols-3 [background:var(--glass-bg)] [border:1px_solid_var(--glass-border)] rounded-xl overflow-hidden backdrop-blur-sm [box-shadow:var(--shadow-md)]">
                <SummaryItem label="MATCHES" value={summary.matches} icon={<BarChart3 size={16} />} />
                <SummaryItem
                    label={`${team_a.name} WIN %`}
                    value={`${summary.win_pct}%`}
                    highlight
                    icon={<Trophy size={16} className="[color:var(--tier-caution)]" />}
                />
                <SummaryItem label="TIE/NR" value={summary.tie_nr} icon={<Dna size={16} />} />
            </div>

            {hasFormGuide && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 [background:var(--glass-bg)] [border:1px_solid_var(--glass-border)] rounded-xl p-4">
                    <FooterItem label={`${team_a.name} Last 5`} value={summary.last_5_home || "-"} />
                    <FooterItem label={`${team_b.name} Last 5`} value={summary.last_5_away || "-"} />
                </div>
            )}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-7">
                <TeamCard team={team_a} isHome={true} />
                <TeamCard team={team_b} isHome={false} />
            </div>

            <div className="flex flex-col gap-4">
                <div className="[background:var(--glass-bg)] [border:1px_solid_var(--glass-border)] rounded-xl p-5 flex flex-wrap justify-center items-center gap-x-12 gap-y-4 backdrop-blur-sm [box-shadow:var(--shadow-md)]">
                    <div className="flex items-center gap-2 [color:var(--text-secondary)] text-sm font-bold tracking-tight">
                        <MapPin size={16} className="[color:var(--accent-primary)]" /> {averagesTitle}
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
        <div className="flex flex-col items-center justify-center p-5 border-r [border-color:var(--glass-border)] last:border-0">
            <span className={`text-[2rem] leading-none font-black font-numeric ${highlight ? "[color:var(--accent-primary)]" : "[color:var(--text-primary)]"}`}>
                {value}
            </span>
            <div className="flex items-center gap-1.5 mt-1.5">
                {icon}
                <span className="text-[10px] font-semibold tracking-[0.14em] [color:var(--text-secondary)] uppercase">{label}</span>
            </div>
        </div>
    );
}

function TeamCard({ team, isHome }: TeamCardProps): React.ReactElement {
    const stats = team.stats;
    const tone = toneClasses(getTeamTone(stats.team_tone));
    const teamAccentClass = isHome
        ? "border-l-4 [border-left-color:var(--accent-primary)]"
        : "border-l-4 [border-left-color:var(--tier-danger)]";
    const teamHeadingStyle: React.CSSProperties = {
        ...(stats.team_color ? { color: stats.team_color } : {}),
        textShadow: "0 0 1px var(--text-primary), 0 0 1px var(--text-primary)",
    };

    return (
        <div className={`relative [background:var(--bg-surface)] border rounded-md overflow-hidden backdrop-blur-sm [box-shadow:var(--shadow-lg)] ${tone.border} ${teamAccentClass}`}>
            <div className={`pointer-events-none absolute inset-x-0 top-0 h-16 opacity-25 ${tone.overlay}`} />
            <div className="border-b [border-color:var(--glass-border)] px-5 py-4 flex flex-col items-center gap-3.5">
                <h3 className="text-center text-[1.65rem] font-black tracking-tight uppercase" style={teamHeadingStyle}>{team.name}</h3>
                <div className="flex justify-center gap-2">
                    <StatBadge icon={<Trophy size={12} className="[color:var(--tier-caution)]" />} label="Wins" value={stats.wins} />
                    <StatBadge icon={<ShieldCheck size={12} className="[color:var(--accent-primary)]" />} label="Def" value={stats.defended} />
                    <StatBadge icon={<Target size={12} className="[color:var(--tier-danger)]" />} label="Chs" value={stats.chased} />
                </div>
            </div>
            <div className="px-5 py-5 sm:px-6 flex flex-col gap-5">
                <div>
                    <SectionHeader label="BATTING 1ST" activeColor="[color:var(--tier-elite)]" />
                    <div className="flex flex-col gap-1 mt-3">
                        <DataRow label="Avg Score:" value={stats.bat1.avg} labelColor="[color:var(--text-secondary)]" />
                        <DataRow label="High / Low:" value={`${stats.bat1.high} / ${stats.bat1.low}`} labelColor="[color:var(--text-secondary)]" />
                        <DataRow label="Avg Win Score:" value={stats.bat1.avg_win} labelColor="[color:var(--text-secondary)]" />
                        <DataRow label="Lowest Defended:" value={stats.bat1.low_def} labelColor="[color:var(--text-secondary)]" />
                    </div>
                </div>

                <div>
                    <SectionHeader label="CHASING" activeColor="[color:var(--accent-primary)]" />
                    <div className="flex flex-col gap-1 mt-3">
                        <DataRow label="Avg Score:" value={stats.chase.avg} labelColor="[color:var(--text-secondary)]" />
                        <DataRow label="Highest Chased:" value={stats.chase.high} labelColor="[color:var(--text-secondary)]" />
                        <DataRow label="Avg Succ. Chase:" value={stats.chase.succ} labelColor="[color:var(--text-secondary)]" />
                        <DataRow label="Avg Fail Chase:" value={stats.chase.fail} labelColor="[color:var(--text-secondary)]" />
                    </div>
                </div>
            </div>
        </div>
    );
}

function StatBadge({ icon, label, value }: StatBadgeProps): React.ReactElement {
    return (
        <div className="flex items-center gap-2 [background:var(--glass-bg)] px-3 py-1.5 rounded-full [border:1px_solid_var(--glass-border)] [box-shadow:var(--shadow-sm)] hover:[background:var(--bg-hover)] transition-colors">
            {icon}
            <span className="text-sm font-black [color:var(--text-primary)] font-numeric leading-none">{value}</span>
            <span className="text-[10px] font-bold [color:var(--text-secondary)] uppercase tracking-[0.12em] leading-none mb-[-1px]">{label}</span>
        </div>
    );
}

function SectionHeader({ label, activeColor }: SectionHeaderProps): React.ReactElement {
    return (
        <div className="border-b-2 [border-color:var(--glass-border)] pb-2 mb-1">
            <span className={`text-xs font-black tracking-[0.2em] uppercase ${activeColor}`}>{label}</span>
        </div>
    );
}

function DataRow({ label, value, labelColor }: DataRowProps): React.ReactElement {
    const renderValue = (displayValue: string): string | React.ReactNode[] => {
        if (displayValue === "" || displayValue === "-") {
            return "-";
        }

        const parts = displayValue.split(/(\[.*?\])/);
        if (parts.length === 1) {
            return displayValue;
        }

        return parts.map((part, index) => {
            if (part.startsWith("[") && part.endsWith("]")) {
                return (
                    <span key={index} className="text-[0.8em] [color:var(--text-muted)] ml-1.5 font-medium">
                        {part}
                    </span>
                );
            }
            return part;
        });
    };

    return (
        <div className="grid grid-cols-[minmax(0,1fr)_minmax(max-content,auto)] items-start gap-x-4 py-1.5 border-b [border-color:var(--border-subtle)] last:border-0 group">
            <span className={`min-w-0 pl-1 text-[12px] font-medium tracking-tight leading-[1.3] ${labelColor} group-hover:[color:var(--text-primary)] transition-colors`}>
                {label}
            </span>
            <span className="min-w-0 pr-3 text-[12px] leading-[1.3] font-medium [color:var(--text-primary)] tracking-tight text-right whitespace-normal break-words">
                {renderValue(value)}
            </span>
        </div>
    );
}

function FooterItem({ label, value }: FooterItemProps): React.ReactElement {
    return (
        <div className="flex items-center gap-2">
            <span className="text-xs font-semibold [color:var(--text-secondary)] whitespace-nowrap">{label}:</span>
            <span className="text-sm font-black [color:var(--text-primary)] font-numeric tracking-tight">{value}</span>
        </div>
    );
}
