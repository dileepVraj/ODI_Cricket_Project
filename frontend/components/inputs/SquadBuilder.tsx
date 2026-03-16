"use client";

import { useCallback, useEffect, useState } from "react";
import { fetchPlayers } from "@/lib/api";
import { useAppContext } from "@/lib/context";
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
            .then((players) => {
                if (cancelled) {
                    return;
                }

                setAvailablePlayers(players);
                setLoadError(null);
                setIsLoadingPlayers(false);
            })
            .catch(() => {
                if (cancelled) {
                    return;
                }

                setAvailablePlayers([]);
                setLoadError("Could not load player list.");
                setIsLoadingPlayers(false);
            });

        return () => {
            cancelled = true;
        };
    }, [formatKey, team, validTeam]);

    const addPlayer = useCallback((player: string) => {
        if (selectedPlayers.length >= maxPlayers || selectedPlayers.includes(player)) {
            return;
        }

        onPlayersChange([...selectedPlayers, player]);
    }, [maxPlayers, onPlayersChange, selectedPlayers]);

    const removePlayer = useCallback((player: string) => {
        onPlayersChange(selectedPlayers.filter((entry) => entry !== player));
    }, [onPlayersChange, selectedPlayers]);

    const clearAll = useCallback(() => {
        onPlayersChange([]);
    }, [onPlayersChange]);

    const loadSquad = useCallback(async () => {
        if (!validTeam) {
            return;
        }

        setIsLoadingPlayers(true);
        setLoadError(null);

        try {
            const players = await fetchPlayers(formatKey, team, opponent || undefined);
            setAvailablePlayers(players);
            onPlayersChange(players.slice(0, maxPlayers));
        } catch {
            setLoadError("Failed to auto-load XI. Please try again.");
        } finally {
            setIsLoadingPlayers(false);
        }
    }, [formatKey, maxPlayers, onPlayersChange, opponent, team, validTeam]);

    return {
        availablePlayers,
        isLoadingPlayers,
        loadError,
        addPlayer,
        removePlayer,
        clearAll,
        loadSquad,
    };
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

    // TODO: Drive panel accent metadata from the manifest when a squad config slot is available.
    const panels = [
        {
            key: "team-a",
            contextLabel: homeLabel,
            team: teamA,
            accentVar: "var(--accent-primary)",
            selectedPlayers: homeXI,
            controller: homeController,
        },
        {
            key: "team-b",
            contextLabel: awayLabel,
            team: teamB,
            accentVar: "var(--accent-secondary)",
            selectedPlayers: awayXI,
            controller: awayController,
        },
    ];

    return (
        <div className="[display:grid] [grid-template-columns:1fr_1fr] [gap:16px] [margin-bottom:20px]">
            {panels.map((panel) => {
                const validTeam = isValidTeam(panel.team);
                const isFull = panel.selectedPlayers.length >= maxPlayers;

                return (
                    <div
                        key={panel.key}
                        className={`glass-card [padding:16px] [border-top:3px_solid_${panel.accentVar}]`}
                    >
                        <PositionSelector
                            contextLabel={panel.contextLabel}
                            team={panel.team}
                            maxPlayers={maxPlayers}
                            playerCount={panel.selectedPlayers.length}
                            validTeam={validTeam}
                            isLoadingPlayers={panel.controller.isLoadingPlayers}
                            hasPlayers={panel.selectedPlayers.length > 0}
                            loadError={panel.controller.loadError}
                            onLoadSquad={panel.controller.loadSquad}
                            onClearAll={panel.controller.clearAll}
                            accentVar={panel.accentVar}
                        />

                        {validTeam ? (
                            <>
                                <PlayerSearch
                                    contextLabel={panel.contextLabel}
                                    team={panel.team}
                                    accentVar={panel.accentVar}
                                    isLoadingPlayers={panel.controller.isLoadingPlayers}
                                    isFull={isFull}
                                    players={panel.controller.availablePlayers}
                                    onSelectPlayer={panel.controller.addPlayer}
                                />
                                <PlayerList
                                    accentVar={panel.accentVar}
                                    selectedPlayers={panel.selectedPlayers}
                                    onRemovePlayer={panel.controller.removePlayer}
                                />
                            </>
                        ) : null}
                    </div>
                );
            })}
        </div>
    );
}
