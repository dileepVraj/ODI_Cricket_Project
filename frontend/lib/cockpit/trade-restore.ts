import {
    restoreTradeSnapshot,
    type RestoreTradeSnapshotRequest,
    type TradeResponse,
} from "@/components/cockpit/cockpit-api";
import type { BetResponse } from "@/lib/cockpit/live-trade-bets-api";

/** @schema none -- frontend-only composite for trade restore */
export interface TradeRestoreSnapshot {
    bets: BetResponse[];
    format: string;
    trade: TradeResponse;
}

export async function restoreDeletedTrade(snapshot: TradeRestoreSnapshot): Promise<TradeResponse> {
    const body: RestoreTradeSnapshotRequest = {
        trade: snapshot.trade,
        bets: snapshot.bets,
    };

    return restoreTradeSnapshot(body, snapshot.format);
}
