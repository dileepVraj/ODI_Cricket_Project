/**
 * components/inputs/SquadBuilder.tsx — Dual-Panel Squad Selector
 * 
 * Lets users build Home XI and Away XI for squad-dependent functions:
 *   - compare_squads, tactical_matrix, matchups, predict_score, generate_pack
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
    homeXI: string[];
    awayXI: string[];
    onHomeXIChange: (players: string[]) => void;
    onAwayXIChange: (players: string[]) => void;
}

export default function SquadBuilder({
    formatKey,
    teamA,
    teamB,
    homeXI,
    awayXI,
    onHomeXIChange,
    onAwayXIChange,
}: SquadBuilderProps) {
    return (
        <div
            style={{
                display: "grid",
                gridTemplateColumns: "1fr 1fr",
                gap: "16px",
                marginBottom: "20px",
            }}
        >
            <SquadPanel
                title="Home XI"
                team={teamA}
                formatKey={formatKey}
                selectedPlayers={homeXI}
                onPlayersChange={onHomeXIChange}
                accentColor="var(--accent-blue)"
            />
            <SquadPanel
                title="Away XI"
                team={teamB}
                formatKey={formatKey}
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
    selectedPlayers: string[];
    onPlayersChange: (players: string[]) => void;
    accentColor: string;
}

function SquadPanel({
    title,
    team,
    formatKey,
    selectedPlayers,
    onPlayersChange,
    accentColor,
}: SquadPanelProps) {
    const [availablePlayers, setAvailablePlayers] = useState<string[]>([]);
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
            return;
        }

        let cancelled = false;
        setIsLoadingPlayers(true);
        fetchPlayers(formatKey, team)
            .then((players) => {
                if (!cancelled) {
                    setAvailablePlayers(players);
                    setIsLoadingPlayers(false);
                }
            })
            .catch(() => {
                if (!cancelled) {
                    setAvailablePlayers([]);
                    setIsLoadingPlayers(false);
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
        if (selectedPlayers.length >= 11) return;
        if (selectedPlayers.includes(player)) return;
        onPlayersChange([...selectedPlayers, player]);
        setSearchTerm("");
        setIsDropdownOpen(false);
    }, [selectedPlayers, onPlayersChange]);

    const removePlayer = useCallback((player: string) => {
        onPlayersChange(selectedPlayers.filter((p) => p !== player));
    }, [selectedPlayers, onPlayersChange]);

    const clearAll = useCallback(() => {
        onPlayersChange([]);
    }, [onPlayersChange]);

    const loadSquad = useCallback(async () => {
        if (!validTeam) return;
        setIsLoadingPlayers(true);
        try {
            const players = await fetchPlayers(formatKey, team);
            // Take first 11
            onPlayersChange(players.slice(0, 11));
        } catch {
            // silently fail
        } finally {
            setIsLoadingPlayers(false);
        }
    }, [formatKey, team, validTeam, onPlayersChange]);

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
    const isFull = playerCount >= 11;

    return (
        <div
            ref={containerRef}
            className="glass-card"
            style={{
                padding: "16px",
                borderTop: `3px solid ${accentColor}`,
            }}
        >
            {/* Panel Header */}
            <div
                style={{
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                    marginBottom: "12px",
                }}
            >
                <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                    <Users size={16} style={{ color: accentColor }} />
                    <span
                        style={{
                            fontSize: "0.9rem",
                            fontWeight: 700,
                            color: "var(--text-primary)",
                        }}
                    >
                        {title}
                    </span>
                    <span
                        className={`badge ${isFull ? "badge-elite" : playerCount > 0 ? "badge-strong" : "badge-caution"}`}
                        style={{ fontSize: "0.7rem" }}
                    >
                        {playerCount}/11
                    </span>
                </div>

                {validTeam && (
                    <span
                        style={{
                            fontSize: "0.75rem",
                            color: accentColor,
                            fontWeight: 600,
                        }}
                    >
                        {team}
                    </span>
                )}
            </div>

            {/* No Team Selected State */}
            {!validTeam && (
                <div
                    style={{
                        padding: "20px",
                        textAlign: "center",
                        color: "var(--text-muted)",
                        fontSize: "0.82rem",
                    }}
                >
                    Select a team from the Context Bar above
                </div>
            )}

            {/* Team selected — show builder */}
            {validTeam && (
                <>
                    {/* Action Buttons */}
                    <div
                        style={{
                            display: "flex",
                            gap: "6px",
                            marginBottom: "10px",
                        }}
                    >
                        <button
                            className="btn-ghost"
                            onClick={loadSquad}
                            disabled={isLoadingPlayers}
                            style={{
                                fontSize: "0.75rem",
                                display: "flex",
                                alignItems: "center",
                                gap: "4px",
                                padding: "4px 10px",
                            }}
                        >
                            <Download size={12} />
                            Load Squad
                        </button>
                        {playerCount > 0 && (
                            <button
                                className="btn-ghost"
                                onClick={clearAll}
                                style={{
                                    fontSize: "0.75rem",
                                    display: "flex",
                                    alignItems: "center",
                                    gap: "4px",
                                    padding: "4px 10px",
                                    color: "var(--tier-danger)",
                                }}
                            >
                                <Trash2 size={12} />
                                Clear
                            </button>
                        )}
                    </div>

                    {/* Player Search Input */}
                    {!isFull && (
                        <div style={{ position: "relative", marginBottom: "10px" }}>
                            <div
                                style={{
                                    display: "flex",
                                    alignItems: "center",
                                    gap: "6px",
                                    background: "var(--bg-active)",
                                    borderRadius: "var(--radius-sm)",
                                    padding: "6px 10px",
                                    border: isDropdownOpen
                                        ? "1px solid var(--accent-blue)"
                                        : "1px solid var(--border)",
                                    transition: "border-color 0.2s",
                                }}
                            >
                                <Search size={14} style={{ color: "var(--text-muted)", flexShrink: 0 }} />
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
                                    style={{
                                        background: "transparent",
                                        border: "none",
                                        outline: "none",
                                        color: "var(--text-primary)",
                                        fontSize: "0.82rem",
                                        width: "100%",
                                        fontFamily: "inherit",
                                    }}
                                />
                                <ChevronDown
                                    size={14}
                                    style={{
                                        color: "var(--text-muted)",
                                        flexShrink: 0,
                                        transform: isDropdownOpen ? "rotate(180deg)" : "none",
                                        transition: "transform 0.2s",
                                        cursor: "pointer",
                                    }}
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
                                        style={{
                                            position: "fixed",
                                            top: dropdownPos.top,
                                            left: dropdownPos.left,
                                            width: dropdownPos.width,
                                            maxHeight: "200px",
                                            overflowY: "auto",
                                            background: "var(--bg-elevated)",
                                            border: "1px solid var(--border)",
                                            borderRadius: "var(--radius-sm)",
                                            zIndex: 99999,
                                            boxShadow: "0 8px 24px rgba(0,0,0,0.4)",
                                        }}
                                    >
                                        {filteredPlayers.map((player) => (
                                            <div
                                                key={player}
                                                onClick={() => addPlayer(player)}
                                                style={{
                                                    padding: "8px 12px",
                                                    fontSize: "0.82rem",
                                                    color: "var(--text-primary)",
                                                    cursor: "pointer",
                                                    borderBottom: "1px solid var(--border)",
                                                    display: "flex",
                                                    alignItems: "center",
                                                    gap: "8px",
                                                    transition: "background 0.15s",
                                                }}
                                                onMouseEnter={(e) => {
                                                    (e.currentTarget as HTMLElement).style.background =
                                                        "var(--bg-active)";
                                                }}
                                                onMouseLeave={(e) => {
                                                    (e.currentTarget as HTMLElement).style.background =
                                                        "transparent";
                                                }}
                                            >
                                                <UserPlus size={12} style={{ color: accentColor }} />
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
                        style={{
                            display: "flex",
                            flexDirection: "column",
                            gap: "4px",
                            minHeight: "40px",
                        }}
                    >
                        {selectedPlayers.length === 0 && (
                            <div
                                style={{
                                    padding: "12px",
                                    textAlign: "center",
                                    color: "var(--text-muted)",
                                    fontSize: "0.78rem",
                                    fontStyle: "italic",
                                }}
                            >
                                No players selected. Search above or Load Squad.
                            </div>
                        )}
                        {selectedPlayers.map((player, idx) => (
                            <div
                                key={player}
                                className="animate-fade-in"
                                style={{
                                    display: "flex",
                                    alignItems: "center",
                                    gap: "8px",
                                    padding: "5px 10px",
                                    background: "var(--bg-active)",
                                    borderRadius: "var(--radius-sm)",
                                    borderLeft: `3px solid ${accentColor}`,
                                    fontSize: "0.8rem",
                                }}
                            >
                                <span
                                    style={{
                                        color: "var(--text-muted)",
                                        fontSize: "0.7rem",
                                        width: "20px",
                                        textAlign: "right",
                                        flexShrink: 0,
                                    }}
                                >
                                    {idx + 1}.
                                </span>
                                <span style={{ flex: 1, color: "var(--text-primary)" }}>
                                    {player}
                                </span>
                                <X
                                    size={14}
                                    style={{
                                        color: "var(--text-muted)",
                                        cursor: "pointer",
                                        flexShrink: 0,
                                        transition: "color 0.15s",
                                    }}
                                    onClick={() => removePlayer(player)}
                                    onMouseEnter={(e) => {
                                        (e.currentTarget as SVGElement).style.color =
                                            "var(--tier-danger)";
                                    }}
                                    onMouseLeave={(e) => {
                                        (e.currentTarget as SVGElement).style.color =
                                            "var(--text-muted)";
                                    }}
                                />
                            </div>
                        ))}
                    </div>
                </>
            )}
        </div>
    );
}
