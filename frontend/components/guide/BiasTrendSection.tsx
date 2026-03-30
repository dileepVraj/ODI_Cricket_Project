"use client";

import { TrendingUp } from "lucide-react";
import CalloutPopover from "@/components/common/CalloutPopover";
import { SectionShell } from "./GuideSection";

const CALLOUTS = [
  {
    number: 1,
    title: "Historical %",
    description: "Bat-first win rate from 3–6 years ago (fixed 3-year calendar window, min 8 decided matches).",
  },
  {
    number: 2,
    title: "Recent %",
    description: "Bat-first win rate from the last 3 years (fixed 3-year calendar window, min 8 decided matches).",
  },
  {
    number: 3,
    title: "Direction",
    description: "STRENGTHENING if gap ≥12pts, WEAKENING if gap ≤−12pts, STABLE otherwise. Reflects whether the surface is changing.",
  },
  {
    number: 4,
    title: "Insufficient Data",
    description: "Shown when either window has fewer than 8 decided matches — trend is suppressed to avoid false signals.",
  },
];

export default function BiasTrendSection() {
  return (
    <SectionShell
      title="Bias Trend"
      description="Compares two fixed 3-year windows to detect whether the bat-first advantage is growing, shrinking, or holding flat."
    >
      <div className="[background:var(--bg-elevated)] [border:1px_solid_var(--border-default)] [border-radius:8px] p-5 space-y-4">
        <div className="flex items-center justify-between gap-4 flex-wrap">
          <span className="text-[9px] font-bold uppercase tracking-widest [color:var(--text-muted)] shrink-0">BIAS TREND</span>
          <span className="text-xs font-bold font-data flex items-center gap-1.5">
            <span className="flex items-center gap-1">
              Historical
              <span className="[color:var(--text-muted)]">52%</span>
              <CalloutPopover number={1} title={CALLOUTS[0].title} description={CALLOUTS[0].description} />
            </span>
            <span className="[color:var(--text-muted)]">→</span>
            <span className="flex items-center gap-1">
              Recent
              <span className="[color:var(--accent-ui)]">61%</span>
              <CalloutPopover number={2} title={CALLOUTS[1].title} description={CALLOUTS[1].description} />
            </span>
          </span>
          <div className="flex items-center gap-1 text-[10px] font-bold uppercase tracking-widest [color:var(--tier-elite)] shrink-0">
            <TrendingUp size={13} />
            <span>STRENGTHENING</span>
            <CalloutPopover number={3} title={CALLOUTS[2].title} description={CALLOUTS[2].description} />
          </div>
        </div>
        <div className="px-3 py-2 [background:var(--bg-hover)] [border:1px_solid_var(--border-subtle)] [border-radius:8px] flex items-center gap-2">
          <span className="text-[9px] font-bold uppercase tracking-widest [color:var(--text-muted)]">INSUFFICIENT DATA example:</span>
          <span className="text-[10px] font-data [color:var(--text-disabled)]">— / —</span>
          <CalloutPopover number={4} title={CALLOUTS[3].title} description={CALLOUTS[3].description} />
        </div>
      </div>
    </SectionShell>
  );
}
