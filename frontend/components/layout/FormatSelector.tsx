"use client";

import { useAppContext } from "@/lib/context";
import { Activity, Zap } from "lucide-react";

export default function FormatSelector() {
    const { formats, activeFormat, switchFormat, manifest } = useAppContext();

    return (
        <header
            id="format-selector-bar"
            className="format-selector [height:var(--format-selector-height)] [display:flex] [align-items:center] [justify-content:space-between] [padding:0_20px] [position:sticky] [top:0px] [z-index:50]"
        >
            <div className="[display:flex] [align-items:center] [gap:10px]">
                <div className="[width:32px] [height:32px] [border-radius:var(--radius-md)] [background:linear-gradient(135deg,_var(--accent-primary),_var(--accent-secondary))] [display:flex] [align-items:center] [justify-content:center]">
                    <Activity size={18} className="[color:var(--text-primary)]" />
                </div>
                <div>
                    <h1 className="gradient-text [font-size:1rem] [font-weight:800] [letter-spacing:-0.02em]">CricketAlgo</h1>
                    <span className="[font-size:0.65rem] [color:var(--text-disabled)] [font-weight:500] [letter-spacing:0.05em] [text-transform:uppercase]">
                        Trading Platform
                    </span>
                </div>
            </div>

            <nav className="[display:flex] [gap:4px] [align-items:center]">
                {formats.map((fmt) => (
                    <button
                        key={fmt.key}
                        id={`format-tab-${fmt.key}`}
                        className={`format-tab ${fmt.key === activeFormat ? "active" : ""} ${!fmt.has_manifest ? "disabled" : ""}`}
                        onClick={() => switchFormat(fmt.key)}
                        disabled={!fmt.has_manifest}
                        title={fmt.has_manifest ? fmt.label : `${fmt.label} - coming soon`}
                    >
                        <span className="[font-size:1rem]">{fmt.icon}</span>
                        <span>{fmt.label}</span>
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
