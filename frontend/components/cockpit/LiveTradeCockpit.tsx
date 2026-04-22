"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { fetchLiveData, type TradeResponse } from "./cockpit-api";
import type { LiveData } from "./cockpit-types";
import LiveScorePanel from "./LiveScorePanel";
import LiveOddsPanel from "./LiveOddsPanel";
import OddsSnapshotPanel from "./OddsSnapshotPanel";
import {
    extractGmid, getSecondsAgo,
    formatScore, formatOvers, formatCrr, formatOdds,
    getBallClass, getBallLabel, isTeam1Favourite,
    buildTossLine, buildMetaLine, buildFormatLabel,
} from "./_live-trade-formatters";

interface LiveTradeCockpitProps {
    trade: TradeResponse;
}

export default function LiveTradeCockpit({ trade }: LiveTradeCockpitProps) {
    const gmid = extractGmid(trade.santhel_url);
    const [liveData, setLiveData] = useState<LiveData | null>(null);
    const [secondsAgo, setSecondsAgo] = useState<string>("—");

    useEffect(() => {
        if (!gmid) return;
        let cancelled = false;

        async function poll() {
            try {
                const data = await fetchLiveData(gmid!);
                if (!cancelled) {
                    setLiveData(data);
                    setSecondsAgo(getSecondsAgo(data.last_updated));
                }
            } catch { /* silently swallow — stale or not yet available */ }
        }

        poll();
        const interval = setInterval(poll, 4000);
        return () => { cancelled = true; clearInterval(interval); };
    }, [gmid]);

    useEffect(() => {
        if (!liveData) return;
        const timer = setInterval(() => {
            setSecondsAgo(getSecondsAgo(liveData.last_updated));
        }, 1000);
        return () => clearInterval(timer);
    }, [liveData]);

    /* ── Pre-compute display values ──────────────────────────────────── */

    const tossLine    = buildTossLine(trade.toss_winner, trade.toss_decision);
    const metaLine    = buildMetaLine(tossLine, trade.stadium);
    const formatLabel = buildFormatLabel(trade.format, trade.season);

    const isFav1      = liveData ? isTeam1Favourite(liveData.odds) : false;
    const hasData     = liveData != null;

    const scorePanelProps = {
        hasLink: gmid != null,
        hasData,
        team1Name:  liveData?.score.team1.name ?? "",
        team1Score: liveData ? formatScore(liveData.score.team1.runs, liveData.score.team1.wickets) : "",
        team1Overs: liveData ? formatOvers(liveData.score.team1.overs) : "",
        team1Crr:   liveData ? formatCrr(liveData.score.team1.crr) : null,
        team2Name:  liveData?.score.team2.name ?? "",
        team2Score: liveData ? formatScore(liveData.score.team2.runs, liveData.score.team2.wickets) : "",
        team2Overs: liveData ? formatOvers(liveData.score.team2.overs) : "",
        balls:      (liveData?.score.balls ?? []).map((b) => ({ cssClass: getBallClass(b.type), label: getBallLabel(b) })),
        timestamp:  secondsAgo,
    };

    const oddsPanelProps = {
        hasLink: gmid != null,
        hasData,
        team1Name:  trade.team_1,
        team2Name:  trade.team_2,
        team1Back:  liveData ? formatOdds(liveData.odds.team1_back) : "—",
        team2Back:  liveData ? formatOdds(liveData.odds.team2_back) : "—",
        team1IsFav: isFav1,
        timestamp:  secondsAgo,
    };

    const snapshotCols: [Parameters<typeof OddsSnapshotPanel>[0]["cols"][0], Parameters<typeof OddsSnapshotPanel>[0]["cols"][1], Parameters<typeof OddsSnapshotPanel>[0]["cols"][2]] = [
        {
            label:    "Before Toss",
            fav:      trade.fav_before_toss ?? "—",
            favEmpty: trade.fav_before_toss == null,
            odds:     formatOdds(trade.odds_before_toss),
            oddsEmpty: trade.odds_before_toss == null,
            showFav:  true,
        },
        {
            label:    "After Toss",
            fav:      trade.fav_after_toss ?? "—",
            favEmpty: trade.fav_after_toss == null,
            odds:     formatOdds(trade.odds_after_toss),
            oddsEmpty: trade.odds_after_toss == null,
            showFav:  true,
        },
        {
            label:    "After Over 1",
            fav:      "—",
            favEmpty: true,
            odds:     formatOdds(trade.odds_after_1st_over),
            oddsEmpty: trade.odds_after_1st_over == null,
            showFav:  false,
        },
    ];

    return (
        <div className="ltc-page">
            <header className="ltc-header">
                <div className="ltc-header-left">
                    <Link href="/trading-dashboard" className="ltc-back-link">← Back</Link>
                    <span className="ltc-match-title">{trade.team_1} vs {trade.team_2}</span>
                    <span className="ltc-match-meta">{metaLine}</span>
                </div>
                <div className="ltc-header-right">
                    <span className="ltc-live-badge">
                        <span className="ltc-live-dot" />
                        <span className="ltc-live-text">LIVE</span>
                    </span>
                    <span className="ltc-format-label">{formatLabel}</span>
                </div>
            </header>

            <div className="ltc-body">
                <div className="ltc-main-grid">
                    <LiveScorePanel {...scorePanelProps} />
                    <LiveOddsPanel {...oddsPanelProps} />
                </div>
                <OddsSnapshotPanel cols={snapshotCols} />
            </div>
        </div>
    );
}
