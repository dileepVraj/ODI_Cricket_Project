/**
 * app/page.tsx — Main Application Shell
 * 
 * Composes the 3-layer layout:
 *   Layer 1: FormatSelector (top)
 *   Layer 2: ContextBar (below top)
 *   Layer 3: Sidebar (left) + Main Content (right)
 * 
 * Renders Dashboard or CategoryScreen based on sidebar selection.
 */
"use client";

import { useState, useEffect } from "react";
import { AppProvider, useAppContext } from "@/lib/context";
import FormatSelector from "@/components/layout/FormatSelector";
import ContextBar from "@/components/layout/ContextBar";
import Sidebar from "@/components/layout/Sidebar";
import { executeFunction, type ExecuteResponse } from "@/lib/api";
import FunctionRenderer from "@/components/renderers/FunctionRenderer";
import SkeletonLoader from "@/components/renderers/SkeletonLoader";
import SquadBuilder from "@/components/inputs/SquadBuilder";
import {
  Activity,
  TrendingUp,
  Database,
  Zap,
  AlertCircle,
  Loader2,
  ChevronRight,
  Users,
} from "lucide-react";

export default function Page() {
  return (
    <AppProvider>
      <AppShell />
    </AppProvider>
  );
}

function AppShell() {
  // Hash-based deep-linking: /#venue_intel syncs to category
  const [activeCategory, setActiveCategory] = useState(() => {
    if (typeof window !== "undefined") {
      const hash = window.location.hash.replace("#", "");
      return hash || "dashboard";
    }
    return "dashboard";
  });

  // Sync hash changes → state
  useEffect(() => {
    function onHashChange() {
      const hash = window.location.hash.replace("#", "");
      if (hash) setActiveCategory(hash);
      else setActiveCategory("dashboard");
    }
    window.addEventListener("hashchange", onHashChange);
    return () => window.removeEventListener("hashchange", onHashChange);
  }, []);

  // Sync state → hash
  const handleCategorySelect = (cat: string) => {
    setActiveCategory(cat);
    if (cat === "dashboard") {
      window.history.replaceState(null, "", window.location.pathname);
    } else {
      window.history.replaceState(null, "", `#${cat}`);
    }
  };

  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        height: "100vh",
        overflow: "hidden",
      }}
    >
      {/* Layer 1: Format Selector */}
      <FormatSelector />

      {/* Layer 2: Context Bar */}
      <ContextBar />

      {/* Layer 3: Sidebar + Content */}
      <div style={{ display: "flex", flex: 1, overflow: "hidden" }}>
        <Sidebar
          activeCategory={activeCategory}
          onCategorySelect={handleCategorySelect}
        />
        <main
          id="main-content"
          style={{
            flex: 1,
            overflow: "auto",
            padding: "24px",
            background: "var(--bg-deepest)",
          }}
        >
          {activeCategory === "dashboard" ? (
            <DashboardScreen />
          ) : (
            <CategoryScreen categoryKey={activeCategory} />
          )}
        </main>
      </div>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════════════
// DASHBOARD SCREEN
// ═══════════════════════════════════════════════════════════════════════════

function DashboardScreen() {
  const { manifest, activeFormat } = useAppContext();

  if (!manifest) return null;

  const totalFunctions = manifest.categories.reduce(
    (acc, cat) => acc + cat.functions.length,
    0
  );

  return (
    <div className="animate-fade-in">
      {/* ── Welcome Header ──────────────────────────────────────────── */}
      <div style={{ marginBottom: "32px" }}>
        <h2
          className="gradient-text"
          style={{ fontSize: "1.75rem", fontWeight: 800, marginBottom: "8px" }}
        >
          {manifest.format_icon} {manifest.format_label} Command Center
        </h2>
        <p style={{ color: "var(--text-secondary)", fontSize: "0.9rem" }}>
          Algorithmic trading intelligence powered by deep cricket analytics
        </p>
      </div>

      {/* ── Stats Cards ─────────────────────────────────────────────── */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fill, minmax(220px, 1fr))",
          gap: "16px",
          marginBottom: "32px",
        }}
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

      {/* ── Category Quick Access Grid ──────────────────────────────── */}
      <h3
        style={{
          fontSize: "1rem",
          fontWeight: 700,
          color: "var(--text-primary)",
          marginBottom: "16px",
        }}
      >
        Quick Access
      </h3>
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))",
          gap: "12px",
        }}
      >
        {manifest.categories.map((cat, i) => (
          <button
            key={cat.key}
            className="glass-card glass-card-hover"
            style={{
              padding: "16px 20px",
              cursor: "pointer",
              textAlign: "left",
              border: "1px solid var(--glass-border)",
              fontFamily: "inherit",
              background: "var(--glass-bg)",
              animationDelay: `${i * 60}ms`,
            }}
            onClick={() => {
              // This triggers sidebar category selection from parent
              const el = document.getElementById(`sidebar-${cat.key}`);
              if (el) el.click();
            }}
          >
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                marginBottom: "8px",
              }}
            >
              <span style={{ fontSize: "0.95rem", fontWeight: 600, color: "var(--text-primary)" }}>
                {cat.label}
              </span>
              <ChevronRight size={16} style={{ color: "var(--text-disabled)" }} />
            </div>
            <p
              style={{
                fontSize: "0.78rem",
                color: "var(--text-muted)",
                lineHeight: 1.4,
                marginBottom: "10px",
              }}
            >
              {cat.description}
            </p>
            <div style={{ display: "flex", gap: "6px", flexWrap: "wrap" }}>
              {cat.functions.slice(0, 3).map((fn) => (
                <span
                  key={fn.key}
                  style={{
                    fontSize: "0.7rem",
                    padding: "2px 8px",
                    borderRadius: "9999px",
                    background: "var(--bg-active)",
                    color: "var(--text-muted)",
                  }}
                >
                  {fn.label}
                </span>
              ))}
              {cat.functions.length > 3 && (
                <span
                  style={{
                    fontSize: "0.7rem",
                    padding: "2px 8px",
                    borderRadius: "9999px",
                    background: "var(--accent-glow)",
                    color: "var(--accent-primary)",
                    fontWeight: 600,
                  }}
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
  return (
    <div
      className="glass-card"
      style={{ padding: "18px 20px", display: "flex", gap: "14px", alignItems: "center" }}
    >
      <div
        style={{
          width: 42,
          height: 42,
          borderRadius: "var(--radius-md)",
          background: `${color}15`,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          color,
          flexShrink: 0,
        }}
      >
        {icon}
      </div>
      <div>
        <div
          style={{
            fontSize: "0.7rem",
            textTransform: "uppercase",
            letterSpacing: "0.06em",
            color: "var(--text-disabled)",
            fontWeight: 600,
          }}
        >
          {label}
        </div>
        <div
          style={{
            fontSize: "1.25rem",
            fontWeight: 800,
            color: "var(--text-primary)",
            lineHeight: 1.2,
          }}
        >
          {value}
        </div>
      </div>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════════════
// CATEGORY SCREEN (Dynamic Tabs + Execute)
// ═══════════════════════════════════════════════════════════════════════════

function CategoryScreen({ categoryKey }: { categoryKey: string }) {
  const { manifest, activeFormat, contextValues } = useAppContext();
  const [activeTab, setActiveTab] = useState(0);
  const [result, setResult] = useState<ExecuteResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [homeXI, setHomeXI] = useState<string[]>([]);
  const [awayXI, setAwayXI] = useState<string[]>([]);

  // Human-readable labels for context field keys
  const contextLabels: Record<string, string> = {
    venue: "🏟️ Venue",
    team_a: "🏏 Home Team",
    team_b: "🏏 Away Team",
    years: "📅 Years",
    region: "🌍 Region",
  };

  // Reset active tab when category changes
  useEffect(() => {
    setActiveTab(0);
    setResult(null);
    setError(null);
  }, [categoryKey]);

  if (!manifest) return null;

  const category = manifest.categories.find((c) => c.key === categoryKey);
  if (!category) {
    return (
      <div
        className="glass-card animate-fade-in"
        style={{
          padding: "40px",
          textAlign: "center",
          maxWidth: 500,
          margin: "60px auto",
        }}
      >
        <AlertCircle
          size={48}
          style={{ color: "var(--tier-caution)", marginBottom: "16px" }}
        />
        <h3 style={{ fontSize: "1.1rem", marginBottom: "8px" }}>
          Category Not Found
        </h3>
        <p style={{ color: "var(--text-secondary)", fontSize: "0.875rem" }}>
          Category &quot;{categoryKey}&quot; is not in the {manifest.format_label} manifest.
        </p>
      </div>
    );
  }

  const activeFn = category.functions[activeTab];

  // Check if required context is filled
  const missingContext = activeFn.required_context.filter((key) => {
    const val = contextValues[key];
    return !val || val === "" || val === "All";
  });

  const canExecute = missingContext.length === 0 ||
    // Allow execution if only optional fields are missing
    missingContext.every((key) => {
      const field = manifest.context_fields[key];
      return field && !field.required;
    });

  // Detect if this function needs squad builder
  const needsSquadBuilder = activeFn.extra_inputs &&
    typeof activeFn.extra_inputs === "object" &&
    (activeFn.extra_inputs as Record<string, unknown>).squad_builder === true;

  // For squad functions, also check if squads are filled
  const squadReady = !needsSquadBuilder || (homeXI.length > 0 && awayXI.length > 0);
  const canRun = canExecute && squadReady;

  async function runExecute() {
    if (!activeFn || !activeFormat) return;

    setIsLoading(true);
    setError(null);
    setResult(null);

    try {
      // Build params from context values — only send what the function needs
      const params: Record<string, unknown> = {};
      for (const key of activeFn.required_context) {
        const val = contextValues[key];
        if (val && val !== "" && val !== "All") {
          params[key] = val;
        }
      }

      // Add squad lists if this function needs them
      if (needsSquadBuilder) {
        params.home_xi = homeXI;
        params.away_xi = awayXI;
      }

      const res = await executeFunction(activeFormat, activeFn.key, params);
      setResult(res);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Execution failed");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className="animate-fade-in">
      {/* ── Category Header ──────────────────────────────────────────── */}
      <div style={{ marginBottom: "20px" }}>
        <h2
          style={{
            fontSize: "1.35rem",
            fontWeight: 700,
            color: "var(--text-primary)",
            marginBottom: "4px",
          }}
        >
          {category.label}
        </h2>
        <p style={{ color: "var(--text-muted)", fontSize: "0.85rem" }}>
          {category.description}
        </p>
      </div>

      {/* ── Function Tabs ────────────────────────────────────────────── */}
      <div
        style={{
          display: "flex",
          gap: "4px",
          marginBottom: "20px",
          overflowX: "auto",
          paddingBottom: "4px",
        }}
      >
        {category.functions.map((fn, i) => (
          <button
            key={fn.key}
            id={`tab-${fn.key}`}
            className={`format-tab ${i === activeTab ? "active" : ""}`}
            onClick={() => {
              setActiveTab(i);
              setResult(null);
              setError(null);
            }}
            style={{ fontFamily: "inherit" }}
          >
            {fn.label}
          </button>
        ))}
      </div>

      {/* ── Active Function Panel ────────────────────────────────────── */}
      <div className="glass-card" style={{ padding: "24px" }}>
        {/* Function info */}
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "flex-start",
            marginBottom: "16px",
            flexWrap: "wrap",
            gap: "12px",
          }}
        >
          <div>
            <h3
              style={{
                fontSize: "1.05rem",
                fontWeight: 700,
                color: "var(--text-primary)",
                marginBottom: "4px",
              }}
            >
              {activeFn.label}
            </h3>
            <div
              style={{
                display: "flex",
                gap: "6px",
                flexWrap: "wrap",
                fontSize: "0.75rem",
              }}
            >
              <span className="badge badge-strong">
                {activeFn.output_type}
              </span>
              <span
                style={{
                  padding: "2px 8px",
                  borderRadius: "9999px",
                  background: "var(--bg-active)",
                  color: "var(--text-muted)",
                }}
              >
                {activeFn.engine_class}.{activeFn.engine_method}
              </span>
            </div>
          </div>

          <div style={{ display: "flex", gap: "8px", alignItems: "center" }}>
            {/* Required context chips */}
            {activeFn.required_context.map((key) => {
              const val = contextValues[key];
              const isFilled = val && val !== "" && val !== "All";
              return (
                <span
                  key={key}
                  className={`badge ${isFilled ? "badge-elite" : "badge-caution"}`}
                >
                  {contextLabels[key] || key}: {isFilled ? String(val) : "needed"}
                </span>
              );
            })}
          </div>
        </div>

        {/* ── Missing Context Alert ──────────────────────────────────── */}
        {!canExecute && missingContext.length > 0 && (
          <div
            className="animate-fade-in"
            style={{
              padding: "16px 20px",
              background: "rgba(245, 158, 11, 0.08)",
              border: "1px solid rgba(245, 158, 11, 0.25)",
              borderRadius: "var(--radius-md)",
              marginBottom: "16px",
              display: "flex",
              gap: "12px",
              alignItems: "flex-start",
            }}
          >
            <AlertCircle
              size={20}
              style={{ color: "var(--tier-caution)", flexShrink: 0, marginTop: 2 }}
            />
            <div>
              <p
                style={{
                  color: "var(--tier-caution)",
                  fontSize: "0.9rem",
                  fontWeight: 600,
                  marginBottom: "6px",
                }}
              >
                Missing Required Context
              </p>
              <p style={{ color: "var(--text-secondary)", fontSize: "0.82rem", lineHeight: 1.5 }}>
                Please fill in the following fields in the Context Bar above:{" "}
                <strong style={{ color: "var(--text-primary)" }}>
                  {missingContext.map((k) => contextLabels[k] || k).join(", ")}
                </strong>
              </p>
            </div>
          </div>
        )}

        {/* ── Squad Builder (for squad-dependent functions) ───────── */}
        {needsSquadBuilder && activeFormat && (
          <SquadBuilder
            formatKey={activeFormat}
            teamA={String(contextValues.team_a || "")}
            teamB={String(contextValues.team_b || "")}
            homeXI={homeXI}
            awayXI={awayXI}
            onHomeXIChange={setHomeXI}
            onAwayXIChange={setAwayXI}
          />
        )}

        {/* Squad not ready alert */}
        {needsSquadBuilder && canExecute && !squadReady && (
          <div
            className="animate-fade-in"
            style={{
              padding: "14px 18px",
              background: "rgba(96, 165, 250, 0.08)",
              border: "1px solid rgba(96, 165, 250, 0.25)",
              borderRadius: "var(--radius-md)",
              marginBottom: "16px",
              display: "flex",
              gap: "12px",
              alignItems: "center",
            }}
          >
            <Users size={18} style={{ color: "var(--accent-blue)", flexShrink: 0 }} />
            <p style={{ color: "var(--text-secondary)", fontSize: "0.82rem" }}>
              Select players for <strong style={{ color: "var(--text-primary)" }}>Home XI</strong> and{" "}
              <strong style={{ color: "var(--text-primary)" }}>Away XI</strong> above, or click{" "}
              <strong style={{ color: "var(--accent-blue)" }}>Load Squad</strong> to auto-fill.
            </p>
          </div>
        )}

        {/* Execute button */}
        <button
          id={`execute-${activeFn.key}`}
          className="btn-primary"
          onClick={runExecute}
          disabled={isLoading || !canRun}
          style={{
            marginBottom: "20px",
            opacity: isLoading || !canRun ? 0.5 : 1,
            cursor: isLoading || !canRun ? "not-allowed" : "pointer",
            display: "flex",
            alignItems: "center",
            gap: "8px",
          }}
        >
          {isLoading ? (
            <>
              <Loader2 size={16} className="animate-spin" style={{ animation: "spin 1s linear infinite" }} />
              Executing...
            </>
          ) : !canRun ? (
            <>
              <AlertCircle size={16} />
              {!canExecute ? "Fill Required Fields" : "Select Squads"}
            </>
          ) : (
            <>
              <Zap size={16} />
              Execute Analysis
            </>
          )}
        </button>

        {/* Error display with Retry */}
        {error && (
          <div
            className="animate-fade-in"
            style={{
              padding: "14px 18px",
              background: "rgba(239, 68, 68, 0.08)",
              border: "1px solid rgba(239, 68, 68, 0.25)",
              borderRadius: "var(--radius-md)",
              marginBottom: "16px",
            }}
          >
            <div style={{ display: "flex", gap: "10px", alignItems: "flex-start" }}>
              <AlertCircle
                size={18}
                style={{ color: "var(--tier-danger)", flexShrink: 0, marginTop: 2 }}
              />
              <div style={{ flex: 1 }}>
                <p style={{ color: "var(--tier-danger)", fontSize: "0.9rem", fontWeight: 600, marginBottom: "4px" }}>
                  Execution Failed
                </p>
                <p style={{ color: "var(--text-secondary)", fontSize: "0.82rem", lineHeight: 1.5 }}>
                  {error}
                </p>
              </div>
            </div>
            <button
              className="btn-ghost"
              onClick={runExecute}
              style={{
                marginTop: "10px",
                fontSize: "0.8rem",
                display: "flex",
                alignItems: "center",
                gap: "6px",
              }}
            >
              <Zap size={14} />
              Retry
            </button>
          </div>
        )}

        {/* ── Loading Skeleton ──────────────────────────────────────── */}
        {isLoading && (
          <div className="animate-fade-in">
            <SkeletonLoader outputType={activeFn.output_type} />
          </div>
        )}

        {/* Result display — Phase 3 FunctionRenderer dispatcher */}
        {result && !isLoading && (
          <div className="animate-fade-in">
            <FunctionRenderer
              outputType={result.output_type}
              data={result.data}
            />
          </div>
        )}
      </div>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════════════
// Phase 2 generic renderers removed — replaced by Phase 3 FunctionRenderer
// dispatcher at: components/renderers/FunctionRenderer.tsx
// which routes output_type → specialized renderers:
//   report          → ReportCard
//   comparison_table → ComparisonTable
//   matrix_table    → MatrixTable
//   form_table      → FormTable
//   table           → DataTable
//   prediction_card → PredictionCard
//   profile_card    → PlayerProfileCard
//   matchup_table   → MatchupTable
//   download_json   → DownloadPanel
// ═══════════════════════════════════════════════════════════════════════════

