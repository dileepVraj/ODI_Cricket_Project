"use client";

import { ChevronLeft } from "lucide-react";
import CockpitMatchSetup from "./CockpitMatchSetup";
import PendingPreTossTrades from "./PendingPreTossTrades";
import { useActiveTradeViewState } from "@/lib/cockpit/useActiveTradeViewState";

interface ActiveTradeViewProps {
    formatKey: string;
}

export default function ActiveTradeView({ formatKey }: ActiveTradeViewProps) {
    const state = useActiveTradeViewState({ formatKey });

    return (
        <div className="cockpit-trade-layout-shell">
            <div
                className={`cockpit-trade-layout${state.isSidebarOpen ? " cockpit-trade-layout--split" : " cockpit-trade-layout--single"}`}
            >
                <CockpitMatchSetup {...state.matchSetupProps} />

                {state.isSidebarOpen && (
                    <PendingPreTossTrades {...state.pendingTradesProps} />
                )}
            </div>

            {!state.isSidebarOpen && (
                <button
                    type="button"
                    className="cockpit-pending-trades-toggle cockpit-pending-trades-toggle--dock"
                    aria-label="Expand pending trades"
                    title="Expand pending trades"
                    onClick={state.openSidebar}
                >
                    <ChevronLeft size={16} />
                </button>
            )}
        </div>
    );
}
