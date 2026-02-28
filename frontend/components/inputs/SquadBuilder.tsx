/**
 * components/inputs/SquadBuilder.tsx — Dual-Panel Squad Selector
 * 
 * Lets users build Home XI and Away XI for squad-dependent functions:
 *   - compare_squads, tactical_matrix, matchups, generate_pack
 * 
 * Features:
 *   - Search-to-add player combobox per team panel
 *   - "Load Squad" button to auto-fill from API
 *   - Player chips with remove button
 *   - Clear all button per panel
 *   - 11-player max with visual counter
 */
"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import ReactDOM from "react-dom";
import { fetchPlayers } from "@/lib/api";
import { Users, UserPlus, X, Trash2, Download, Search, ChevronDown } from "lucide-react";

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
    return (
        <div
            className="[display:grid] [grid-template-columns:1fr_1fr] [gap:16px] [margin-bottom:20px]"
        >
            <SquadPanel
                title="Home XI"
                team={teamA}
                formatKey={formatKey}
                maxPlayers={maxPlayers}
                selectedPlayers={homeXI}
                onPlayersChange={onHomeXIChange}
                accentColor="var(--accent-blue)"
            />
            <SquadPanel
                title="Away XI"
                team={teamB}
                formatKey={formatKey}
                maxPlayers={maxPlayers}
                selectedPlayers={awayXI}
                onPlayersChange={onAwayXIChange}
                accentColor="var(--accent-purple)"
            />
        </div>
    );
}

// ═══════════════════════════════════════════════════════════════════════════
// SQUAD PANEL (one per team)
// ═══════════════════════════════════════════════════════════════════════════

interface SquadPanelProps {
    title: string;
    team: string;
    formatKey: string;
    maxPlayers: number;
    selectedPlayers: string[];
    onPlayersChange: (players: string[]) => void;
    accentColor: string;
}

type SquadBadgeState = "full" | "partial" | "empty";

const SQUAD_BADGE_CLASS: Record<SquadBadgeState, string> = {
    full: "badge-elite",
    partial: "badge-strong",
    empty: "badge-caution",
};

function resolveSquadBadgeState(args: { isFull: boolean; hasPlayers: boolean }): SquadBadgeState {
    if (args.isFull) return "full";
    if (args.hasPlayers) return "partial";
    return "empty";
}

function SquadPanel({
    title,
    team,
    formatKey,
    maxPlayers,
    selectedPlayers,
    onPlayersChange,
    accentColor,
}: SquadPanelProps) {
    const [availablePlayers, setAvailablePlayers] = useState<string[]>([]);
    const [loadError, setLoadError] = useState<string | null>(null);
    const [searchTerm, setSearchTerm] = useState("");
    const [isDropdownOpen, setIsDropdownOpen] = useState(false);
    const [isLoadingPlayers, setIsLoadingPlayers] = useState(false);
    const inputRef = useRef<HTMLInputElement>(null);
    const containerRef = useRef<HTMLDivElement>(null);
    const [dropdownPos, setDropdownPos] = useState({ top: 0, left: 0, width: 0 });

    const validTeam = team && team !== "All" && team !== "";

    // Load available players when team changes
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
                if (!cancelled) {
                    setAvailablePlayers(players);
                    setIsLoadingPlayers(false);
                    setLoadError(null);
                }
            })
            .catch(() => {
                if (!cancelled) {
                    setAvailablePlayers([]);
                    setIsLoadingPlayers(false);
                    setLoadError("Could not load player list.");
                }
            });

        return () => { cancelled = true; };
    }, [formatKey, team, validTeam]);

    // Filter available players by search term and not already selected
    const filteredPlayers = availablePlayers.filter(
        (p) =>
            !selectedPlayers.includes(p) &&
            p.toLowerCase().includes(searchTerm.toLowerCase())
    );

    const addPlayer = useCallback((player: string) => {
        if (selectedPlayers.length >= maxPlayers) return;
        if (selectedPlayers.includes(player)) return;
        onPlayersChange([...selectedPlayers, player]);
        setSearchTerm("");
        setIsDropdownOpen(false);
    }, [maxPlayers, selectedPlayers, onPlayersChange]);

    const removePlayer = useCallback((player: string) => {
        onPlayersChange(selectedPlayers.filter((p) => p !== player));
    }, [selectedPlayers, onPlayersChange]);

    const clearAll = useCallback(() => {
        onPlayersChange([]);
    }, [onPlayersChange]);

    const loadSquad = useCallback(async () => {
        if (!validTeam) return;
        setIsLoadingPlayers(true);
        setLoadError(null);
        try {
            const players = await fetchPlayers(formatKey, team);
            // Take first max players from manifest-driven limit.
            onPlayersChange(players.slice(0, maxPlayers));
        } catch {
            setLoadError("Failed to auto-load XI. Please try again.");
        } finally {
            setIsLoadingPlayers(false);
        }
    }, [formatKey, maxPlayers, team, validTeam, onPlayersChange]);

    // Update dropdown position
    const updateDropdownPos = useCallback(() => {
        if (inputRef.current) {
            const rect = inputRef.current.getBoundingClientRect();
            setDropdownPos({
                top: rect.bottom + 4,
                left: rect.left,
                width: rect.width,
            });
        }
    }, []);

    // Close dropdown on click outside
    useEffect(() => {
        function handleClickOutside(e: MouseEvent) {
            const target = e.target as HTMLElement;
            if (
                containerRef.current &&
                !containerRef.current.contains(target) &&
                !target.closest("[data-squad-dropdown]")
            ) {
                setIsDropdownOpen(false);
            }
        }
        document.addEventListener("mousedown", handleClickOutside);
        return () => document.removeEventListener("mousedown", handleClickOutside);
    }, []);

    const playerCount = selectedPlayers.length;
    const hasPlayers = selectedPlayers.length !== 0;
    const isFull = playerCount >= maxPlayers;
    const squadBadgeState = resolveSquadBadgeState({ isFull, hasPlayers });
    const squadBadgeClass = SQUAD_BADGE_CLASS[squadBadgeState];

    return (
        <div
            ref={containerRef}
            className={`glass-card [padding:16px] [border-top:3px_solid_${accentColor}]`}
        >
            {/* Panel Header */}
            <div
                className="[display:flex] [justify-content:space-between] [align-items:center] [margin-bottom:12px]"
            >
                <div className="[display:flex] [align-items:center] [gap:8px]">
                    <Users size={16} className={`[color:${accentColor}]`} />
                    <span
                        className="[font-size:0.9rem] [font-weight:700] [color:var(--text-primary)]"
                    >
                        {title}
                    </span>
                    <span
                        className={`badge ${squadBadgeClass} [font-size:0.7rem]`}
                    >
                        {playerCount}/{maxPlayers}
                    </span>
                </div>

                {validTeam && (
                    <span className={`[font-size:0.75rem] [font-weight:600] [color:${accentColor}]`}>
                        {team}
                    </span>
                )}
            </div>

            {/* No Team Selected State */}
            {!validTeam && (
                <div
                    className="[padding:20px] [text-align:center] [color:var(--text-muted)] [font-size:0.82rem]"
                >
                    Select a team from the Context Bar above
                </div>
            )}

            {/* Team selected — show builder */}
            {validTeam && (
                <>
                    {/* Action Buttons */}
                    <div
                        className="[display:flex] [gap:6px] [margin-bottom:10px]"
                    >
                        <button
                            className="btn-ghost [font-size:0.75rem] [display:flex] [align-items:center] [gap:4px] [padding:4px_10px]"
                            onClick={loadSquad}
                            disabled={isLoadingPlayers}
                        >
                            <Download size={12} />
                            Load Squad
                        </button>
                        {hasPlayers && (
                            <button
                                className="btn-ghost [font-size:0.75rem] [display:flex] [align-items:center] [gap:4px] [padding:4px_10px] [color:var(--tier-danger)]"
                                onClick={clearAll}
                            >
                                <Trash2 size={12} />
                                Clear
                            </button>
                        )}
                    </div>
                    {loadError && (
                        <div
                            className="[margin-bottom:10px] [font-size:0.74rem] [color:var(--tier-caution)]"
                        >
                            {loadError}
                        </div>
                    )}

                    {/* Player Search Input */}
                    {!isFull && (
                        <div className="[position:relative] [margin-bottom:10px]">
                            <div
                                className={`[display:flex] [align-items:center] [gap:6px] [background:var(--bg-active)] [border-radius:var(--radius-sm)] [padding:6px_10px] [transition:border-color_0.2s] ${isDropdownOpen ? "[border:1px_solid_var(--accent-blue)]" : "[border:1px_solid_var(--border)]"}`}
                            >
                                <Search size={14} className="[color:var(--text-muted)] [flex-shrink:0]" />
                                <input
                                    ref={inputRef}
                                    type="text"
                                    value={searchTerm}
                                    placeholder="Search players..."
                                    onChange={(e) => {
                                        setSearchTerm(e.target.value);
                                        setIsDropdownOpen(true);
                                        updateDropdownPos();
                                    }}
                                    onFocus={() => {
                                        setIsDropdownOpen(true);
                                        updateDropdownPos();
                                    }}
                                    className="[background:transparent] [border:none] [outline:none] [color:var(--text-primary)] [font-size:0.82rem] [width:100%] [font-family:inherit]"
                                />
                                <ChevronDown
                                    size={14}
                                    className={`[color:var(--text-muted)] [flex-shrink:0] [transition:transform_0.2s] [cursor:pointer] ${isDropdownOpen ? "[transform:rotate(180deg)]" : "[transform:none]"}`}
                                    onClick={() => {
                                        setIsDropdownOpen(!isDropdownOpen);
                                        updateDropdownPos();
                                    }}
                                />
                            </div>

                            {/* Dropdown Portal */}
                            {isDropdownOpen &&
                                filteredPlayers.length > 0 &&
                                ReactDOM.createPortal(
                                    <div
                                        data-squad-dropdown
                                        className="[position:fixed] [max-height:200px] [overflow-y:auto] [background:var(--bg-elevated)] [border:1px_solid_var(--border)] [border-radius:var(--radius-sm)] [z-index:99999] [box-shadow:0_8px_24px_rgba(0,_0,_0,_0.4)]"
                                        style={{
                                            top: dropdownPos.top,
                                            left: dropdownPos.left,
                                            width: dropdownPos.width,
                                        }}
                                    >
                                        {filteredPlayers.map((player) => (
                                            <div
                                                key={player}
                                                onClick={() => addPlayer(player)}
                                                className="[padding:8px_12px] [font-size:0.82rem] [color:var(--text-primary)] [cursor:pointer] [border-bottom:1px_solid_var(--border)] [display:flex] [align-items:center] [gap:8px] [transition:background_0.15s] hover:[background:var(--bg-active)]"
                                            >
                                                <UserPlus size={12} className={`[color:${accentColor}]`} />
                                                {player}
                                            </div>
                                        ))}
                                    </div>,
                                    document.body
                                )}
                        </div>
                    )}

                    {/* Selected Players List */}
                    <div
                        className="[display:flex] [flex-direction:column] [gap:4px] [min-height:40px]"
                    >
                        {selectedPlayers.length === 0 && (
                            <div
                                className="[padding:12px] [text-align:center] [color:var(--text-muted)] [font-size:0.78rem] [font-style:italic]"
                            >
                                No players selected. Search above or Load Squad.
                            </div>
                        )}
                        {selectedPlayers.map((player, idx) => (
                            <div
                                key={player}
                                className={`animate-fade-in [display:flex] [align-items:center] [gap:8px] [padding:5px_10px] [background:var(--bg-active)] [border-radius:var(--radius-sm)] [font-size:0.8rem] [border-left:3px_solid_${accentColor}]`}
                            >
                                <span
                                    className="[color:var(--text-muted)] [font-size:0.7rem] [width:20px] [text-align:right] [flex-shrink:0]"
                                >
                                    {idx + 1}.
                                </span>
                                <span className="[flex:1] [color:var(--text-primary)]">
                                    {player}
                                </span>
                                <X
                                    size={14}
                                    className="[color:var(--text-muted)] [cursor:pointer] [flex-shrink:0] [transition:color_0.15s] hover:[color:var(--tier-danger)]"
                                    onClick={() => removePlayer(player)}
                                />
                            </div>
                        ))}
                    </div>
                </>
            )}
        </div>
    );
}
