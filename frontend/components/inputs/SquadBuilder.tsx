"use client";

import { useCallback, useEffect, useState } from "react";
import { fetchPlayers } from "@/lib/api";
import { useAppContext } from "@/lib/context";
import { ChevronDown, ChevronUp } from "lucide-react";
import PlayerList from "@/components/inputs/PlayerList";
import PlayerSearch from "@/components/inputs/PlayerSearch";
import PositionSelector from "@/components/inputs/PositionSelector";

interface SquadBuilderProps {
    formatKey: string;
    teamA: string;
    teamB: string;
    maxPlayers: number;
    homeXI: string[];
    awayXI: string[];
    onHomeXIChange: (players: string[]) => void;
    onAwayXIChange: (players: string[]) => void;
}

interface SquadPanelControllerArgs {
    formatKey: string;
    team: string;
    opponent: string;
    maxPlayers: number;
    selectedPlayers: string[];
    onPlayersChange: (players: string[]) => void;
}

interface SquadPanelController {
    availablePlayers: string[];
    isLoadingPlayers: boolean;
    loadError: string | null;
    addPlayer: (player: string) => void;
    removePlayer: (player: string) => void;
    clearAll: () => void;
    loadSquad: () => Promise<void>;
}

function isValidTeam(team: string): boolean {
    return Boolean(team && team !== "All");
}

function useSquadPanelController(args: SquadPanelControllerArgs): SquadPanelController {
    const { formatKey, team, opponent, maxPlayers, selectedPlayers, onPlayersChange } = args;
    const [availablePlayers, setAvailablePlayers] = useState<string[]>([]);
    const [loadError, setLoadError] = useState<string | null>(null);
    const [isLoadingPlayers, setIsLoadingPlayers] = useState(false);
    const validTeam = isValidTeam(team);

    useEffect(() => {
        if (!validTeam) {
            setAvailablePlayers([]);
            setLoadError(null);
            return;
        }
        let cancelled = false;
        setIsLoadingPlayers(true);
        setLoadError(null);
        fetchPlayers(formatKey, team)
            .then(players => { if (!cancelled) { setAvailablePlayers(players); setIsLoadingPlayers(false); } })
            .catch(() => { if (!cancelled) { setAvailablePlayers([]); setLoadError("Could not load player list."); setIsLoadingPlayers(false); } });
        return () => { cancelled = true; };
    }, [formatKey, team, validTeam]);

    const addPlayer = useCallback((p: string) => {
        if (selectedPlayers.length < maxPlayers && !selectedPlayers.includes(p)) onPlayersChange([...selectedPlayers, p]);
    }, [maxPlayers, onPlayersChange, selectedPlayers]);

    const removePlayer = useCallback((p: string) => onPlayersChange(selectedPlayers.filter(e => e !== p)), [onPlayersChange, selectedPlayers]);
    const clearAll = useCallback(() => onPlayersChange([]), [onPlayersChange]);
    const loadSquad = useCallback(async () => {
        if (!validTeam) return;
        setIsLoadingPlayers(true);
        setLoadError(null);
        try {
            const players = await fetchPlayers(formatKey, team, opponent || undefined);
            setAvailablePlayers(players);
            onPlayersChange(players.slice(0, maxPlayers));
        } catch { setLoadError("Failed to auto-load XI. Please try again."); } finally { setIsLoadingPlayers(false); }
    }, [formatKey, maxPlayers, onPlayersChange, opponent, team, validTeam]);

    return { availablePlayers, isLoadingPlayers, loadError, addPlayer, removePlayer, clearAll, loadSquad };
}

export default function SquadBuilder({
    formatKey,
    teamA,
    teamB,
    maxPlayers,
    homeXI,
    awayXI,
    onHomeXIChange,
    onAwayXIChange,
}: SquadBuilderProps) {
    const { manifest } = useAppContext();
    const homeLabel = manifest?.context_fields?.team_a?.label ?? "Team A";
    const awayLabel = manifest?.context_fields?.team_b?.label ?? "Team B";
    const homeController = useSquadPanelController({
        formatKey,
        team: teamA,
        opponent: teamB,
        maxPlayers,
        selectedPlayers: homeXI,
        onPlayersChange: onHomeXIChange,
    });
    const awayController = useSquadPanelController({
        formatKey,
        team: teamB,
        opponent: teamA,
        maxPlayers,
        selectedPlayers: awayXI,
        onPlayersChange: onAwayXIChange,
    });

    const [isCollapsed, setIsCollapsed] = useState<boolean>(homeXI.length >= 1 && awayXI.length >= 1);

    useEffect(() => {
        if (homeXI.length >= 1 && awayXI.length >= 1) setIsCollapsed(true);
    }, [homeXI.length, awayXI.length]);

    const renderChips = (players: string[]) => {
        const visible = players.slice(0, 3);
        const overflowCount = players.length > 3 ? players.length - 3 : 0;
        return (
            <div className="[display:flex] [gap:4px]">
                {visible.map(p => <div key={p} className="[padding:2px_8px] [background:rgb(30,42,56)] [border:1px_solid_rgb(26,39,64)] [border-radius:4px] [color:white] [font-size:10px] [font-weight:500] [white-space:nowrap]">{p}</div>)}
                {overflowCount > 0 && <div className="[padding:2px_8px] [background:rgb(30,42,56)] [border:1px_solid_rgb(26,39,64)] [border-radius:4px] [color:white] [font-size:10px] [font-weight:500] [opacity:0.5]">+{overflowCount}</div>}
            </div>
        );
    };

    if (isCollapsed) {
        return (
            <div
                onClick={() => setIsCollapsed(false)}
                className="[width:100%] [height:56px] [background:rgb(17,28,42)] [border-bottom:1px_solid_rgb(26,39,64)] [display:flex] [align-items:center] [padding:0_16px] [justify-content:space-between] [cursor:pointer] [margin-bottom:20px] animate-fade-in"
                role="button" tabIndex={0} onKeyDown={e => (e.key === "Enter" || e.key === " ") && setIsCollapsed(false)}
                aria-label="Expand squad builder"
            >
                <div className="[display:flex] [align-items:center] [gap:24px] [overflow:hidden] [flex:1]">
                    <div className="[display:flex] [align-items:center] [gap:12px] [flex-shrink:0]">
                        <span className="[font-size:12px] [font-weight:700] [color:var(--text-secondary)] [text-transform:uppercase] [letter-spacing:0.05em] [white-space:nowrap]">{homeLabel}</span>
                        {renderChips(homeXI)}
                    </div>
                    <div className="[width:1px] [height:24px] [background:rgb(26,39,64)] [flex-shrink:0]" />
                    <div className="[display:flex] [align-items:center] [gap:12px] [flex-shrink:0]">
                        <span className="[font-size:12px] [font-weight:700] [color:var(--text-secondary)] [text-transform:uppercase] [letter-spacing:0.05em] [white-space:nowrap]">{awayLabel}</span>
                        {renderChips(awayXI)}
                    </div>
                </div>
                <div className="[display:flex] [align-items:center] [gap:8px] [flex-shrink:0] [margin-left:16px]">
                    <span className="[font-size:10px] [color:var(--text-muted)]">Edit squads</span>
                    <ChevronDown size={16} className="[color:var(--text-secondary)]" />
                </div>
            </div>
        );
    }

    return (
        <div className="[display:flex] [flex-direction:column] [gap:8px] [margin-bottom:20px]">
            <div className="[display:flex] [justify-content:flex-end]">
                <button
                    aria-label="Collapse"
                    type="button"
                    onClick={() => setIsCollapsed(true)}
                    className="[display:flex] [align-items:center] [gap:4px] [font-size:10px] [color:var(--text-muted)] hover:[color:var(--text-secondary)] [transition:all_var(--transition-fast)]"
                >
                    <span>Collapse</span>
                    <ChevronUp size={14} />
                </button>
            </div>
            <div className="[display:grid] [grid-template-columns:1fr_1fr] [gap:16px]">
                {[
                    { key: "team-a", contextLabel: homeLabel, team: teamA, accentVar: "var(--accent-primary)", selectedPlayers: homeXI, controller: homeController },
                    { key: "team-b", contextLabel: awayLabel, team: teamB, accentVar: "var(--accent-secondary)", selectedPlayers: awayXI, controller: awayController },
                ].map((panel) => {
                    const validTeam = isValidTeam(panel.team);
                    const isFull = panel.selectedPlayers.length >= maxPlayers;
                    return (
                        <div key={panel.key} className={`glass-card [padding:16px] [border-top:3px_solid_${panel.accentVar}]`}>
                            <PositionSelector contextLabel={panel.contextLabel} team={panel.team} maxPlayers={maxPlayers} playerCount={panel.selectedPlayers.length} validTeam={validTeam} isLoadingPlayers={panel.controller.isLoadingPlayers} hasPlayers={panel.selectedPlayers.length > 0} loadError={panel.controller.loadError} onLoadSquad={panel.controller.loadSquad} onClearAll={panel.controller.clearAll} accentVar={panel.accentVar} />
                            {validTeam && (
                                <>
                                    <PlayerSearch contextLabel={panel.contextLabel} team={panel.team} accentVar={panel.accentVar} isLoadingPlayers={panel.controller.isLoadingPlayers} isFull={isFull} players={panel.controller.availablePlayers} onSelectPlayer={panel.controller.addPlayer} />
                                    <PlayerList accentVar={panel.accentVar} selectedPlayers={panel.selectedPlayers} onRemovePlayer={panel.controller.removePlayer} />
                                </>
                            )}
                        </div>
                    );
                })}
            </div>
        </div>
    );
}
