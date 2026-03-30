"use client";

import CalloutPopover from "@/components/common/CalloutPopover";
import { SectionShell } from "./GuideSection";

const CALLOUTS = [
  {
    number: 1,
    title: "LOW SAMPLE",
    description: "Fewer than 10 decided matches. Do not trade on this signal — percentages are highly unstable at small n.",
  },
  {
    number: 2,
    title: "MODERATE",
    description: "10–24 matches. Use for directional context only. The signal is suggestive but not yet statistically robust.",
  },
  {
    number: 3,
    title: "RELIABLE",
    description: "25+ matches. Signal is statistically actionable. The confidence interval will be acceptably narrow.",
  },
];

export default function SampleReliabilitySection() {
  return (
    <SectionShell
      title="Sample Reliability Badge"
      description="Every result is tagged with a reliability tier so you know how much statistical weight to apply to the win split signal."
    >
      <div className="[background:var(--bg-elevated)] [border:1px_solid_var(--border-default)] [border-radius:8px] p-5">
        <div className="flex items-center gap-4 flex-wrap mb-5">
          <div className="flex items-center gap-2">
            <span className="badge badge-danger text-[9px] uppercase tracking-widest">LOW SAMPLE</span>
            <CalloutPopover number={1} title={CALLOUTS[0].title} description={CALLOUTS[0].description} />
          </div>
          <div className="flex items-center gap-2">
            <span className="badge badge-caution text-[9px] uppercase tracking-widest">MODERATE</span>
            <CalloutPopover number={2} title={CALLOUTS[1].title} description={CALLOUTS[1].description} />
          </div>
          <div className="flex items-center gap-2">
            <span className="badge badge-elite text-[9px] uppercase tracking-widest">RELIABLE</span>
            <CalloutPopover number={3} title={CALLOUTS[2].title} description={CALLOUTS[2].description} />
          </div>
        </div>
        <div className="space-y-1.5">
          <p className="text-[10px] [color:var(--text-muted)]">
            <span className="font-data [color:var(--tier-danger)]">&lt;10</span> matches → LOW SAMPLE
          </p>
          <p className="text-[10px] [color:var(--text-muted)]">
            <span className="font-data [color:var(--tier-caution)]">10–24</span> matches → MODERATE
          </p>
          <p className="text-[10px] [color:var(--text-muted)]">
            <span className="font-data [color:var(--tier-elite)]">25+</span> matches → RELIABLE
          </p>
        </div>
      </div>
    </SectionShell>
  );
}
