"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { fetchTradeById, type TradeResponse } from "@/components/cockpit/cockpit-api";
import LiveTradeCockpit from "@/components/cockpit/LiveTradeCockpit";

export default function LiveTradePage() {
    const params = useParams();
    const tradeId = Number(params.tradeId);

    const [trade, setTrade] = useState<TradeResponse | null>(null);
    const [error, setError] = useState<string | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        if (!tradeId || Number.isNaN(tradeId)) {
            setError("Invalid trade ID.");
            setLoading(false);
            return;
        }

        fetchTradeById(tradeId)
            .then((data) => {
                setTrade(data);
                setLoading(false);
            })
            .catch(() => {
                setError("Trade not found.");
                setLoading(false);
            });
    }, [tradeId]);

    if (loading) {
        return (
            <div className="ltc-page">
                <div className="ltc-body">
                    <p className="ltc-no-data">Loading trade…</p>
                </div>
            </div>
        );
    }

    if (error || !trade) {
        return (
            <div className="ltc-page">
                <div className="ltc-body">
                    <p className="ltc-no-data">{error ?? "Trade not found."}</p>
                </div>
            </div>
        );
    }

    return <LiveTradeCockpit trade={trade} />;
}
