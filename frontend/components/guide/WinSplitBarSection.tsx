"use client";

import CalloutPopover from "@/components/common/CalloutPopover";
import { SectionShell } from "./GuideSection";

const CALLOUTS = [
  {
    number: 1,
    title: "Bat First %",
    description: "Win rate of teams batting first, out of decided matches only. Ties and no-results are excluded from the denominator.",
  },
  {
    number: 2,
    title: "Chase %",
    description: "Complementary win rate; always sums to 100% with Bat First since all decided matches have exactly one outcome.",
  },
  {
    number: 3,
    title: "Confidence Interval",
    description: "Wilson 95% CI for the bat-first win rate. A narrower band means a larger, more reliable sample.",
  },
  {
    number: 4,
    title: "Excluded Matches",
    description: "Count of ties and no-results removed from the denominator. These outcomes carry no bat/chase signal.",
  },
];

export default function WinSplitBarSection() {
  return (
    <SectionShell
      title="Win Split Bar"
      description="The headline signal — how often does batting first win at this ground? The bar divides decided matches into bat-first and chase wins."
    >
      <div className="[background:var(--bg-elevated)] [border:1px_solid_var(--border-default)] [border-radius:8px] p-5">
        <div className="flex justify-between items-end mb-3">
          <span className="font-data text-base font-black [color:var(--accent-ui)] flex items-center gap-1.5">
            BAT FIRST 58%
            <CalloutPopover number={1} title={CALLOUTS[0].title} description={CALLOUTS[0].description} />
          </span>
          <span className="font-data text-base font-black [color:var(--accent-data)] flex items-center gap-1.5">
            <CalloutPopover number={2} title={CALLOUTS[1].title} description={CALLOUTS[1].description} />
            CHASE 42%
          </span>
        </div>
        <div className="w-full h-[10px] rounded-full overflow-hidden flex [background:var(--bg-hover)]">
          <div className="h-full [background:var(--accent-ui)]" style={{ width: "58%" }} />
          <div className="h-full flex-1 [background:var(--accent-data)]" />
        </div>
        <div className="mt-3 flex items-center justify-center gap-1 text-[10px] uppercase tracking-widest [color:var(--text-muted)]">
          <span>95% confidence:</span>
          <span className="font-data font-bold [color:var(--text-primary)]">48%</span>
          <span>–</span>
          <span className="font-data font-bold [color:var(--text-primary)]">67%</span>
          <span>bat-first</span>
          <CalloutPopover number={3} title={CALLOUTS[2].title} description={CALLOUTS[2].description} />
        </div>
        <div className="mt-1 flex items-center justify-center gap-1 text-[10px] uppercase tracking-widest [color:var(--text-disabled)]">
          <span className="font-data">3</span>
          <span>matches excluded — ties / no result</span>
          <CalloutPopover number={4} title={CALLOUTS[3].title} description={CALLOUTS[3].description} />
        </div>
      </div>
    </SectionShell>
  );
}
