"use client";

import CockpitDropdown from "./CockpitDropdown";
import CockpitTeamText from "./CockpitTeamText";

interface CockpitOddsSelectorProps {
    fieldLabel: string;
    idPrefix: string;
    teamOptions: string[];
    selectedTeam: string;
    backOdds: string;
    layOdds: string;
    onSelectedTeamChange: (value: string) => void;
    onBackOddsChange: (value: string) => void;
    onLayOddsChange: (value: string) => void;
}

export default function CockpitOddsSelector({
    fieldLabel,
    idPrefix,
    teamOptions,
    selectedTeam,
    backOdds,
    layOdds,
    onSelectedTeamChange,
    onBackOddsChange,
    onLayOddsChange,
}: CockpitOddsSelectorProps) {
    const hasTeamOptions = teamOptions.length > 0;

    return (
        <div className="cockpit-odds-selector">
            <CockpitDropdown
                id={`${idPrefix}-team`}
                ariaLabel={`${fieldLabel} team`}
                value={selectedTeam}
                options={teamOptions.map((team) => ({ value: team, label: <CockpitTeamText team={team} variant="outlined" /> }))}
                placeholder="Team"
                disabled={!hasTeamOptions}
                onChange={onSelectedTeamChange}
                className="cockpit-odds-selector-control cockpit-odds-selector-control--team"
                triggerClassName="cockpit-match-setup-input cockpit-odds-selector-control"
            />

            <input
                id={`${idPrefix}-back`}
                type="text"
                inputMode="text"
                autoComplete="off"
                className="context-input cockpit-match-setup-input cockpit-odds-selector-control cockpit-odds-selector-control--odds"
                placeholder="Back"
                value={backOdds}
                onChange={(event) => onBackOddsChange(event.target.value)}
                aria-label={`${fieldLabel} back odds`}
            />

            <input
                id={`${idPrefix}-lay`}
                type="text"
                inputMode="text"
                autoComplete="off"
                className="context-input cockpit-match-setup-input cockpit-odds-selector-control cockpit-odds-selector-control--odds"
                placeholder="Lay"
                value={layOdds}
                onChange={(event) => onLayOddsChange(event.target.value)}
                aria-label={`${fieldLabel} lay odds`}
            />
        </div>
    );
}
