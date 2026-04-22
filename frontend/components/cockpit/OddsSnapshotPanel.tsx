/**
 * OddsSnapshotPanel — read-only display of pre-match odds from the trade record.
 * Three columns: before toss, after toss, after over 1.
 */

interface SnapshotCol {
    label: string;
    fav: string;
    favEmpty: boolean;
    odds: string;
    oddsEmpty: boolean;
    showFav: boolean;
}

interface OddsSnapshotPanelProps {
    cols: [SnapshotCol, SnapshotCol, SnapshotCol];
}

export default function OddsSnapshotPanel({ cols }: OddsSnapshotPanelProps) {
    return (
        <div className="ltc-snapshot-panel">
            <div className="ltc-snapshot-header">
                <div className="ltc-section-label">Odds Snapshot</div>
            </div>
            <div className="ltc-snapshot-grid">
                {cols.map((col) => (
                    <div key={col.label} className="ltc-snapshot-col">
                        <span className="ltc-snapshot-sublabel">{col.label}</span>
                        {col.showFav && (
                            <span className={`ltc-snapshot-fav${col.favEmpty ? " ltc-snapshot-fav--empty" : ""}`}>
                                {col.fav}
                            </span>
                        )}
                        {!col.showFav && (
                            <span className="ltc-snapshot-fav ltc-snapshot-fav--empty">—</span>
                        )}
                        <span className={`ltc-snapshot-odds${col.oddsEmpty ? " ltc-snapshot-odds--empty" : ""}`}>
                            {col.odds}
                        </span>
                    </div>
                ))}
            </div>
        </div>
    );
}
