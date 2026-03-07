"use client";

import { X } from "lucide-react";

interface PlayerListProps {
    accentVar: string;
    selectedPlayers: string[];
    onRemovePlayer: (player: string) => void;
}

export default function PlayerList({
    accentVar,
    selectedPlayers,
    onRemovePlayer,
}: PlayerListProps) {
    if (selectedPlayers.length === 0) {
        return (
            <div className="[padding:12px] [text-align:center] [color:var(--text-muted)] [font-size:0.78rem] [font-style:italic]">
                No players selected. Filter the squad and choose from the combobox above.
            </div>
        );
    }

    return (
        <div className="[display:flex] [flex-direction:column] [gap:4px] [min-height:40px]">
            {selectedPlayers.map((player, index) => (
                <div
                    key={player}
                    className={`animate-fade-in [display:flex] [align-items:center] [gap:8px] [padding:5px_10px] [background:var(--bg-active)] [border-radius:var(--radius-sm)] [font-size:0.8rem] [border-left:3px_solid_${accentVar}]`}
                >
                    <span className="[color:var(--text-muted)] [font-size:0.7rem] [width:20px] [text-align:right] [flex-shrink:0]">
                        {index + 1}.
                    </span>
                    <span className="[flex:1] [color:var(--text-primary)]">
                        {player}
                    </span>
                    <button
                        type="button"
                        className="btn-ghost [padding:4px] [min-width:auto]"
                        onClick={() => onRemovePlayer(player)}
                        aria-label={`Remove ${player} from the selected XI`}
                    >
                        <X size={14} />
                    </button>
                </div>
            ))}
        </div>
    );
}
