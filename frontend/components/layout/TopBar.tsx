"use client";

import { useRouter } from "next/navigation";
import { Activity } from "lucide-react";
import { useAppContext } from "@/lib/context";
import { stripEmoji } from "@/lib/utils";

export default function TopBar() {
    const router = useRouter();
    const { formats, activeFormat } = useAppContext();

    const activeFmt = formats.find((f) => f.key === activeFormat);
    const formatLabel = activeFmt ? stripEmoji(activeFmt.label).trim() : "";

    return (
        <header className="topbar" role="banner">
            <div className="topbar-wordmark">
                <div className="topbar-logo" aria-hidden="true">
                    <Activity size={14} />
                </div>
                <span className="topbar-title">VANTAGE</span>
            </div>

            {formatLabel && (
                <button
                    className="topbar-format-label"
                    onClick={() => router.push("/")}
                    aria-label={`Active format: ${formatLabel}. Click to change format.`}
                >
                    {formatLabel}
                </button>
            )}
        </header>
    );
}
