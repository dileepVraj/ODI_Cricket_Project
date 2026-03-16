"use client";

import { AccessibleCombobox } from "@/components/common/AccessibleCombobox";

interface PlayerSearchProps {
    contextLabel: string;
    team: string;
    accentVar: string;
    isLoadingPlayers: boolean;
    isFull: boolean;
    players: string[];
    onSelectPlayer: (player: string) => void;
}

function resolvePlaceholder(args: {
    contextLabel: string;
    isFull: boolean;
    isLoadingPlayers: boolean;
    players: string[];
}): string {
    if (args.isLoadingPlayers) {
        return "Loading players...";
    }
    if (args.isFull) {
        return "XI complete";
    }
    if (args.players.length === 0) {
        return `No ${args.contextLabel} matches`;
    }
    return `Choose ${args.contextLabel} player`;
}

export default function PlayerSearch(props: PlayerSearchProps) {
    const {
        contextLabel,
        isLoadingPlayers,
        isFull,
        players,
        onSelectPlayer,
    } = props;

    if (isFull) {
        return null;
    }

    const options = players.map((player) => ({
        label: player,
        value: player,
    }));
    const helperText = isLoadingPlayers
        ? `Loading ${contextLabel.toLowerCase()} players...`
        : players.length === 0
            ? "No players available"
            : `${players.length} players available`;

    return (
        <div className="[display:flex] [flex-direction:column] [gap:10px] [margin-bottom:12px]">
            <AccessibleCombobox
                value=""
                onChange={onSelectPlayer}
                options={options}
                placeholder={resolvePlaceholder({
                    contextLabel,
                    isFull,
                    isLoadingPlayers,
                    players,
                })}
            />

            <p className="[font-size:0.74rem] [color:var(--text-muted)]">
                {helperText}
            </p>
        </div>
    );
}
