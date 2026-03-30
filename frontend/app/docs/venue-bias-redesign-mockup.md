# VenueBiasCard Redesign Mockup (v2.0)
**Screen Name:** VenueBiasCard Redesign
**Status:** PROPOSAL (Stitch MCP Unavailable)
**Target:** `frontend/components/renderers/VenueBiasCard.tsx`
**Visual:** `screenshots/VenueBiasCard-Redesign-Gemini.png`

---

## 🎨 DESIGN SPECIFICATION (VANTAGE v4.0)

### 1. HERO ROW - BIAS IMPACT
- **Two Giant Win% Numbers:** Left (Bat First Win%) in **Cyan** (`#06b6d4`), Right (Chase Win%) in **Purple** (`#a855f7`).
- **Typography:** 64px font-black font-data (JetBrains Mono).
- **Split Progress Bar:** Horizontal bar directly below win% numbers, proportional to win split.
- **Labels:** 11px font-bold font-ui text-muted uppercase tracking-wider.

### 2. METADATA ROW - CONSOLIDATED CONTEXT
- **Venue Name:** Bold, text-primary, uppercase.
- **Match Stats:** "47 MATCHES · 5 YEARS" in compact 12px secondary text.
- **Badges (Right-Aligned):** 
    - **Confidence:** "RELIABLE SAMPLE" (Cyan border/text).
    - **Verdict:** "BAT FIRST BIAS" (Purple border/text).

### 3. STATS GRID - CORE METRICS (4 Equal Columns)
- **Columns:** AVG 1ST INN, AVG 2ND INN, LOWEST DEFENDED, HIGHEST CHASED.
- **Data Display:** 
    - **Value:** 32px font-black font-data text-primary.
    - **Subtext:** Small **σ (sigma)** value (e.g. "σ12.4") in font-data text-muted (10px).
- **Labels:** 11px font-bold text-muted uppercase tracking-widest.

### 4. TOSS INTEL - DECISION RATES
- **Horizontal Layout:** "Chose Bat Win%" (Left) vs "Chose Bowl Win%" (Right).
- **Typography:** 40px font-black font-data.
- **Spacing:** Separated by a 40px vertical border divider.
- **Description:** Small italic text-muted explains the stat context.

### 5. DANGER STRIP (Optional)
- **Background:** Dark Red (`#450a0a`).
- **Foreground:** Tier-Danger (`#ef4444`).
- **Logic:** Only rendered when match sample < 15 or σ > 25.0.

---

## 🛠️ TSX STRUCTURE (COMPLIANT MOCKUP)

```tsx
/* 
  VANTAGE REDESIGN: VenueBiasCard
  Implementation-ready for Codex.
*/

<section className="venue-bias-card flex flex-col bg-elevated border border-default rounded-sm overflow-hidden">
  
  {/* HERO ROW */}
  <div className="p-10 flex flex-col gap-8">
    <div className="flex justify-between items-end">
      <div className="flex flex-col">
        <span className="text-[11px] font-bold text-muted uppercase tracking-widest mb-2">Bat First Win%</span>
        <span className="text-6xl font-black font-data text-accent-ui">64%</span>
      </div>
      <div className="flex flex-col items-end">
        <span className="text-[11px] font-bold text-muted uppercase tracking-widest mb-2">Chase Win%</span>
        <span className="text-6xl font-black font-data text-accent-data">36%</span>
      </div>
    </div>
    <div className="h-4 w-full bg-bg-hover rounded-full overflow-hidden flex border border-subtle relative">
      <div className="h-full bg-accent-ui" style={{ width: '64%' }} />
      <div className="h-full bg-accent-data flex-1" />
      <div className="absolute left-1/2 h-full w-px bg-white/30" />
    </div>
  </div>

  {/* METADATA ROW */}
  <div className="px-10 py-4 bg-bg-hover/60 border-y border-subtle flex justify-between items-center">
    <div className="flex items-center gap-4">
      <h3 className="text-base font-black text-primary">EDEN GARDENS</h3>
      <div className="h-4 w-px bg-border-subtle" />
      <span className="text-xs text-secondary font-medium">47 MATCHES · 5 YEARS</span>
    </div>
    <div className="flex gap-3">
       <div className="badge badge-cyan">RELIABLE SAMPLE</div>
       <div className="badge badge-purple">BAT FIRST BIAS</div>
    </div>
  </div>

  {/* STATS GRID */}
  <div className="grid grid-cols-4 divide-x divide-subtle border-b border-subtle">
    {[
      { label: 'AVG 1ST INN', value: '287', sigma: 'σ12.4' },
      { label: 'AVG 2ND INN', value: '241', sigma: 'σ18.1' },
      { label: 'LOWEST DEFENDED', value: '142', sigma: 'σ9.2' },
      { label: 'HIGHEST CHASED', value: '210', sigma: 'σ14.5' },
    ].map((s) => (
      <div className="p-6 flex flex-col items-center text-center">
        <span className="text-[11px] font-bold text-muted uppercase tracking-widest mb-3">{s.label}</span>
        <span className="text-3xl font-black font-data text-primary">{s.value}</span>
        <span className="text-[10px] text-muted mt-2 font-data font-medium tracking-widest">{s.sigma}</span>
      </div>
    ))}
  </div>

  {/* TOSS INTEL */}
  <div className="p-10 flex flex-col gap-6">
    <div className="flex justify-between items-center border-b border-subtle pb-4">
      <span className="text-[11px] font-bold text-secondary uppercase tracking-widest">Toss Decision Win Rates</span>
      <span className="text-[10px] text-muted font-data">HISTORICAL DATA (n=47)</span>
    </div>
    <div className="grid grid-cols-2 gap-12">
      <div className="flex items-center gap-6">
        <div className="flex flex-col">
          <span className="text-[10px] text-muted uppercase font-black tracking-widest mb-1">Chose Bat</span>
          <span className="text-4xl font-black font-data text-accent-ui">58%</span>
        </div>
        <div className="h-10 w-px bg-border-subtle" />
        <p className="text-[10px] text-muted italic leading-relaxed max-w-[120px]">Win rate when winning toss & electing to bat</p>
      </div>
      <div className="flex items-center gap-6 justify-end text-right">
        <p className="text-[10px] text-muted italic leading-relaxed max-w-[120px]">Win rate when winning toss & electing to bowl</p>
        <div className="h-10 w-px bg-border-subtle" />
        <div className="flex flex-col items-end">
          <span className="text-[10px] text-muted uppercase font-black tracking-widest mb-1">Chose Bowl</span>
          <span className="text-4xl font-black font-data text-accent-data">42%</span>
        </div>
      </div>
    </div>
  </div>

  {/* DANGER STRIP (HIDDEN LOGIC) */}
  {/* <div className="bg-[#450a0a] text-danger p-2 text-center text-[11px] font-black uppercase tracking-widest">⚠ LOW SAMPLE SIZE WARNING</div> */}
</section>
```
