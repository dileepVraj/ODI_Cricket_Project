"use client";

import { Search } from "lucide-react";
import { AccessibleCombobox } from "@/components/common/AccessibleCombobox";

interface PlayerSearchProps {
    contextLabel: string;
    team: string;
    accentVar: string;
    isLoadingPlayers: boolean;
    isFull: boolean;
    availablePlayerCount: number;
    searchTerm: string;
    filteredPlayers: string[];
    onSearchTermChange: (value: string) => void;
    onSelectPlayer: (player: string) => void;
}

function resolvePlaceholder(args: {
    contextLabel: string;
    isFull: boolean;
    isLoadingPlayers: boolean;
    filteredPlayers: string[];
}): string {
    if (args.isLoadingPlayers) {
        return "Loading players...";
    }
    if (args.isFull) {
        return "XI complete";
    }
    if (args.filteredPlayers.length === 0) {
        return `No ${args.contextLabel} matches`;
    }
    return `Choose ${args.contextLabel} player`;
}

export default function PlayerSearch({
    contextLabel,
    team,
    accentVar,
    isLoadingPlayers,
    isFull,
    availablePlayerCount,
    searchTerm,
    filteredPlayers,
    onSearchTermChange,
    onSelectPlayer,
}: PlayerSearchProps) {
    if (isFull) {
        return null;
    }

    const options = filteredPlayers.slice(0, 50).map((player) => ({
        label: player,
        value: player,
    }));
    const helperText = isLoadingPlayers
        ? `Loading ${contextLabel.toLowerCase()} players...`
        : filteredPlayers.length === 0 && searchTerm
            ? "No players match this search."
            : `${filteredPlayers.length} of ${availablePlayerCount} players available`;

    return (
        <div className="[display:flex] [flex-direction:column] [gap:10px] [margin-bottom:12px]">
            <div className="[display:flex] [align-items:center] [gap:8px]">
                <Search size={14} className={`[color:${accentVar}] [flex-shrink:0]`} />
                <input
                    type="text"
                    value={searchTerm}
                    onChange={(event) => onSearchTermChange(event.target.value)}
                    placeholder={`Filter ${team} players`}
                    className="context-input"
                    aria-label={`Filter ${team} player options`}
                />
            </div>

            <AccessibleCombobox
                value=""
                onChange={onSelectPlayer}
                options={options}
                placeholder={resolvePlaceholder({
                    contextLabel,
                    isFull,
                    isLoadingPlayers,
                    filteredPlayers,
                })}
            />

            <p className="[font-size:0.74rem] [color:var(--text-muted)]">
                {helperText}
            </p>
        </div>
    );
}
