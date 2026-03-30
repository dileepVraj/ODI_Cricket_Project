"use client";

import CalloutPopover from "@/components/common/CalloutPopover";
import { SectionShell } from "./GuideSection";

const CALLOUTS = [
  {
    number: 1,
    title: "Chose to Bat Win %",
    description: "Of matches where the toss winner chose to bat, how often did they win? Isolated from the general bat-first rate.",
  },
  {
    number: 2,
    title: "Chose to Bowl Win %",
    description: "Of matches where the toss winner chose to bowl, how often did they win? Complements the Chose to Bat signal.",
  },
  {
    number: 3,
    title: "n= count",
    description: "Sample size per decision group. Shown as '—' when below the minimum threshold of 12 matches.",
  },
];

export default function TossIntelSection() {
  return (
    <SectionShell
      title="Toss Intelligence"
      description="Separates the venue bias signal from the toss signal. A venue can strongly favour bat-first while the toss itself provides minimal additional edge."
    >
      <div className="[background:var(--bg-elevated)] [border:1px_solid_var(--border-default)] [border-radius:8px] overflow-hidden">
        <div className="px-5 pt-4 pb-3 [border-bottom:1px_solid_var(--border-subtle)]">
          <p className="text-[10px] font-bold uppercase tracking-widest [color:var(--text-secondary)]">
            TOSS INTELLIGENCE ·{" "}
            <span className="font-data">69</span> matches with toss data
          </p>
        </div>
        <div className="grid grid-cols-2 relative p-5">
          <div className="absolute left-1/2 top-5 bottom-5 w-px [background:var(--border-subtle)]" aria-hidden="true" />
          <div className="flex flex-col items-center pr-4">
            <div className="flex items-center gap-1.5 mb-1">
              <span className="text-xs [color:var(--text-secondary)]">Chose to Bat</span>
              <CalloutPopover number={1} title={CALLOUTS[0].title} description={CALLOUTS[0].description} />
            </div>
            <span className="text-4xl font-black font-data [color:var(--accent-ui)]">65%</span>
            <span className="text-[9px] uppercase tracking-widest [color:var(--text-muted)] mt-2">toss winner win rate</span>
            <div className="flex items-center gap-1 mt-1">
              <span className="text-[9px] font-data [color:var(--text-disabled)]">n=42</span>
              <CalloutPopover number={3} title={CALLOUTS[2].title} description={CALLOUTS[2].description} />
            </div>
          </div>
          <div className="flex flex-col items-center pl-4">
            <div className="flex items-center gap-1.5 mb-1">
              <span className="text-xs [color:var(--text-secondary)]">Chose to Bowl</span>
              <CalloutPopover number={2} title={CALLOUTS[1].title} description={CALLOUTS[1].description} />
            </div>
            <span className="text-4xl font-black font-data [color:var(--accent-data)]">48%</span>
            <span className="text-[9px] uppercase tracking-widest [color:var(--text-muted)] mt-2">toss winner win rate</span>
            <span className="text-[9px] font-data [color:var(--text-disabled)] mt-1">n=27</span>
          </div>
        </div>
        <div className="px-5 py-2 [background:var(--bg-hover)] [border-top:1px_solid_var(--border-subtle)] flex items-center gap-2">
          <span className="text-[9px] uppercase tracking-widest [color:var(--text-muted)]">Decision Gap:</span>
          <span className="font-data font-bold text-xs [color:var(--tier-elite)]">+17pts</span>
          <span className="text-[9px] [color:var(--text-muted)]">(65% − 48%)</span>
        </div>
      </div>
    </SectionShell>
  );
}
