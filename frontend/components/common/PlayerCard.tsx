import { User } from "lucide-react";
import { Badge } from "./Badge";
import { StatPill } from "./StatPill";

export interface PlayerStatItem {
    label: string;
    value: string;
}

interface PlayerCardProps {
    name: string;
    team?: string;
    role?: string;
    stats: PlayerStatItem[];
}

export function PlayerCard({ name, team, role, stats }: PlayerCardProps) {
    return (
        <div className="player-card">
            <div className="player-card-header">
                <div className="player-card-avatar">
                    <User size={24} aria-hidden="true" />
                </div>
                <div>
                    <p className="player-card-name">{name}</p>
                    <div className="player-card-meta">
                        {team && <Badge variant="strong">{team}</Badge>}
                        {role && <span className="player-card-role">{role}</span>}
                    </div>
                </div>
            </div>
            {stats.length > 0 && (
                <div className="player-card-stats">
                    {stats.map((s) => (
                        <StatPill key={s.label} label={s.label} value={s.value} />
                    ))}
                </div>
            )}
        </div>
    );
}
