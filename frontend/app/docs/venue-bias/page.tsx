"use client";

import { X, Lightbulb } from "lucide-react";
import { ErrorBoundary } from "@/components/common/ErrorBoundary";
import WinSplitBarSection from "@/components/guide/WinSplitBarSection";
import SampleReliabilitySection from "@/components/guide/SampleReliabilitySection";
import ScoreIntelSection from "@/components/guide/ScoreIntelSection";
import BiasTrendSection from "@/components/guide/BiasTrendSection";
import TossIntelSection from "@/components/guide/TossIntelSection";
import { SectionShell } from "@/components/guide/GuideSection";

const INFO_GRID = [
  { label: "Primary Question", value: "Does winning the toss matter here?" },
  { label: "Data Source", value: "Historical ODI match results" },
  { label: "Min Recommended", value: "8 years of data" },
  { label: "Best Range", value: "8–10 years" },
];

const KEY_TAKEAWAYS = [
  "Always run 8–10 years for reliable trend data. Under 6 years returns INSUFFICIENT DATA for bias trend.",
  "The win split bar always sums to 100% — ties and no-results are excluded from the denominator.",
  "Toss Intelligence and Venue Bias are different signals. A venue can strongly favour bat-first while the toss itself provides minimal edge.",
];

function WhatIsThisSection() {
  return (
    <SectionShell
      title="What Is This Analysis?"
      description="This analysis identifies whether batting first or chasing provides a statistical advantage at a specific ground, using historical ODI match results. Run it with a minimum of 8 years of data for directional signals, and 8–10 years for full statistical confidence."
    >
      <div className="[background:var(--bg-elevated)] [border:1px_solid_var(--border-default)] [border-radius:8px] overflow-hidden">
        <div className="grid grid-cols-2">
          {INFO_GRID.map(({ label, value }, i) => (
            <div
              key={label}
              className={`p-5 flex flex-col gap-2 ${i % 2 === 0 ? "[border-right:1px_solid_var(--border-subtle)]" : ""} ${i < 2 ? "[border-bottom:1px_solid_var(--border-subtle)]" : ""}`}
            >
              <span className="text-[10px] font-bold uppercase tracking-widest [color:var(--text-muted)]">{label}</span>
              <span className="[font-size:14px] [color:var(--text-secondary)]">{value}</span>
            </div>
          ))}
        </div>
      </div>
    </SectionShell>
  );
}

function KeyTakeawaysSection() {
  return (
    <SectionShell
      title="Key Takeaways"
      accentColor="var(--tier-caution)"
      description=""
    >
      <div className="[background:var(--bg-elevated)] [border:1px_solid_var(--border-default)] [border-radius:8px] p-5">
        <div className="flex items-center gap-2 mb-4">
          <Lightbulb size={14} className="[color:var(--tier-caution)] shrink-0" />
          <span className="text-[11px] font-bold uppercase tracking-widest [color:var(--tier-caution)]">Important Notes</span>
        </div>
        <ul className="space-y-4">
          {KEY_TAKEAWAYS.map((point) => (
            <li key={point.slice(0, 30)} className="flex items-start gap-3">
              <span className="[font-size:14px] font-bold [color:var(--tier-caution)] mt-0.5 shrink-0">·</span>
              <p className="[font-size:14px] [color:var(--text-secondary)] [line-height:1.6]">{point}</p>
            </li>
          ))}
        </ul>
      </div>
    </SectionShell>
  );
}

export default function VenueBiasGuidePage() {
  return (
    <ErrorBoundary fallbackMessage="Failed to load guide.">
      <div className="min-h-screen [background:var(--bg-base)] flex flex-col">

        <header className="sticky top-0 z-40 [background:var(--bg-surface)] [border-bottom:1px_solid_var(--border-default)] flex justify-center">
          <div className="[width:min(900px,100%)] px-8 h-16 flex items-center justify-between gap-4">
            <div className="flex flex-col gap-1">
              <span className="text-[10px] font-bold uppercase tracking-widest [color:var(--text-muted)]">
                Analysis Guide / Toss &amp; Venue Bias
              </span>
              <h1 className="[font-size:18px] font-semibold [color:var(--text-primary)]">Toss &amp; Venue Bias Analysis</h1>
            </div>
            <button
              type="button"
              onClick={() => window.close()}
              aria-label="Close guide"
              className="btn-ghost w-9 h-9 flex items-center justify-center shrink-0"
            >
              <X size={18} />
            </button>
          </div>
        </header>

        <main className="flex-1 flex flex-col items-center">
          <div className="[width:min(900px,100%)] px-8 py-12 space-y-8">
            <WhatIsThisSection />
            <WinSplitBarSection />
            <SampleReliabilitySection />
            <ScoreIntelSection />
            <BiasTrendSection />
            <TossIntelSection />
            <KeyTakeawaysSection />
          </div>
        </main>

        <footer className="[border-top:1px_solid_var(--border-subtle)] flex justify-center">
          <div className="[width:min(900px,100%)] px-8 py-4 flex items-center justify-end">
            <span className="text-[10px] font-data [color:var(--text-disabled)] uppercase tracking-widest">
              Sovereign Operator Interface V_2.4.0_STABLE
            </span>
          </div>
        </footer>

      </div>
    </ErrorBoundary>
  );
}
