"use client";

import CalloutPopover from "@/components/common/CalloutPopover";
import { SectionShell } from "./GuideSection";

const CALLOUTS = [
  {
    number: 1,
    title: "Median Score",
    description: "Central tendency using median, not mean, to reduce skew from batting collapses and exceptional totals.",
  },
  {
    number: 2,
    title: "σ (Std Dev)",
    description: "Score volatility. Low σ = predictable surface. High σ = unpredictable — approach total-based signals cautiously.",
  },
  {
    number: 3,
    title: "Lowest Defended",
    description: "Smallest total successfully defended at this ground; useful for setting minimum viable chase targets.",
  },
  {
    number: 4,
    title: "Highest Chased",
    description: "Largest total successfully chased; defines the upper bound of chase viability at this venue.",
  },
];

export default function ScoreIntelSection() {
  return (
    <SectionShell
      title="Score Intel Grid"
      description="Four score reference points to calibrate total expectations and identify the surface's predictability."
    >
      <div className="[background:var(--bg-elevated)] [border:1px_solid_var(--border-default)] [border-radius:8px] overflow-hidden">
        <div className="grid grid-cols-2">
          <div className="p-5 flex flex-col items-center text-center [border-right:1px_solid_var(--border-subtle)] [border-bottom:1px_solid_var(--border-subtle)]">
            <div className="flex items-center gap-1.5 mb-2">
              <span className="text-[9px] font-bold uppercase tracking-widest [color:var(--text-muted)]">AVG 1ST INN</span>
              <CalloutPopover number={1} title={CALLOUTS[0].title} description={CALLOUTS[0].description} />
            </div>
            <span className="text-3xl font-bold font-data [color:var(--text-primary)]">287</span>
            <div className="flex items-center gap-1 mt-2">
              <span className="text-[10px] [color:var(--text-muted)] font-data">min 180 · max 420 · σ62</span>
              <CalloutPopover number={2} title={CALLOUTS[1].title} description={CALLOUTS[1].description} />
            </div>
          </div>
          <div className="p-5 flex flex-col items-center text-center [border-bottom:1px_solid_var(--border-subtle)]">
            <span className="text-[9px] font-bold uppercase tracking-widest [color:var(--text-muted)] mb-2">AVG 2ND INN</span>
            <span className="text-3xl font-bold font-data [color:var(--text-primary)]">261</span>
            <span className="text-[10px] [color:var(--text-muted)] mt-2 font-data">min 142 · max 389 · σ58</span>
          </div>
          <div className="p-5 flex flex-col items-center text-center [border-right:1px_solid_var(--border-subtle)]">
            <div className="flex items-center gap-1.5 mb-2">
              <span className="text-[9px] font-bold uppercase tracking-widest [color:var(--text-muted)]">LOWEST DEFENDED</span>
              <CalloutPopover number={3} title={CALLOUTS[2].title} description={CALLOUTS[2].description} />
            </div>
            <span className="text-3xl font-bold font-data [color:var(--text-primary)]">218</span>
          </div>
          <div className="p-5 flex flex-col items-center text-center">
            <div className="flex items-center gap-1.5 mb-2">
              <span className="text-[9px] font-bold uppercase tracking-widest [color:var(--text-muted)]">HIGHEST CHASED</span>
              <CalloutPopover number={4} title={CALLOUTS[3].title} description={CALLOUTS[3].description} />
            </div>
            <span className="text-3xl font-bold font-data [color:var(--text-primary)]">344</span>
          </div>
        </div>
      </div>
    </SectionShell>
  );
}
