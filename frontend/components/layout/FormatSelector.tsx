"use client";

import { useEffect, useState } from "react";
import { useAppContext } from "@/lib/context";
import { stripEmoji } from "@/lib/utils";
import { Activity, Zap } from "lucide-react";

export default function FormatSelector() {
    const { formats, activeFormat, switchFormat, manifest } = useAppContext();
    const [isMounted, setIsMounted] = useState(false);
    const showFormatTabs = isMounted && formats.length > 0;

    useEffect(() => {
        setIsMounted(true);
    }, []);

    return (
        <header
            id="format-selector-bar"
            className="format-selector [height:var(--format-selector-height)] [display:flex] [align-items:center] [justify-content:space-between] [padding:0_20px] [position:sticky] [top:0px] [z-index:50]"
        >
            <div className="[display:flex] [align-items:center] [gap:10px]">
                <div className="[width:28px] [height:28px] [border-radius:var(--radius-md)] [background:var(--bg-elevated)] [border:1px_solid_var(--border-default)] [display:flex] [align-items:center] [justify-content:center]">
                    <Activity size={16} className="[color:var(--text-primary)]" />
                </div>
                <div>
                    <h1
                        className="[color:var(--text-primary)] [font-size:0.95rem] [font-weight:700] [letter-spacing:-0.01em]"
                    >
                        Vantage
                    </h1>
                </div>
            </div>

            <nav className="[display:flex] [gap:4px] [align-items:center]">
                {showFormatTabs && formats.map((fmt) => (
                    <button
                        key={fmt.key}
                        id={`format-tab-${fmt.key}`}
                        className={`format-tab ${isMounted && fmt.key === activeFormat ? "active" : ""} ${!fmt.has_manifest ? "disabled" : ""}`}
                        onClick={() => switchFormat(fmt.key)}
                        disabled={!fmt.has_manifest}
                        title={fmt.has_manifest ? fmt.label : `${fmt.label} - coming soon`}
                    >
                        <span>{stripEmoji(fmt.label)}</span>
                    </button>
                ))}
            </nav>

            <div className="[display:flex] [align-items:center] [gap:8px]">
                {manifest && (
                    <span className="[display:flex] [align-items:center] [gap:6px] [font-size:0.75rem] [color:var(--tier-elite)] [font-weight:500]">
                        <Zap size={12} />
                        <span>LIVE</span>
                    </span>
                )}
            </div>
        </header>
    );
}
