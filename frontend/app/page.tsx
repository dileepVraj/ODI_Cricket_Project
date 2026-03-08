/**
 * app/page.tsx - Main Application Shell
 *
 * Composes the 3-layer layout:
 *   Layer 1: FormatSelector (top)
 *   Layer 2: ContextBar (below top)
 *   Layer 3: Sidebar (left) + Main Content (right)
 *
 * Renders Dashboard or CategoryScreen based on sidebar selection.
 */
"use client";

import { useEffect, useMemo, useState } from "react";
import { useAppContext } from "@/lib/context";
import ContextBar from "@/components/layout/ContextBar";
import FormatSelector from "@/components/layout/FormatSelector";
import Sidebar from "@/components/layout/Sidebar";
import { CategoryScreen } from "@/components/layout/CategoryScreen";
import {
  Activity,
  ChevronRight,
  Database,
  TrendingUp,
  Zap,
} from "lucide-react";

const NAV_ROOT_FALLBACK = "dashboard";

export default function Page() {
  return <AppShell />;
}

function AppShell() {
  const { manifest } = useAppContext();
  const navRootKey = useMemo(
    () => manifest?.navigation_root?.key ?? NAV_ROOT_FALLBACK,
    [manifest?.navigation_root?.key]
  );

  const [activeCategory, setActiveCategory] = useState(() => {
    if (typeof window !== "undefined") {
      const hash = window.location.hash.replace("#", "");
      return hash || navRootKey;
    }
    return navRootKey;
  });

  useEffect(() => {
    function onHashChange() {
      const hash = window.location.hash.replace("#", "");
      if (hash) setActiveCategory(hash);
      else setActiveCategory(navRootKey);
    }
    window.addEventListener("hashchange", onHashChange);
    return () => window.removeEventListener("hashchange", onHashChange);
  }, [navRootKey]);

  const handleCategorySelect = (cat: string) => {
    setActiveCategory(cat);
    if (cat === navRootKey) {
      window.history.replaceState(null, "", window.location.pathname);
    } else {
      window.history.replaceState(null, "", `#${cat}`);
    }
  };

  return (
    <div
      className="[display:flex] [flex-direction:column] [height:100vh] [overflow:hidden]"
    >
      <FormatSelector />
      <ContextBar />
      <div className="[display:flex] [flex:1] [overflow:hidden]">
        <Sidebar
          activeCategory={activeCategory}
          onCategorySelect={handleCategorySelect}
        />
        <main
          id="main-content"
          className="[flex:1] [overflow:auto] [padding:24px] [background:var(--bg-deepest)]"
        >
          {activeCategory === navRootKey ? (
            <DashboardScreen />
          ) : (
            <CategoryScreen categoryKey={activeCategory} />
          )}
        </main>
      </div>
    </div>
  );
}

function DashboardScreen() {
  const { manifest, activeFormat } = useAppContext();

  if (!manifest) return null;

  const totalFunctions = manifest.categories.reduce(
    (acc, cat) => acc + cat.functions.length,
    0
  );

  return (
    <div className="animate-fade-in">
      <div className="[margin-bottom:32px]">
        <h2
          className="gradient-text [font-size:1.75rem] [font-weight:800] [margin-bottom:8px]"
        >
          {manifest.format_icon} {manifest.format_label} Command Center
        </h2>
        <p className="[color:var(--text-secondary)] [font-size:0.9rem]">
          Algorithmic trading intelligence powered by deep cricket analytics
        </p>
      </div>
      <div
        className="[display:grid] [grid-template-columns:repeat(auto-fill,_minmax(220px,_1fr))] [gap:16px] [margin-bottom:32px]"
      >
        <StatCard
          icon={<Database size={20} />}
          label="Categories"
          value={String(manifest.categories.length)}
          color="var(--accent-primary)"
        />
        <StatCard
          icon={<Activity size={20} />}
          label="Functions"
          value={String(totalFunctions)}
          color="var(--accent-tertiary)"
        />
        <StatCard
          icon={<Zap size={20} />}
          label="Format"
          value={activeFormat.toUpperCase()}
          color="var(--accent-secondary)"
        />
        <StatCard
          icon={<TrendingUp size={20} />}
          label="Status"
          value="LIVE"
          color="var(--tier-elite)"
        />
      </div>
      <h3
        className="[font-size:1rem] [font-weight:700] [color:var(--text-primary)] [margin-bottom:16px]"
      >
        Quick Access
      </h3>
      <div
        className="[display:grid] [grid-template-columns:repeat(auto-fill,_minmax(280px,_1fr))] [gap:12px]"
      >
        {manifest.categories.map((cat, i) => (
          <button
            key={cat.key}
            className={`glass-card glass-card-hover [padding:16px_20px] [cursor:pointer] [text-align:left] [border:1px_solid_var(--glass-border)] [font-family:inherit] [background:var(--glass-bg)] [animation-delay:${i * 60}ms]`}
            onClick={() => {
              const el = document.getElementById(`sidebar-${cat.key}`);
              if (el) el.click();
            }}
          >
            <div
              className="[display:flex] [justify-content:space-between] [align-items:center] [margin-bottom:8px]"
            >
              <span className="[font-size:0.95rem] [font-weight:600] [color:var(--text-primary)]">
                {cat.label}
              </span>
              <ChevronRight size={16} className="[color:var(--text-disabled)]" />
            </div>
            <p
              className="[font-size:0.78rem] [color:var(--text-muted)] [line-height:1.4] [margin-bottom:10px]"
            >
              {cat.description}
            </p>
            <div className="[display:flex] [gap:6px] [flex-wrap:wrap]">
              {cat.functions.slice(0, 3).map((fn) => (
                <span
                  key={fn.key}
                  className="[font-size:0.7rem] [padding:2px_8px] [border-radius:9999px] [background:var(--bg-active)] [color:var(--text-muted)]"
                >
                  {fn.label}
                </span>
              ))}
              {cat.functions.length > 3 && (
                <span
                  className="[font-size:0.7rem] [padding:2px_8px] [border-radius:9999px] [background:var(--accent-glow)] [color:var(--accent-primary)] [font-weight:600]"
                >
                  +{cat.functions.length - 3} more
                </span>
              )}
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}

const STAT_CARD_VARIANT: Record<string, string> = {
  "var(--accent-primary)": "stat-card-primary",
  "var(--accent-secondary)": "stat-card-secondary",
  "var(--accent-tertiary)": "stat-card-tertiary",
  "var(--tier-elite)": "stat-card-elite",
};

function StatCard({
  icon,
  label,
  value,
  color,
}: {
  icon: React.ReactNode;
  label: string;
  value: string;
  color: string;
}) {
  const variantClass = STAT_CARD_VARIANT[color] ?? "stat-card-primary";
  return (
    <div className="glass-card [padding:18px_20px] [display:flex] [gap:14px] [align-items:center]">
      <div
        className={`[width:42px] [height:42px] [border-radius:var(--radius-md)] [display:flex] [align-items:center] [justify-content:center] [flex-shrink:0] ${variantClass}`}
      >
        {icon}
      </div>
      <div>
        <div
          className="[font-size:0.7rem] [text-transform:uppercase] [letter-spacing:0.06em] [color:var(--text-disabled)] [font-weight:600]"
        >
          {label}
        </div>
        <div
          className="[font-size:1.25rem] [font-weight:800] [color:var(--text-primary)] [line-height:1.2]"
        >
          {value}
        </div>
      </div>
    </div>
  );
}
