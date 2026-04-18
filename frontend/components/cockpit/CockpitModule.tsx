"use client";

import { useState } from "react";

type CockpitTabKey = "live-trade" | "history";

interface CockpitTab {
    key: CockpitTabKey;
    label: string;
    message: string;
}

const COCKPIT_TABS: CockpitTab[] = [
    {
        key: "live-trade",
        label: "Live Trade",
        message: "Live Trade view \u2014 coming soon",
    },
    {
        key: "history",
        label: "History",
        message: "History view \u2014 coming soon",
    },
];

function getTabButtonClass(isActive: boolean): string {
    return `format-tab${isActive ? " format-tab-active" : ""}`;
}

export default function CockpitModule() {
    const [activeTab, setActiveTab] = useState<CockpitTabKey>("live-trade");
    const [selectedTradeId, setSelectedTradeId] = useState<number | null>(null);
    const activeView = COCKPIT_TABS.find((tab) => tab.key === activeTab) ?? COCKPIT_TABS[0];

    return (
        <div className="module-page animate-fade-in">
            <div
                className="module-tabs"
                role="tablist"
                aria-label="Cockpit views"
            >
                {COCKPIT_TABS.map((tab) => {
                    const isActive = tab.key === activeTab;
                    return (
                        <button
                            key={tab.key}
                            type="button"
                            role="tab"
                            id={`cockpit-tab-${tab.key}`}
                            aria-selected={isActive}
                            aria-controls="cockpit-panel"
                            className={getTabButtonClass(isActive)}
                            onClick={() => {
                                if (tab.key === "live-trade") {
                                    setSelectedTradeId(null);
                                }
                                setActiveTab(tab.key);
                            }}
                        >
                            {tab.label}
                        </button>
                    );
                })}
            </div>

            <div
                id="cockpit-panel"
                role="tabpanel"
                aria-live="polite"
                aria-labelledby={`cockpit-tab-${activeView.key}`}
                className="glass-card animate-fade-in"
                data-selected-trade-id={selectedTradeId ?? ""}
            >
                <CockpitPlaceholder label={activeView.message} />
            </div>
        </div>
    );
}

function CockpitPlaceholder({ label }: { label: string }) {
    return (
        <div className="px-6 py-12 text-center">
            <p className="page-header-subtitle">{label}</p>
        </div>
    );
}
