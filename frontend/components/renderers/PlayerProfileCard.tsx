/**
 * PlayerProfileCard.tsx — Player Deep-Dive Profile
 * 
 * Used by: player_profile (output_type: "profile_card")
 * 
 * Renders player stats in a premium card layout with:
 *   - Player header: name, team, role badge
 *   - Key stat grid: Innings, Average, SR, 100s, etc.
 *   - Handles both batting and bowling stats
 */
"use client";

import { User, Award, Target } from "lucide-react";

interface PlayerProfileCardProps {
    data: Record<string, unknown>;
}

export default function PlayerProfileCard({ data }: PlayerProfileCardProps) {
    if (!data || typeof data !== "object") {
        return (
            <div style={{ padding: "20px", textAlign: "center", color: "var(--text-muted)" }}>
                No player data available.
            </div>
        );
    }

    const name = String(data["player_name"] ?? data["name"] ?? data["Player"] ?? "Unknown");
    const team = String(data["team"] ?? data["Team"] ?? "");
    const role = String(data["role"] ?? data["Role"] ?? "");

    // Separate batting and bowling stats
    const batKeys = ["innings", "runs", "average", "strike_rate", "hundreds", "fifties",
        "highest_score", "not_outs", "balls_faced", "fours", "sixes",
        "Innings", "Runs", "Average", "SR", "100s", "50s", "HS", "NO"];
    const bowlKeys = ["wickets", "bowling_avg", "economy", "bowling_sr", "best_bowling",
        "overs", "maiden", "Wickets", "Bowl_Avg", "Econ", "Bowl_SR", "Best"];

    const displayEntries = Object.entries(data).filter(
        ([key]) => key !== "player_name" && key !== "name" && key !== "Player" &&
            key !== "team" && key !== "Team" && key !== "role" && key !== "Role" &&
            key !== "MATCH_IDS" && key !== "raw_matches" &&
            typeof data[key] !== "object"
    );

    const battingStats = displayEntries.filter(([k]) =>
        batKeys.some((bk) => k.toLowerCase().includes(bk.toLowerCase()))
    );
    const bowlingStats = displayEntries.filter(([k]) =>
        bowlKeys.some((bk) => k.toLowerCase().includes(bk.toLowerCase()))
    );
    const otherStats = displayEntries.filter(([k]) =>
        !batKeys.some((bk) => k.toLowerCase().includes(bk.toLowerCase())) &&
        !bowlKeys.some((bk) => k.toLowerCase().includes(bk.toLowerCase()))
    );

    return (
        <div style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
            {/* ── Player Header ────────────────────────────────────────────── */}
            <div
                className="glass-card"
                style={{
                    padding: "24px",
                    display: "flex",
                    alignItems: "center",
                    gap: "20px",
                    border: "1px solid var(--border-accent)",
                }}
            >
                {/* Avatar */}
                <div style={{
                    width: 56, height: 56, borderRadius: "50%",
                    background: "linear-gradient(135deg, var(--accent-primary), var(--accent-secondary))",
                    display: "flex", alignItems: "center", justifyContent: "center",
                    flexShrink: 0,
                }}>
                    <User size={28} style={{ color: "white" }} />
                </div>

                <div style={{ flex: 1 }}>
                    <h3 style={{
                        fontSize: "1.3rem", fontWeight: 800, color: "var(--text-primary)",
                        marginBottom: "4px",
                    }}>
                        {name}
                    </h3>
                    <div style={{ display: "flex", gap: "8px", alignItems: "center", flexWrap: "wrap" }}>
                        {team && (
                            <span className="badge badge-strong" style={{ fontSize: "0.7rem" }}>{team}</span>
                        )}
                        {role && (
                            <span style={{
                                padding: "2px 10px", borderRadius: "9999px",
                                background: "var(--bg-active)", color: "var(--text-muted)",
                                fontSize: "0.7rem", fontWeight: 500,
                            }}>
                                {role}
                            </span>
                        )}
                    </div>
                </div>
            </div>

            {/* ── Batting Stats ────────────────────────────────────────────── */}
            {battingStats.length > 0 && (
                <StatSection
                    title="Batting"
                    icon={<Award size={14} />}
                    stats={battingStats}
                    color="var(--accent-primary)"
                />
            )}

            {/* ── Bowling Stats ────────────────────────────────────────────── */}
            {bowlingStats.length > 0 && (
                <StatSection
                    title="Bowling"
                    icon={<Target size={14} />}
                    stats={bowlingStats}
                    color="var(--accent-secondary)"
                />
            )}

            {/* ── Other Stats ──────────────────────────────────────────────── */}
            {otherStats.length > 0 && (
                <StatSection
                    title="Details"
                    icon={<User size={14} />}
                    stats={otherStats}
                    color="var(--accent-tertiary)"
                />
            )}
        </div>
    );
}

// ── Stat Section Sub-Component ──────────────────────────────────────────

function StatSection({
    title,
    icon,
    stats,
    color,
}: {
    title: string;
    icon: React.ReactNode;
    stats: [string, unknown][];
    color: string;
}) {
    return (
        <div>
            <div style={{
                display: "flex", alignItems: "center", gap: "8px", marginBottom: "10px",
            }}>
                <div style={{
                    width: 4, height: 16, borderRadius: 2, background: color,
                }} />
                <span style={{
                    fontSize: "0.78rem", fontWeight: 700, color: "var(--text-secondary)",
                    textTransform: "uppercase", letterSpacing: "0.06em",
                    display: "inline-flex", alignItems: "center", gap: "6px",
                }}>
                    {icon} {title}
                </span>
            </div>
            <div style={{
                display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(140px, 1fr))",
                gap: "8px",
            }}>
                {stats.map(([key, val]) => (
                    <div key={key} style={{
                        padding: "12px 14px", background: "var(--bg-elevated)",
                        borderRadius: "var(--radius-md)", border: "1px solid var(--border-subtle)",
                    }}>
                        <div style={{
                            fontSize: "0.65rem", textTransform: "uppercase", letterSpacing: "0.05em",
                            color: "var(--text-disabled)", fontWeight: 600, marginBottom: "3px",
                        }}>
                            {key.replace(/_/g, " ")}
                        </div>
                        <div style={{
                            fontSize: "1.1rem", fontWeight: 700, color: "var(--text-primary)",
                            fontVariantNumeric: "tabular-nums",
                        }}>
                            {val === null || val === undefined ? "—" : String(val)}
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}
