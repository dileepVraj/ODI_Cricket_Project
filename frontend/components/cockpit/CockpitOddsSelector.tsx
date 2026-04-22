"use client";

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
            <select
                id={`${idPrefix}-team`}
                className="context-input cockpit-match-setup-input cockpit-odds-selector-control"
                value={selectedTeam}
                onChange={(event) => onSelectedTeamChange(event.target.value)}
                disabled={!hasTeamOptions}
                aria-label={`${fieldLabel} team`}
            >
                <option value="">{hasTeamOptions ? "Select team" : "Select teams first"}</option>
                {teamOptions.map((team) => (
                    <option key={team} value={team}>
                        {team}
                    </option>
                ))}
            </select>

            <input
                id={`${idPrefix}-back`}
                type="text"
                inputMode="text"
                className="context-input cockpit-match-setup-input cockpit-odds-selector-control"
                placeholder="Back"
                value={backOdds}
                onChange={(event) => onBackOddsChange(event.target.value)}
                aria-label={`${fieldLabel} back odds`}
            />

            <input
                id={`${idPrefix}-lay`}
                type="text"
                inputMode="text"
                className="context-input cockpit-match-setup-input cockpit-odds-selector-control"
                placeholder="Lay"
                value={layOdds}
                onChange={(event) => onLayOddsChange(event.target.value)}
                aria-label={`${fieldLabel} lay odds`}
            />
        </div>
    );
}
