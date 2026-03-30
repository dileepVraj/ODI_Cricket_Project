# VenueBiasCard: Stitch Design (v2.0)
**Status:** DESIGN PROPOSAL | **Target:** `frontend/components/renderers/VenueBiasCard.tsx`
**Design System:** Stitch (Dark Theme)

---

## 🎨 DESIGN SPECIFICATION

### 1. Structure & Layout
- **Container:** Single `rounded-xl` card with `bg-elevated` background. No alternating strip backgrounds.
- **Hero Section:** High-impact Win% display. Bat First vs. Bowl First (Chase).
- **Metadata Row:** Consolidated row below hero for venue name, match count, and period.
- **Stats Grid:** Clean 2x2 or 1x4 grid for score metrics (Avg 1st Inn, Avg 2nd Inn, etc.).
- **Toss Intel:** Integrated as a sub-section with clear contrast.

### 2. Typography & Hierarchy
- **Primary Stat (Win%):** `text-5xl font-black font-data`.
- **Labels:** `text-[11px] font-bold uppercase tracking-wider` (Minimum 11px).
- **Secondary Text:** `text-sm font-medium`.
- **Metadata:** `text-xs text-muted`.

### 3. Color Semantics
- **Bat First:** `[color:var(--accent-ui)]` (Cyan/India Blue).
- **Bowl First (Chase):** `[color:var(--accent-data)]` (Purple/Teal).
- **Verdict:** Semantic badges (Elite/Caution/Danger) based on reliability, not just bias.

---

## 🛠️ STITCH COMPONENT MOCKUP

```tsx
/*
  STITCH DESIGN: VenueBiasCard Fixed
  Note: This is a design guide for implementation.
*/

<section className="w-full bg-elevated border border-default rounded-xl overflow-hidden flex flex-col shadow-lg">
  
  {/* --- 1. HERO WIN% ROW --- */}
  <div className="px-8 pt-8 pb-6 flex flex-col gap-6">
    <div className="flex justify-between items-end">
      {/* Bat First Hero */}
      <div className="flex flex-col">
        <span className="text-[11px] font-bold text-muted uppercase tracking-widest mb-1">Bat First Win%</span>
        <div className="flex items-baseline gap-1">
          <span className="text-5xl font-black font-data text-accent-ui">{bat1_win_pct}%</span>
          {bias_verdict === 'bat_first' && <TrendingUp size={20} className="text-accent-ui mb-1" />}
        </div>
      </div>

      {/* VS Divider */}
      <div className="h-12 w-px bg-subtle self-center" />

      {/* Chase Hero */}
      <div className="flex flex-col items-end">
        <span className="text-[11px] font-bold text-muted uppercase tracking-widest mb-1">Chase Win%</span>
        <div className="flex items-baseline gap-1">
          {bias_verdict === 'bowl_first' && <TrendingUp size={20} className="text-accent-data mb-1" />}
          <span className="text-5xl font-black font-data text-accent-data">{chase_win_pct}%</span>
        </div>
      </div>
    </div>

    {/* Win Split Bar - Single consolidated bar */}
    <div className="relative h-3 w-full bg-bg-hover rounded-full overflow-hidden flex">
      <div 
        className="h-full bg-accent-ui transition-all duration-700" 
        style={{ width: `${bat1_win_pct}%` }} 
      />
      <div className="h-full flex-1 bg-accent-data transition-all duration-700" />
      {/* Midpoint Marker */}
      <div className="absolute left-1/2 top-0 bottom-0 w-px bg-white/20" />
    </div>
  </div>

  {/* --- 2. CONSOLIDATED METADATA --- */}
  <div className="px-8 py-3 bg-bg-hover/50 border-y border-subtle flex justify-between items-center">
    <div className="flex items-center gap-3">
      <h3 className="text-sm font-bold text-primary tracking-tight">{venue_id}</h3>
      <div className="h-3 w-px bg-subtle" />
      <span className="text-xs text-muted font-data">{total_matches} matches · {period}y</span>
    </div>
    <div className="flex gap-2">
       <Badge variant={sample_reliability} size="sm">{reliabilityLabel}</Badge>
       <Badge variant={bias_verdict} size="sm">{verdictLabel}</Badge>
    </div>
  </div>

  {/* --- 3. CORE METRICS GRID --- */}
  <div className="grid grid-cols-4 divide-x divide-subtle border-b border-subtle">
    {[
      { label: 'AVG 1ST', value: inn1_median, sub: `σ${inn1_std}` },
      { label: 'AVG 2ND', value: inn2_median, sub: `σ${inn2_std}` },
      { label: 'LOWEST DEF', value: lowest_defended, clickable: true },
      { label: 'HIGHEST CHASE', value: highest_chased, clickable: true },
    ].map((item) => (
      <div className="p-5 flex flex-col items-center text-center group transition-colors hover:bg-bg-hover">
        <span className="text-[10px] font-bold text-muted uppercase tracking-wider mb-2">{item.label}</span>
        <span className="text-2xl font-bold font-data text-primary">{item.value ?? '—'}</span>
        {item.sub && <span className="text-[10px] text-muted mt-1 font-data">{item.sub}</span>}
        {item.clickable && <span className="text-[9px] text-disabled mt-2 uppercase opacity-0 group-hover:opacity-100 transition-opacity">Audit Match</span>}
      </div>
    ))}
  </div>

  {/* --- 4. TOSS INTELLIGENCE (Compact) --- */}
  {toss_intelligence?.data_available && (
    <div className="p-8 flex flex-col gap-4">
      <div className="flex justify-between items-center">
        <span className="text-[11px] font-bold text-secondary uppercase tracking-widest">Toss Decision Win Rates</span>
        <span className="text-[10px] text-disabled font-data">n={toss_match_count}</span>
      </div>
      <div className="grid grid-cols-2 gap-8">
        <div className="flex items-center gap-4">
          <div className="flex flex-col">
            <span className="text-[10px] text-muted uppercase font-bold">Bat First</span>
            <span className="text-3xl font-black font-data text-accent-ui">{chose_bat_win_pct}%</span>
          </div>
          <div className="text-[10px] text-disabled leading-tight">Win rate when<br/>winning toss</div>
        </div>
        <div className="flex items-center gap-4 justify-end">
          <div className="text-[10px] text-disabled text-right leading-tight">Win rate when<br/>winning toss</div>
          <div className="flex flex-col items-end">
            <span className="text-[10px] text-muted uppercase font-bold">Bowl First</span>
            <span className="text-3xl font-black font-data text-accent-data">{chose_bowl_win_pct}%</span>
          </div>
        </div>
      </div>
    </div>
  )}

  {/* --- 5. DANGER ZONE (Low Sample) --- */}
  {sample_reliability === "LOW_SAMPLE" && (
    <div className="bg-danger/10 border-t border-danger/20 px-8 py-3 flex items-center gap-3">
      <AlertTriangle size={14} className="text-tier-danger" />
      <span className="text-[11px] font-bold text-tier-danger uppercase tracking-wide">
        LOW SAMPLE SIZE (< 10) — DATA IS INDICATIVE ONLY
      </span>
    </div>
  )}
</section>
```

---

## 🚀 IMPROVEMENTS SUMMARY
1.  **Hierarchy Flip:** Win% is now the first thing a trader sees (the "Hero"). Venue name moved to metadata.
2.  **Typography:** All text is 11px+ (labels) or 10px (fine print). No 9px micro-labels.
3.  **Visual Noise Reduction:** Removed the "strips" background. Used a clean `bg-elevated` card with semantic borders/dividers.
4.  **Information Density:** Consolidated the metadata row (Venue + Count + Period) to save vertical space.
5.  **Color Clarity:** Strictly mapped colors to `accent-ui` and `accent-data` for consistency across the platform.
6.  **Toss Intel Integration:** Redesigned to be more horizontal and scannable, avoiding the "giant number floating in space" look.
