"use client";

import { Activity } from "lucide-react";
import EmptyState from "@/components/common/EmptyState";
import MatchAuditSection from "./MatchAuditSection";
import StatPill from "@/components/phase-analysis/StatPill";
import FilterCriteriaNotice from "@/components/phase-analysis/FilterCriteriaNotice";
import PhaseTable from "@/components/phase-analysis/PhaseTable";
import GlobalHabitsCard from "@/components/phase-analysis/GlobalHabitsCard";

interface PhaseData {
    avg: number;
    n: number;
    wkts: number;
}

interface InningsStats {
    pp: PhaseData;
    mid: PhaseData;
    dth: PhaseData;
    total: PhaseData;
}

interface PhaseAnalysisData {
    stadium_id?: string;
    match_count?: number;
    years?: number;
    filter_criteria?: {
        min_first_innings_balls?: number;
        min_first_innings_overs?: number;
        keep_all_outs?: boolean;
        keep_successful_chases?: boolean;
        drop_short_no_result_only?: boolean;
    };
    baseline?: { "1"?: InningsStats; "2"?: InningsStats };
    home_at_venue?: { team: string; stats: { "1"?: InningsStats; "2"?: InningsStats } } | null;
    away_at_venue?: { team: string; stats: { "1"?: InningsStats; "2"?: InningsStats } } | null;
    global_habits?: {
        start_year?: number | string;
        bat_first?: Record<string, number | undefined>;
        chasing?: Record<string, number | undefined>;
        scenario_rows?: {
            bat_first?: { label: string; home_value?: number; away_value?: number; higher_better?: boolean; diff_text?: string; diff_tone?: "success" | "danger" | "muted" }[];
            chasing?: { label: string; home_value?: number; away_value?: number; higher_better?: boolean; diff_text?: string; diff_tone?: "success" | "danger" | "muted" }[];
        };
        home?: { pp_rr: number; mid_rr: number; dth_rr: number; avg_score: number };
        away?: { pp_rr: number; mid_rr: number; dth_rr: number; avg_score: number };
    } | null;
    match_audit?: Record<string, unknown>[];
    MATCH_IDS?: string;
}

interface PhaseAnalysisCardProps {
    data: PhaseAnalysisData;
}

export default function PhaseAnalysisCard({ data }: PhaseAnalysisCardProps) {
    if (!data || typeof data !== "object") {
        return <EmptyState message="No phase analysis data available." />;
    }

    const stadiumId = String(data.stadium_id ?? "Unknown");
    const stadiumLabel =
        stadiumId.split("_").slice(1).join(" ").replace(/\b\w/g, (c) => c.toUpperCase()) || stadiumId;
    const matchCount = data.match_count ?? 0;
    const years = data.years ?? 5;

    return (
        <div className="[display:flex] [flex-direction:column] [gap:20px]">
            <div className="glass-card [padding:18px_22px] [display:flex] [align-items:center] [gap:16px] [flex-wrap:wrap] [border-left:4px_solid_var(--accent-primary)]">
                <div className="[width:40px] [height:40px] [border-radius:var(--radius-md)] [background:var(--accent-glow)] [display:flex] [align-items:center] [justify-content:center]">
                    <Activity size={20} className="[color:var(--accent-primary)]" />
                </div>

                <div className="[flex:1]">
                    <div className="[font-size:0.7rem] [text-transform:uppercase] [letter-spacing:0.06em] [color:var(--text-disabled)] [font-weight:600]">
                        Phase Analysis
                    </div>
                    <div className="[font-size:1.1rem] [font-weight:800] [color:var(--text-primary)]">{stadiumLabel}</div>
                </div>

                <div className="[display:flex] [gap:20px]">
                    <StatPill label="Matches" value={String(matchCount)} />
                    <StatPill label="Period" value={`${years}yr`} />
                </div>
            </div>

            {data.filter_criteria && <FilterCriteriaNotice criteria={data.filter_criteria} />}

            {data.baseline && (
                <PhaseTable
                    title="Venue Baseline (All Teams)"
                    stats={data.baseline}
                    accentColor="var(--accent-tertiary)"
                />
            )}

            {data.home_at_venue?.stats && (
                <PhaseTable
                    title={`${data.home_at_venue.team} at this Venue`}
                    stats={data.home_at_venue.stats}
                    accentColor="var(--accent-primary)"
                />
            )}

            {data.away_at_venue?.stats && (
                <PhaseTable
                    title={`${data.away_at_venue.team} at this Venue`}
                    stats={data.away_at_venue.stats}
                    accentColor="var(--accent-secondary)"
                />
            )}

            {data.global_habits && (
                <GlobalHabitsCard
                    habits={data.global_habits}
                    homeTeam={data.home_at_venue?.team}
                    awayTeam={data.away_at_venue?.team}
                />
            )}

            {data.match_audit && <MatchAuditSection records={data.match_audit} />}
        </div>
    );
}
