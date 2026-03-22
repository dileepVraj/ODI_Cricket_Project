"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import CricketGeometry from "@/components/common/CricketGeometry";
import {
  type LandingGender,
  type LandingCategory,
  type LandingFormatSlug,
  type LandingFormatOption,
  LANDING_FORMAT_OPTIONS,
  LANDING_GENDER_LABELS,
  LANDING_CATEGORY_LABELS,
} from "@/lib/types";

// ── Sub-components ─────────────────────────────────────────────

interface ChipProps {
  label: string;
  selected: boolean;
  onClick: () => void;
  fullWidth?: boolean;
}

function SelectionChip({ label, selected, onClick, fullWidth }: ChipProps) {
  const modifier = selected ? "landing-chip--selected" : "landing-chip--unselected";
  const chipClass = `landing-chip ${modifier}`;
  return (
    <button
      type="button"
      onClick={onClick}
      style={fullWidth ? { gridColumn: "1 / -1" } : undefined}
      className={chipClass}
    >
      {label}
    </button>
  );
}

function StepLabel({ children }: { children: React.ReactNode }) {
  return <p className="landing-step-label">{children}</p>;
}

// ── Main page ──────────────────────────────────────────────────

export default function LandingPage() {
  const router = useRouter();

  // Blank state on every mount — spec requires landing always starts fresh.
  // useState(null) satisfies this: Next.js App Router fully remounts client
  // components on navigation to a new route, so bfcache state restoration
  // is not a concern here. No useEffect reset needed.
  const [gender, setGender] = useState<LandingGender | null>(null);
  const [category, setCategory] = useState<LandingCategory | null>(null);
  const [format, setFormat] = useState<LandingFormatSlug | null>(null);

  function handleGenderSelect(g: LandingGender) {
    setGender(g);
    setCategory(null);
    setFormat(null);
  }

  function handleCategorySelect(c: LandingCategory) {
    setCategory(c);
    setFormat(null);
  }

  function handleFormatSelect(f: LandingFormatSlug) {
    setFormat(f);
  }

  function handleEnter() {
    if (!gender || !category || !format) return;
    router.push(`/?gender=${gender}&category=${category}&format=${format}`);
  }

  const formatOptions: LandingFormatOption[] =
    gender && category ? LANDING_FORMAT_OPTIONS[gender][category] : [];

  const isCtaEnabled = gender !== null && category !== null && format !== null;

  // Build path summary — show only selected segments
  const pathParts: string[] = [];
  if (gender) pathParts.push(LANDING_GENDER_LABELS[gender]);
  if (category) pathParts.push(LANDING_CATEGORY_LABELS[category]);
  if (format) {
    const found = formatOptions.find((o) => o.slug === format);
    if (found) pathParts.push(found.label);
  }
  const pathSummary = pathParts.join(" · ");

  return (
    <div className="landing-root">
      <CricketGeometry />

      {/* Wordmark — top-left terminal header */}
      <header className="landing-wordmark" aria-label="Vantage application header">
        <span className="landing-wordmark-name">VANTAGE</span>
        <span className="landing-wordmark-version">v2.0</span>
      </header>

      {/* Selection card — centered */}
      <main className="landing-center">
        <div className="landing-card" role="form" aria-label="Format selection">

          <p className="landing-subtitle">STRATEGIC ALGO EXCHANGE</p>

          {/* Step 01 */}
          <StepLabel>01 — SELECT GENDER</StepLabel>
          <div className="landing-chip-row">
            <SelectionChip
              label="Men's"
              selected={gender === "mens"}
              onClick={() => handleGenderSelect("mens")}
            />
            <SelectionChip
              label="Women's"
              selected={gender === "womens"}
              onClick={() => handleGenderSelect("womens")}
            />
          </div>

          {/* Step 02 */}
          <StepLabel>02 — SELECT CATEGORY</StepLabel>
          <div className="landing-chip-row">
            <SelectionChip
              label="Internationals"
              selected={category === "internationals"}
              onClick={() => handleCategorySelect("internationals")}
            />
            <SelectionChip
              label="Domestic Leagues"
              selected={category === "domestic"}
              onClick={() => handleCategorySelect("domestic")}
            />
          </div>

          {/* Step 03 */}
          <StepLabel>03 — SELECT FORMAT</StepLabel>
          <div className="landing-chip-grid" aria-live="polite">
            {formatOptions.map((opt, idx) => {
              const isOrphan =
                formatOptions.length % 2 !== 0 &&
                idx === formatOptions.length - 1;
              return (
                <SelectionChip
                  key={opt.slug}
                  label={opt.label}
                  selected={format === opt.slug}
                  onClick={() => handleFormatSelect(opt.slug)}
                  fullWidth={isOrphan}
                />
              );
            })}
          </div>

          <div className="landing-divider" aria-hidden="true" />

          {/* CTA */}
          <button
            type="button"
            className="landing-cta"
            onClick={handleEnter}
            disabled={!isCtaEnabled}
            aria-disabled={!isCtaEnabled}
          >
            Enter Vantage →
          </button>

          {/* Path summary */}
          {pathSummary && (
            <p className="landing-path-summary" aria-live="polite">
              {pathSummary}
            </p>
          )}
        </div>
      </main>

      {/* Footer */}
      <footer className="landing-footer">
        <p>VANTAGE v2.0 · Algo-Trading Intelligence Platform</p>
      </footer>
    </div>
  );
}
