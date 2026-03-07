"use client";

import { Award, Target, User } from "lucide-react";
import EmptyState from "@/components/common/EmptyState";
import QuickLinks from "@/components/navigation/QuickLinks";
import { useAppContext } from "@/lib/context";
import { PlayerPayloadFragment, toPlayerPayloadFragment } from "@/lib/types";

interface PlayerProfileCardProps {
    data: Record<string, unknown>;
}

type SectionTone = "primary" | "secondary" | "tertiary";

function toneBarClass(tone: SectionTone): string {
    if (tone === "primary") return "[background:var(--accent-primary)]";
    if (tone === "secondary") return "[background:var(--accent-secondary)]";
    return "[background:var(--accent-tertiary)]";
}

export default function PlayerProfileCard({ data }: PlayerProfileCardProps) {
    const { activeFormat } = useAppContext();

    if (!data || typeof data !== "object") {
        return <EmptyState message="No player data available." />;
    }

    const name = String(data["player_name"] ?? data["name"] ?? data["Player"] ?? "Unknown");
    const team = String(data["team"] ?? data["Team"] ?? "");
    const role = String(data["role"] ?? data["Role"] ?? "");

    const battingObj = toPlayerPayloadFragment(data["batting"]);
    const bowlingObj = toPlayerPayloadFragment(data["bowling"]);
    const venueCtx = toPlayerPayloadFragment(data["venue_stats"]);
    const opponentCtx = toPlayerPayloadFragment(data["vs_opponent_stats"]);

    const pickStats = (obj: PlayerPayloadFragment | null, keys: string[]): [string, unknown][] => {
        if (!obj) return [];
        const out: [string, unknown][] = [];
        for (const key of keys) {
            if (key in obj) out.push([key, obj[key]]);
        }
        return out;
    };

    const battingStatsNested = pickStats(battingObj, [
        "innings",
        "runs",
        "average",
        "strike_rate",
        "centuries",
        "fifties",
        "highest_score",
    ]);
    const bowlingStatsNested = pickStats(bowlingObj, ["innings", "wickets", "average", "economy", "best_figures"]);

    const contextToStats = (ctx: PlayerPayloadFragment | null): [string, unknown][] => {
        if (!ctx) return [];
        const bat = toPlayerPayloadFragment(ctx["batting"]);
        const bowl = toPlayerPayloadFragment(ctx["bowling"]);
        return [
            ...pickStats(bat, ["innings", "runs", "average", "strike_rate", "highest_score", "centuries", "fifties"]),
            ...pickStats(bowl, ["innings", "wickets", "average", "economy", "best_figures"]),
        ];
    };

    const batKeys = [
        "innings",
        "runs",
        "average",
        "strike_rate",
        "hundreds",
        "fifties",
        "highest_score",
        "not_outs",
        "balls_faced",
        "fours",
        "sixes",
        "Innings",
        "Runs",
        "Average",
        "SR",
        "100s",
        "50s",
        "HS",
        "NO",
    ];
    const bowlKeys = [
        "wickets",
        "bowling_avg",
        "economy",
        "bowling_sr",
        "best_bowling",
        "overs",
        "maiden",
        "Wickets",
        "Bowl_Avg",
        "Econ",
        "Bowl_SR",
        "Best",
    ];

    const displayEntries = Object.entries(data).filter(
        ([key]) =>
            key !== "player_name" &&
            key !== "name" &&
            key !== "Player" &&
            key !== "team" &&
            key !== "Team" &&
            key !== "role" &&
            key !== "Role" &&
            key !== "MATCH_IDS" &&
            key !== "raw_matches" &&
            typeof data[key] !== "object"
    );

    const battingStatsFlat = displayEntries.filter(([k]) =>
        batKeys.some((bk) => k.toLowerCase().includes(bk.toLowerCase()))
    );
    const bowlingStatsFlat = displayEntries.filter(([k]) =>
        bowlKeys.some((bk) => k.toLowerCase().includes(bk.toLowerCase()))
    );
    const otherStats = displayEntries.filter(
        ([k]) =>
            !batKeys.some((bk) => k.toLowerCase().includes(bk.toLowerCase())) &&
            !bowlKeys.some((bk) => k.toLowerCase().includes(bk.toLowerCase()))
    );

    const battingStats = battingStatsNested.length > 0 ? battingStatsNested : battingStatsFlat;
    const bowlingStats = bowlingStatsNested.length > 0 ? bowlingStatsNested : bowlingStatsFlat;
    const vsOpponentStats = contextToStats(opponentCtx);
    const atVenueStats = contextToStats(venueCtx);

    return (
        <div className="[display:flex] [flex-direction:column] [gap:20px]">
            <div className="glass-card [padding:24px] [display:flex] [align-items:center] [gap:20px] [border:1px_solid_var(--border-accent)]">
                <div className="[width:56px] [height:56px] [border-radius:50%] [background:linear-gradient(135deg,_var(--accent-primary),_var(--accent-secondary))] [display:flex] [align-items:center] [justify-content:center] [flex-shrink:0]">
                    <User size={28} className="[color:var(--text-primary)]" />
                </div>

                <div className="[flex:1]">
                    <h3 className="[font-size:1.3rem] [font-weight:800] [color:var(--text-primary)] [margin-bottom:4px]">{name}</h3>
                    <div className="[display:flex] [gap:8px] [align-items:center] [flex-wrap:wrap]">
                        {team && <span className="badge badge-strong [font-size:0.7rem]">{team}</span>}
                        {role && (
                            <span className="[padding:2px_10px] [border-radius:9999px] [background:var(--bg-active)] [color:var(--text-muted)] [font-size:0.7rem] [font-weight:500]">
                                {role}
                            </span>
                        )}
                    </div>
                </div>
            </div>

            {battingStats.length > 0 && (
                <StatSection title="Batting" icon={<Award size={14} />} stats={battingStats} tone="primary" />
            )}

            {bowlingStats.length > 0 && (
                <StatSection title="Bowling" icon={<Target size={14} />} stats={bowlingStats} tone="secondary" />
            )}

            {vsOpponentStats.length > 0 && (
                <StatSection title="Vs Opponent" icon={<Target size={14} />} stats={vsOpponentStats} tone="tertiary" />
            )}

            {atVenueStats.length > 0 && (
                <StatSection title="At Venue" icon={<Award size={14} />} stats={atVenueStats} tone="tertiary" />
            )}

            {otherStats.length > 0 && (
                <StatSection title="Details" icon={<User size={14} />} stats={otherStats} tone="tertiary" />
            )}

            {activeFormat && (
                <QuickLinks
                    links={[
                        { label: "View H2H", href: "/:format/rivalry/global_h2h?team_b=" + encodeURIComponent(team) },
                        { label: "Add to Squad", href: "/:format/squad_battle/compare_squads" },
                    ]}
                />
            )}
        </div>
    );
}

function StatSection({
    title,
    icon,
    stats,
    tone,
}: {
    title: string;
    icon: React.ReactNode;
    stats: [string, unknown][];
    tone: SectionTone;
}) {
    return (
        <div>
            <div className="[display:flex] [align-items:center] [gap:8px] [margin-bottom:10px]">
                <div className={`[width:4px] [height:16px] [border-radius:2px] ${toneBarClass(tone)}`} />
                <span className="[font-size:0.78rem] [font-weight:700] [color:var(--text-secondary)] [text-transform:uppercase] [letter-spacing:0.06em] [display:inline-flex] [align-items:center] [gap:6px]">
                    {icon} {title}
                </span>
            </div>

            <div className="[display:grid] [grid-template-columns:repeat(auto-fill,_minmax(140px,_1fr))] [gap:8px]">
                {stats.map(([key, val]) => (
                    <div key={key} className="[padding:12px_14px] [background:var(--bg-elevated)] [border-radius:var(--radius-md)] [border:1px_solid_var(--border-subtle)]">
                        <div className="[font-size:0.65rem] [text-transform:uppercase] [letter-spacing:0.05em] [color:var(--text-disabled)] [font-weight:600] [margin-bottom:3px]">
                            {key.replace(/_/g, " ")}
                        </div>
                        <div className="[font-size:1.1rem] [font-weight:700] [color:var(--text-primary)] font-numeric">
                            {val === null || val === undefined ? "-" : String(val)}
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}
