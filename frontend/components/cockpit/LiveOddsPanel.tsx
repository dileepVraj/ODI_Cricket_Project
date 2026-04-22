/**
 * LiveOddsPanel — displays live back prices for each team from Santhel.
 */

interface LiveOddsPanelProps {
    hasLink: boolean;
    hasData: boolean;
    team1Name: string;
    team2Name: string;
    team1Back: string;
    team2Back: string;
    team1IsFav: boolean;
    timestamp: string;
}

export default function LiveOddsPanel({
    hasLink,
    hasData,
    team1Name,
    team2Name,
    team1Back,
    team2Back,
    team1IsFav,
    timestamp,
}: LiveOddsPanelProps) {
    return (
        <div className="ltc-panel">
            <div>
                <div className="ltc-section-label">Live Odds</div>
                <div className="ltc-section-sub">Santhel · Match Odds</div>
            </div>

            {hasData ? (
                <>
                    <div className="ltc-odds-rows">
                        <div className="ltc-odds-row">
                            <span className="ltc-odds-team">{team1Name}</span>
                            <span className="ltc-back-label">Back</span>
                            <span className={`ltc-odds-value${team1IsFav ? " ltc-odds-value--green" : ""}`}>
                                {team1Back}
                            </span>
                        </div>
                        <div className="ltc-odds-row">
                            <span className="ltc-odds-team ltc-odds-team--dim">{team2Name}</span>
                            <span className="ltc-back-label">Back</span>
                            <span className={`ltc-odds-value${!team1IsFav ? " ltc-odds-value--green" : ""}`}>
                                {team2Back}
                            </span>
                        </div>
                    </div>
                    <span className="ltc-timestamp">Updated {timestamp}</span>
                </>
            ) : hasLink ? (
                <p className="ltc-no-data">Connecting to Santhel…</p>
            ) : (
                <p className="ltc-no-link">No Santhel match linked.</p>
            )}
        </div>
    );
}
