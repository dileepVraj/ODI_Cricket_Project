/**
 * LiveScorePanel — displays live score rows and ball-by-ball from Santhel.
 */

interface Ball {
    cssClass: string;
    label: string;
}

interface LiveScorePanelProps {
    hasLink: boolean;
    hasData: boolean;
    team1Name: string;
    team1Score: string;
    team1Overs: string;
    team1Crr: string | null;
    team2Name: string;
    team2Score: string;
    team2Overs: string;
    balls: Ball[];
    timestamp: string;
}

export default function LiveScorePanel({
    hasLink,
    hasData,
    team1Name,
    team1Score,
    team1Overs,
    team1Crr,
    team2Name,
    team2Score,
    team2Overs,
    balls,
    timestamp,
}: LiveScorePanelProps) {
    return (
        <div className="ltc-panel">
            <div className="ltc-section-label">Live Score</div>

            {hasData ? (
                <>
                    <div className="ltc-score-rows">
                        <div className="ltc-team-row">
                            <span className="ltc-team-name">{team1Name}</span>
                            <span className="ltc-score-runs">{team1Score}</span>
                            <span className="ltc-score-overs">{team1Overs}</span>
                            {team1Crr && <span className="ltc-crr-chip">{team1Crr}</span>}
                        </div>
                        <div className="ltc-team-row">
                            <span className="ltc-team-name ltc-team-name--dim">{team2Name}</span>
                            <span className="ltc-score-runs ltc-score-runs--dim">{team2Score}</span>
                            <span className="ltc-score-overs ltc-text-dim">{team2Overs}</span>
                        </div>
                    </div>

                    <div className="ltc-balls-section">
                        <span className="ltc-balls-label">Last 6 Balls</span>
                        <div className="ltc-balls-row">
                            {balls.map((ball, i) => (
                                <span key={i} className={ball.cssClass}>{ball.label}</span>
                            ))}
                        </div>
                    </div>

                    <span className="ltc-timestamp">Updated {timestamp}</span>
                </>
            ) : hasLink ? (
                <p className="ltc-no-data">Connecting to Santhel…</p>
            ) : (
                <p className="ltc-no-link">
                    No Santhel match linked — edit the trade to add a match URL.
                </p>
            )}
        </div>
    );
}
