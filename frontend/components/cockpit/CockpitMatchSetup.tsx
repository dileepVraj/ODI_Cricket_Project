"use client";

import type { VenueOption } from "./cockpit-api";
import CockpitDropdown, { type CockpitDropdownOption } from "./CockpitDropdown";
import CockpitHomeGroundToggle from "./CockpitHomeGroundToggle";
import CockpitOddsSelector from "./CockpitOddsSelector";
import CockpitTeamText from "./CockpitTeamText";
import type { HomeGround, OddsPhaseInput, TossSelection } from "./cockpit-types";

interface CockpitMatchSetupProps {
    teamOptions: string[];
    awayTeamOptions: string[];
    oddsTeamOptions: string[];
    venueOptions: VenueOption[];
    isLoadingTeams: boolean;
    isLoadingVenues: boolean;
    homeTeam: string;
    awayTeam: string;
    tossSelection: TossSelection;
    venue: string;
    bankroll: string;
    matchDate: string;
    homeGround: HomeGround;
    oddsBeforeToss: OddsPhaseInput;
    oddsAfterToss: OddsPhaseInput;
    walletBalance: number | null;
    canCreateTrade: boolean;
    isCreating: boolean;
    createError: string | null;
    createMessage: string | null;
    submitLabel: string;
    onHomeTeamChange: (value: string) => void;
    onAwayTeamChange: (value: string) => void;
    onTossSelectionChange: (value: TossSelection) => void;
    onVenueChange: (value: string) => void;
    onBankrollChange: (value: string) => void;
    onMatchDateChange: (value: string) => void;
    onHomeGroundChange: (value: HomeGround) => void;
    onOddsBeforeTossSelectedTeamChange: (value: string) => void;
    onOddsBeforeTossBackOddsChange: (value: string) => void;
    onOddsBeforeTossLayOddsChange: (value: string) => void;
    onOddsAfterTossSelectedTeamChange: (value: string) => void;
    onOddsAfterTossBackOddsChange: (value: string) => void;
    onOddsAfterTossLayOddsChange: (value: string) => void;
    onCreateTrade: () => void;
}

export default function CockpitMatchSetup({
    teamOptions,
    awayTeamOptions,
    venueOptions,
    isLoadingTeams,
    isLoadingVenues,
    homeTeam,
    awayTeam,
    oddsTeamOptions,
    tossSelection,
    venue,
    bankroll,
    matchDate,
    homeGround,
    oddsBeforeToss,
    oddsAfterToss,
    walletBalance,
    canCreateTrade,
    isCreating,
    createError,
    createMessage,
    submitLabel,
    onHomeTeamChange,
    onAwayTeamChange,
    onTossSelectionChange,
    onVenueChange,
    onBankrollChange,
    onMatchDateChange,
    onHomeGroundChange,
    onOddsBeforeTossSelectedTeamChange,
    onOddsBeforeTossBackOddsChange,
    onOddsBeforeTossLayOddsChange,
    onOddsAfterTossSelectedTeamChange,
    onOddsAfterTossBackOddsChange,
    onOddsAfterTossLayOddsChange,
    onCreateTrade,
}: CockpitMatchSetupProps) {
    const hasTeamOptions = teamOptions.length > 0;
    const hasVenueOptions = venueOptions.length > 0;
    const homeTeamPlaceholder = isLoadingTeams ? "Loading teams..." : hasTeamOptions ? "Select home team..." : "No teams available";
    const awayTeamPlaceholder = isLoadingTeams ? "Loading teams..." : hasTeamOptions ? "Select away team..." : "No teams available";
    const venuePlaceholder = isLoadingVenues ? "Loading venues..." : "No venues available";
    const teamDropdownOptions: CockpitDropdownOption[] = teamOptions.map((team) => ({
        value: team,
        label: <CockpitTeamText team={team} variant="outlined" />,
    }));
    const tossOptions: CockpitDropdownOption[] = homeTeam && awayTeam
        ? [
            { value: "HOME_FIELD" as const, label: <><CockpitTeamText team={homeTeam} variant="outlined" /> choose to field</> },
            { value: "HOME_BAT" as const, label: <><CockpitTeamText team={homeTeam} variant="outlined" /> choose to bat</> },
            { value: "AWAY_FIELD" as const, label: <><CockpitTeamText team={awayTeam} variant="outlined" /> choose to field</> },
            { value: "AWAY_BAT" as const, label: <><CockpitTeamText team={awayTeam} variant="outlined" /> choose to bat</> },
        ]
        : [];

    function handleSubmit(event: React.FormEvent<HTMLFormElement>): void {
        event.preventDefault();
        if (canCreateTrade && !isCreating) {
            onCreateTrade();
        }
    }

    return (
        <form className="glass-card cockpit-match-setup" onSubmit={handleSubmit}>
            <div className="cockpit-match-setup-header">
                <div className="cockpit-match-setup-copy">
                    <h2 className="cockpit-match-setup-title">Match Setup</h2>
                    <p className="cockpit-match-setup-hint">
                        Save the pre-toss setup now, then finish the trade after the toss is known.
                    </p>
                </div>
            </div>

            <div className="cockpit-match-setup-grid">
                {/* Block 1: Match details */}
                <div className="cockpit-match-setup-field">
                    <label className="cockpit-match-setup-label" htmlFor="cockpit-match-date">
                        Match date
                    </label>
                    <input
                        id="cockpit-match-date"
                        type="date"
                        autoComplete="off"
                        className="context-input cockpit-match-setup-input"
                        value={matchDate}
                        onChange={(event) => onMatchDateChange(event.target.value)}
                    />
                </div>

                <div className="cockpit-match-setup-field">
                    <label className="cockpit-match-setup-label" htmlFor="cockpit-home-team">
                        Home team
                    </label>
                    <CockpitDropdown
                        id="cockpit-home-team"
                        ariaLabel="Home team"
                        value={homeTeam}
                        options={teamDropdownOptions}
                        placeholder={homeTeamPlaceholder}
                        disabled={!hasTeamOptions}
                        triggerClassName="cockpit-match-setup-input"
                        onChange={onHomeTeamChange}
                    />
                </div>

                <div className="cockpit-match-setup-field">
                    <label className="cockpit-match-setup-label" htmlFor="cockpit-away-team">
                        Away team
                    </label>
                    <CockpitDropdown
                        id="cockpit-away-team"
                        ariaLabel="Away team"
                        value={awayTeam}
                        options={awayTeamOptions.map((team) => ({ value: team, label: <CockpitTeamText team={team} variant="outlined" /> }))}
                        placeholder={awayTeamPlaceholder}
                        disabled={!hasTeamOptions}
                        triggerClassName="cockpit-match-setup-input"
                        onChange={onAwayTeamChange}
                    />
                </div>

                <div className="cockpit-match-setup-field">
                    <label className="cockpit-match-setup-label" htmlFor="cockpit-venue">
                        Venue
                    </label>
                    <select
                        id="cockpit-venue"
                        className="context-input cockpit-match-setup-input"
                        value={venue}
                        onChange={(event) => onVenueChange(event.target.value)}
                        disabled={!hasVenueOptions}
                    >
                        <option value="" disabled className="text-slate-500">{hasVenueOptions ? "Select venue" : venuePlaceholder}</option>
                        {venueOptions.map((option) => (
                            <option key={option.id} value={option.id}>
                                {option.label}
                            </option>
                        ))}
                    </select>
                </div>

                <div className="cockpit-match-setup-field">
                    <label className="cockpit-match-setup-label">Home ground</label>
                    <CockpitHomeGroundToggle
                        value={homeGround}
                        onChange={onHomeGroundChange}
                        homeTeam={homeTeam || undefined}
                        awayTeam={awayTeam || undefined}
                    />
                </div>

                <div className="cockpit-match-setup-field">
                    <label className="cockpit-match-setup-label" htmlFor="cockpit-before-toss-odds-team">
                        Odds before toss
                    </label>
                    <CockpitOddsSelector
                        fieldLabel="Odds before toss"
                        idPrefix="cockpit-before-toss-odds"
                        teamOptions={oddsTeamOptions}
                        selectedTeam={oddsBeforeToss.selectedTeam}
                        backOdds={oddsBeforeToss.backOdds}
                        layOdds={oddsBeforeToss.layOdds}
                        onSelectedTeamChange={onOddsBeforeTossSelectedTeamChange}
                        onBackOddsChange={onOddsBeforeTossBackOddsChange}
                        onLayOddsChange={onOddsBeforeTossLayOddsChange}
                    />
                </div>

                <div className="cockpit-match-setup-field">
                    <label className="cockpit-match-setup-label" htmlFor="cockpit-toss">
                        Toss
                    </label>
                    <CockpitDropdown
                        id="cockpit-toss"
                        ariaLabel="Toss outcome"
                        value={tossSelection}
                        options={tossOptions}
                        placeholder={tossOptions.length === 0 ? "Select teams first" : "Select toss winner..."}
                        disabled={tossOptions.length === 0}
                        triggerClassName="cockpit-match-setup-input"
                        onChange={(nextValue) => onTossSelectionChange(nextValue as TossSelection)}
                    />
                </div>

                <div className="cockpit-match-setup-field">
                    <label className="cockpit-match-setup-label" htmlFor="cockpit-after-toss-odds-team">
                        Odds after toss
                    </label>
                    <CockpitOddsSelector
                        fieldLabel="Odds after toss"
                        idPrefix="cockpit-after-toss-odds"
                        teamOptions={oddsTeamOptions}
                        selectedTeam={oddsAfterToss.selectedTeam}
                        backOdds={oddsAfterToss.backOdds}
                        layOdds={oddsAfterToss.layOdds}
                        onSelectedTeamChange={onOddsAfterTossSelectedTeamChange}
                        onBackOddsChange={onOddsAfterTossBackOddsChange}
                        onLayOddsChange={onOddsAfterTossLayOddsChange}
                    />
                </div>

                <div className="cockpit-match-setup-field">
                    <label className="cockpit-match-setup-label" htmlFor="cockpit-bankroll">
                        BANKROLL (INR)
                    </label>
                    <input
                        id="cockpit-bankroll"
                        type="number"
                        step="0.01"
                        min="0.01"
                        inputMode="decimal"
                        autoComplete="off"
                        className="context-input cockpit-match-setup-input"
                        placeholder="e.g. 5000"
                        value={bankroll}
                        onChange={(event) => onBankrollChange(event.target.value)}
                    />
                    {walletBalance !== null && (
                        <p className="cockpit-match-setup-hint" aria-live="polite">
                            Available:{" "}
                            <span className="font-numeric">
                                {walletBalance.toLocaleString("en-IN", {
                                    style: "currency",
                                    currency: "INR",
                                    maximumFractionDigits: 0,
                                })}
                            </span>
                        </p>
                    )}
                </div>
            </div>

            <div className="cockpit-match-setup-footer">
                {createError && (
                    <p className="cockpit-match-setup-error" role="alert">
                        {createError}
                    </p>
                )}
                {createMessage && !createError && (
                    <p className="cockpit-match-setup-hint cockpit-match-setup-message">
                        {createMessage}
                    </p>
                )}
                <button
                    type="submit"
                    className="btn-primary cockpit-match-setup-submit"
                    disabled={!canCreateTrade || isCreating}
                >
                    {isCreating ? "Saving..." : submitLabel}
                </button>
            </div>
        </form>
    );
}
