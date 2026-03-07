"use client";

import { Download, Trash2, Users } from "lucide-react";

interface PositionSelectorProps {
    contextLabel: string;
    team: string;
    maxPlayers: number;
    playerCount: number;
    validTeam: boolean;
    isLoadingPlayers: boolean;
    hasPlayers: boolean;
    loadError: string | null;
    onLoadSquad: () => Promise<void>;
    onClearAll: () => void;
    accentVar: string;
}

function resolveBadgeClass(playerCount: number, maxPlayers: number): string {
    if (playerCount >= maxPlayers) {
        return "badge-elite";
    }
    if (playerCount > 0) {
        return "badge-strong";
    }
    return "badge-caution";
}

export default function PositionSelector({
    contextLabel,
    team,
    maxPlayers,
    playerCount,
    validTeam,
    isLoadingPlayers,
    hasPlayers,
    loadError,
    onLoadSquad,
    onClearAll,
    accentVar,
}: PositionSelectorProps) {
    return (
        <div className="[display:flex] [flex-direction:column] [gap:10px] [margin-bottom:12px]">
            <div className="[display:flex] [justify-content:space-between] [align-items:center] [gap:12px]">
                <div className="[display:flex] [align-items:center] [gap:8px] [flex-wrap:wrap]">
                    <Users size={16} className={`[color:${accentVar}]`} />
                    <span className="[font-size:0.9rem] [font-weight:700] [color:var(--text-primary)]">
                        {contextLabel} XI
                    </span>
                    <span className={`badge ${resolveBadgeClass(playerCount, maxPlayers)} [font-size:0.7rem]`}>
                        {playerCount}/{maxPlayers}
                    </span>
                </div>

                {validTeam ? (
                    <span className={`[font-size:0.75rem] [font-weight:600] [color:${accentVar}]`}>
                        {team}
                    </span>
                ) : null}
            </div>

            {!validTeam ? (
                <div className="[padding:20px] [text-align:center] [color:var(--text-muted)] [font-size:0.82rem]">
                    Select a team from the Context Bar above.
                </div>
            ) : (
                <div className="[display:flex] [flex-direction:column] [gap:10px]">
                    <div className="[display:flex] [gap:6px] [flex-wrap:wrap]">
                        <button
                            type="button"
                            className="btn-ghost [font-size:0.75rem] [padding:4px_10px]"
                            onClick={onLoadSquad}
                            disabled={isLoadingPlayers}
                            aria-label={`Load the ${team} squad into the selected XI`}
                        >
                            <Download size={12} />
                            Load Squad
                        </button>

                        {hasPlayers ? (
                            <button
                                type="button"
                                className="btn-ghost [font-size:0.75rem] [padding:4px_10px] [color:var(--tier-danger)]"
                                onClick={onClearAll}
                                aria-label={`Clear all selected players for ${team}`}
                            >
                                <Trash2 size={12} />
                                Clear
                            </button>
                        ) : null}
                    </div>

                    {loadError ? (
                        <div
                            role="alert"
                            className="[font-size:0.74rem] [color:var(--tier-caution)]"
                        >
                            {loadError}
                        </div>
                    ) : null}
                </div>
            )}
        </div>
    );
}
