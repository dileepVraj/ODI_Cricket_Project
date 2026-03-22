"use client";

import { useAppContext } from "@/lib/context";

export default function DashboardPage() {
    const { manifest, isLoadingManifest } = useAppContext();

    if (isLoadingManifest || !manifest) {
        return (
            <div className="flex items-center justify-center h-full">
                <p className="empty-state-text">Loading Vantage...</p>
            </div>
        );
    }

    return (
        <div className="flex items-center justify-center h-full">
            <p className="empty-state-text">
                Select a module from the sidebar to begin analysis.
            </p>
        </div>
    );
}
