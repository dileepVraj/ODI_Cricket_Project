"use client";

import { Zap, Clock, Target, BarChart3 } from "lucide-react";
import { thClass, tdClass, accentBarClass, fmtNum } from "./PhaseTableStyles";

interface PhaseData {
    avg: number;
    n: number;
    wkts: number;
}

interface InningsStats {
    pp: PhaseData;
    mid: PhaseData;
    dth: PhaseData;
    total: PhaseData;
}

export default function PhaseTable({
    title,
    stats,
    accentColor,
}: {
    title: string;
    stats: { "1"?: InningsStats; "2"?: InningsStats };
    accentColor: string;
}) {
    const inn1 = stats["1"];
    const inn2 = stats["2"];

    const phases = [
        { key: "pp", label: "Powerplay (1-10)", icon: <Zap size={14} /> },
        { key: "mid", label: "Middle (11-40)", icon: <Clock size={14} /> },
        { key: "dth", label: "Death (41-50)", icon: <Target size={14} /> },
        { key: "total", label: "Total", icon: <BarChart3 size={14} /> },
    ] as const;

    return (
        <div>
            <div className="[display:flex] [align-items:center] [gap:10px] [margin-bottom:10px]">
                <div className={`[width:4px] [height:20px] [border-radius:2px] ${accentBarClass(accentColor)}`} />
                <h4 className="[font-size:0.8rem] [font-weight:700] [color:var(--text-secondary)] [text-transform:uppercase] [letter-spacing:0.06em]">
                    {title}
                </h4>
            </div>

            <div className="[background:var(--bg-elevated)] [border-radius:var(--radius-md)] [border:1px_solid_var(--border-subtle)] [overflow:hidden] [box-shadow:0_8px_22px_rgba(2,_8,_23,_0.2)]">
                <table className="[width:100%] [border-collapse:collapse] [font-size:0.84rem]">
                    <thead>
                        <tr>
                            <th className={thClass("left")}>Phase</th>
                            <th className={thClass("right")}>1st Inn Avg</th>
                            <th className={thClass("right")}>1st Inn Wkts</th>
                            <th className={thClass("right")}>2nd Inn Avg</th>
                            <th className={thClass("right")}>2nd Inn Wkts</th>
                            <th className={thClass("right")}>Matches</th>
                        </tr>
                    </thead>
                    <tbody>
                        {phases.map((phase, i) => {
                            const d1 = inn1?.[phase.key];
                            const d2 = inn2?.[phase.key];
                            const isTotal = phase.key === "total";
                            return (
                                <tr
                                    key={phase.key}
                                    className={`[transition:background-color_0.2s] ${i < phases.length - 1 ? "[border-bottom:1px_solid_var(--border-subtle)]" : ""} ${isTotal ? "[font-weight:700] [background:var(--bg-hover)]" : "[font-weight:500] hover:[background:var(--bg-hover)]"}`}
                                >
                                    <td className={`${tdClass("left")} [font-weight:600]`}>
                                        <span className="[display:inline-flex] [align-items:center] [gap:6px]">
                                            {phase.icon} {phase.label}
                                        </span>
                                    </td>
                                    <td className={tdClass("right")}>{fmtNum(d1?.avg)}</td>
                                    <td className={tdClass("right")}>{isTotal ? "-" : fmtNum(d1?.wkts)}</td>
                                    <td className={tdClass("right")}>{fmtNum(d2?.avg)}</td>
                                    <td className={tdClass("right")}>{isTotal ? "-" : fmtNum(d2?.wkts)}</td>
                                    <td className={tdClass("right")}>{d1?.n ?? d2?.n ?? "-"}</td>
                                </tr>
                            );
                        })}
                    </tbody>
                </table>
            </div>
        </div>
    );
}
