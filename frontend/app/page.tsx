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
import ExtraInputRenderer from "@/components/inputs/ExtraInputRenderer";
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

type ExtraInputFieldConfig = {
  type: string;
  label: string;
  required?: boolean;
  source?: string;
};

type SquadBuilderConfig = {
  enabled: boolean;
  maxPlayers: number;
};

const CONTEXT_BADGE_CLASS_BY_COMPLETION: Record<"complete" | "incomplete", string> = {
  complete: "badge-elite",
  incomplete: "badge-caution",
};

function resolveContextBadgeClass(isContextComplete: boolean): string {
  return CONTEXT_BADGE_CLASS_BY_COMPLETION[isContextComplete ? "complete" : "incomplete"];
}

function parsePositiveInteger(value: unknown): number | null {
  if (typeof value === "number" && Number.isInteger(value) && value > 0) return value;
  if (typeof value === "string") {
    const trimmed = value.trim();
    if (!trimmed) return null;
    const parsed = Number(trimmed);
    if (Number.isInteger(parsed) && parsed > 0) return parsed;
  }
  return null;
}

function resolveSquadBuilderConfig(extraInputs: unknown): SquadBuilderConfig {
  const defaultConfig: SquadBuilderConfig = { enabled: false, maxPlayers: 11 };
  if (!extraInputs || typeof extraInputs !== "object") return defaultConfig;

  const inputs = extraInputs as Record<string, unknown>;
  const rawSquadBuilder = inputs.squad_builder;
  if (rawSquadBuilder === undefined || rawSquadBuilder === null || rawSquadBuilder === false) {
    return defaultConfig;
  }

  const fallbackMaxPlayers =
    parsePositiveInteger(inputs.squad_max_players) ??
    parsePositiveInteger(inputs.max_players) ??
    parsePositiveInteger(inputs.max_xi) ??
    defaultConfig.maxPlayers;

  if (rawSquadBuilder === true) {
    return { enabled: true, maxPlayers: fallbackMaxPlayers };
  }

  if (typeof rawSquadBuilder === "object") {
    const cfg = rawSquadBuilder as Record<string, unknown>;
    const enabled = typeof cfg.enabled === "boolean" ? cfg.enabled : true;
    const maxPlayers =
      parsePositiveInteger(cfg.max_players) ??
      parsePositiveInteger(cfg.squad_max_players) ??
      parsePositiveInteger(cfg.max_xi) ??
      fallbackMaxPlayers;
    return { enabled, maxPlayers };
  }

  return { enabled: Boolean(rawSquadBuilder), maxPlayers: fallbackMaxPlayers };
}

function isExtraInputFieldConfig(value: unknown): value is ExtraInputFieldConfig {
  if (!value || typeof value !== "object") return false;
  const obj = value as Record<string, unknown>;
  return typeof obj.type === "string" && typeof obj.label === "string";
}

function getExtraInputFields(extraInputs: unknown): Record<string, ExtraInputFieldConfig> {
  if (!extraInputs || typeof extraInputs !== "object") return {};
  const fields: Record<string, ExtraInputFieldConfig> = {};

  for (const [key, raw] of Object.entries(extraInputs as Record<string, unknown>)) {
    if (key === "squad_builder") continue;
    if (isExtraInputFieldConfig(raw)) {
      fields[key] = raw;
    }
  }

  return fields;
}

function getMissingContext(
  requiredContext: string[],
  contextValues: Record<string, string | number>
): string[] {
  return requiredContext.filter((key) => {
    const val = contextValues[key];
    return !val || val === "" || val === "All";
  });
}

function buildExecuteParams(args: {
  requiredContext: string[];
  contextValues: Record<string, string | number>;
  needsSquadBuilder: boolean;
  homeXI: string[];
  awayXI: string[];
  extraInputValues: Record<string, string>;
}): Record<string, unknown> {
  const {
    requiredContext,
    contextValues,
    needsSquadBuilder,
    homeXI,
    awayXI,
    extraInputValues,
  } = args;

  const params: Record<string, unknown> = {};

  for (const key of requiredContext) {
    const val = contextValues[key];
    if (val && val !== "" && val !== "All") {
      params[key] = val;
    }
  }

  if (needsSquadBuilder) {
    params.home_xi = homeXI;
    params.away_xi = awayXI;
  }

  Object.entries(extraInputValues).forEach(([key, val]) => {
    if (val) params[key] = val;
  });

  return params;
}

function formatExecuteError(err: unknown): string {
  const fallback = "Execution failed. Please try again.";
  if (!(err instanceof Error)) return fallback;

  const maybeStatus = (err as Error & { status?: number }).status;
  const message = err.message?.trim();
  if (message && !message.startsWith("[") && !message.startsWith("{")) {
    return message;
  }

  if (maybeStatus === 422) {
    return "Validation Error: Please verify the selected context and required inputs.";
  }
  if (typeof maybeStatus === "number" && maybeStatus >= 500) {
    return "Server Error: Backend execution failed. Please retry in a moment.";
  }
  return fallback;
}

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
      className="[display:flex] [flex-direction:column] [height:100vh] [overflow:hidden]"
    >
      {/* Layer 1: Format Selector */}
      <FormatSelector />

      {/* Layer 2: Context Bar */}
      <ContextBar />

      {/* Layer 3: Sidebar + Content */}
      <div className="[display:flex] [flex:1] [overflow:hidden]">
        <Sidebar
          activeCategory={activeCategory}
          onCategorySelect={handleCategorySelect}
        />
        <main
          id="main-content"
          className="[flex:1] [overflow:auto] [padding:24px] [background:var(--bg-deepest)]"
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

      {/* ── Stats Cards ─────────────────────────────────────────────── */}
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

      {/* ── Category Quick Access Grid ──────────────────────────────── */}
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
              // This triggers sidebar category selection from parent
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
    <div className="glass-card [padding:18px_20px] [display:flex] [gap:14px] [align-items:center]">
      <div
        className={`[width:42px] [height:42px] [border-radius:var(--radius-md)] [display:flex] [align-items:center] [justify-content:center] [flex-shrink:0] [background:${color}15] [color:${color}]`}
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
  const [extraInputValues, setExtraInputValues] = useState<Record<string, string>>({});

  const getContextLabel = (key: string) =>
    manifest?.context_fields?.[key]?.label ?? key.replace(/_/g, " ");

  // Reset active tab when category changes
  useEffect(() => {
    setActiveTab(0);
    setResult(null);
    setError(null);
    setExtraInputValues({});
  }, [categoryKey]);

  // Reset result/error when function tab changes
  useEffect(() => {
    setResult(null);
    setError(null);
    // Keep extra inputs if the keys overlap, but usually better to clear to avoid stale values
    setExtraInputValues({});
  }, [activeTab]);

  if (!manifest) return null;

  const category = manifest.categories.find((c) => c.key === categoryKey);
  if (!category) {
    return (
      <div
        className="glass-card animate-fade-in [padding:32px] [text-align:center] [max-width:500px] [margin:60px_auto]"
      >
        <AlertCircle
          size={48}
          className="[color:var(--tier-caution)] [margin-bottom:16px]"
        />
        <h3 className="[font-size:1.1rem] [margin-bottom:8px]">
          Category Not Found
        </h3>
        <p className="[color:var(--text-secondary)] [font-size:0.875rem]">
          Category &quot;{categoryKey}&quot; is not in the {manifest.format_label} manifest.
        </p>
      </div>
    );
  }

  if (!category.functions || category.functions.length === 0) {
    return (
      <div
        className="glass-card animate-fade-in [padding:32px] [text-align:center] [max-width:500px] [margin:60px_auto]"
      >
        <AlertCircle
          size={48}
          className="[color:var(--tier-caution)] [margin-bottom:16px]"
        />
        <h3 className="[font-size:1.1rem] [margin-bottom:8px]">
          No Functions Available
        </h3>
        <p className="[color:var(--text-secondary)] [font-size:0.875rem]">
          Category &quot;{category.label}&quot; has no runnable functions in the manifest.
        </p>
      </div>
    );
  }

  const safeActiveTab = Math.min(activeTab, category.functions.length - 1);
  const activeFn = category.functions[safeActiveTab];
  const effectiveRequiredContext = activeFn.required_context;
  const missingContext = getMissingContext(effectiveRequiredContext, contextValues);

  const canExecute = missingContext.length === 0;

  // Detect if this function needs squad builder and max squad size from manifest.
  const squadBuilderConfig = resolveSquadBuilderConfig(activeFn.extra_inputs);
  const needsSquadBuilder = squadBuilderConfig.enabled;
  const squadMaxPlayers = squadBuilderConfig.maxPlayers;

  const extraInputFields = getExtraInputFields(activeFn.extra_inputs);

  // For squad functions, also check if squads are filled
  const squadReady = !needsSquadBuilder || (homeXI.length !== 0 && awayXI.length !== 0);

  // Check if required extra inputs are filled
  const missingExtraInputs = Object.entries(extraInputFields)
    .filter(([key, field]) => Boolean(field.required) && !extraInputValues[key])
    .map(([, field]) => field.label);

  const canRun = canExecute && squadReady && missingExtraInputs.length === 0;

  async function runExecute() {
    if (!activeFn || !activeFormat) return;

    setIsLoading(true);
    setError(null);
    setResult(null);

    try {
      const params = buildExecuteParams({
        requiredContext: effectiveRequiredContext,
        contextValues,
        needsSquadBuilder,
        homeXI,
        awayXI,
        extraInputValues,
      });

      const res = await executeFunction(activeFormat, activeFn.key, params);
      setResult(res);
    } catch (err) {
      setError(formatExecuteError(err));
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className="animate-fade-in">
      {/* ── Category Header ──────────────────────────────────────────── */}
      <div className="[margin-bottom:20px]">
        <h2
          className="[font-size:1.35rem] [font-weight:700] [color:var(--text-primary)] [margin-bottom:4px]"
        >
          {category.label}
        </h2>
        <p className="[color:var(--text-muted)] [font-size:0.85rem]">
          {category.description}
        </p>
      </div>

      {/* ── Function Tabs ────────────────────────────────────────────── */}
      <div
        className="[display:flex] [gap:4px] [margin-bottom:20px] [overflow-x:auto] [padding-bottom:4px]"
      >
        {category.functions.map((fn, i) => (
          <button
            key={fn.key}
            id={`tab-${fn.key}`}
            className={`format-tab ${i === safeActiveTab ? "active" : ""} [font-family:inherit]`}
            onClick={() => {
              setActiveTab(i);
              setResult(null);
              setError(null);
            }}
          >
            {fn.label}
          </button>
        ))}
      </div>

      {/* ── Active Function Panel ────────────────────────────────────── */}
      <div className="glass-card [padding:24px]">
        {/* Function info */}
        <div
          className="[display:flex] [justify-content:space-between] [align-items:flex-start] [margin-bottom:16px] [flex-wrap:wrap] [gap:12px]"
        >
          <div>
            <h3
              className="[font-size:1.05rem] [font-weight:700] [color:var(--text-primary)] [margin-bottom:4px]"
            >
              {activeFn.label}
            </h3>
            <div
              className="[display:flex] [gap:6px] [flex-wrap:wrap] [font-size:0.75rem]"
            >
              <span className="badge badge-strong">
                {activeFn.output_type}
              </span>
              <span
                className="[padding:2px_8px] [border-radius:9999px] [background:var(--bg-active)] [color:var(--text-muted)]"
              >
                {activeFn.engine_class}.{activeFn.engine_method}
              </span>
            </div>
          </div>

          <div className="[display:flex] [gap:8px] [align-items:center]">
            {/* Required context chips */}
            {effectiveRequiredContext.map((key) => {
              const val = contextValues[key];
              const isContextComplete = Boolean(val && val !== "" && val !== "All");
              const contextBadgeClass = resolveContextBadgeClass(isContextComplete);
              return (
                <span
                  key={key}
                  className={`badge ${contextBadgeClass}`}
                >
                  {getContextLabel(key)}: {isContextComplete ? String(val) : "needed"}
                </span>
              );
            })}
          </div>
        </div>

        {/* ── Missing Context Alert ──────────────────────────────────── */}
        {!canExecute && missingContext.length > 0 && (
          <div
            className="animate-fade-in [padding:16px] [background:rgba(245,_158,_11,_0.08)] [border:1px_solid_rgba(245,_158,_11,_0.25)] [border-radius:var(--radius-md)] [margin-bottom:16px] [display:flex] [gap:12px] [align-items:flex-start]"
          >
            <AlertCircle
              size={20}
              className="[color:var(--tier-caution)] [flex-shrink:0] [margin-top:2px]"
            />
            <div>
              <p
                className="[color:var(--tier-caution)] [font-size:0.9rem] [font-weight:600] [margin-bottom:6px]"
              >
                Missing Required Context
              </p>
              <p className="[color:var(--text-secondary)] [font-size:0.82rem] [line-height:1.5]">
                Please fill in the following fields in the Context Bar above:{" "}
                <strong className="[color:var(--text-primary)]">
                  {missingContext.map((k) => getContextLabel(k)).join(", ")}
                </strong>
              </p>
            </div>
          </div>
        )}

        {/* ── Extra Inputs (manifest-driven) ────────────────────────── */}
        {Object.keys(extraInputFields).length > 0 && activeFormat && (
          <ExtraInputRenderer
            formatKey={activeFormat}
            extraInputs={extraInputFields}
            contextValues={contextValues}
            values={extraInputValues}
            onChange={(key, val) =>
              setExtraInputValues((prev) => ({ ...prev, [key]: val }))
            }
          />
        )}

        {/* ── Squad Builder (for squad-dependent functions) ───────── */}
        {needsSquadBuilder && activeFormat && (
          <SquadBuilder
            formatKey={activeFormat}
            teamA={String(contextValues.team_a || "")}
            teamB={String(contextValues.team_b || "")}
            maxPlayers={squadMaxPlayers}
            homeXI={homeXI}
            awayXI={awayXI}
            onHomeXIChange={setHomeXI}
            onAwayXIChange={setAwayXI}
          />
        )}

        {/* Squad not ready alert */}
        {needsSquadBuilder && canExecute && !squadReady && (
          <div
            className="animate-fade-in [padding:14px] [background:rgba(59,_130,_246,_0.08)] [border:1px_solid_rgba(59,_130,_246,_0.25)] [border-radius:var(--radius-md)] [margin-bottom:16px] [display:flex] [gap:12px] [align-items:center]"
          >
            <Users size={18} className="[color:var(--accent-blue)] [flex-shrink:0]" />
            <p className="[color:var(--text-secondary)] [font-size:0.82rem]">
              Select players for <strong className="[color:var(--text-primary)]">Home XI</strong> and{" "}
              <strong className="[color:var(--text-primary)]">Away XI</strong> above, or click{" "}
              <strong className="[color:var(--accent-blue)]">Load Squad</strong> to auto-fill.
            </p>
          </div>
        )}

        {/* Extra inputs missing alert */}
        {canExecute && squadReady && missingExtraInputs.length > 0 && (
          <div
            className="animate-fade-in [padding:14px] [background:rgba(59,_130,_246,_0.08)] [border:1px_solid_rgba(59,_130,_246,_0.25)] [border-radius:var(--radius-md)] [margin-bottom:16px] [display:flex] [gap:12px] [align-items:center]"
          >
            <AlertCircle size={18} className="[color:var(--accent-blue)] [flex-shrink:0]" />
            <p className="[color:var(--text-secondary)] [font-size:0.82rem]">
              Please select <strong className="[color:var(--text-primary)]">{missingExtraInputs.join(", ")}</strong> to proceed.
            </p>
          </div>
        )}

        {/* Execute button */}
        <button
          id={`execute-${activeFn.key}`}
          className={`btn-primary [margin-bottom:20px] [display:flex] [align-items:center] [gap:8px] ${isLoading || !canRun ? "[opacity:0.5] [cursor:not-allowed]" : "[opacity:1] [cursor:pointer]"}`}
          onClick={runExecute}
          disabled={isLoading || !canRun}
        >
          {isLoading ? (
            <>
              <Loader2 size={16} className="animate-spin" />
              Executing...
            </>
          ) : !canRun ? (
            <>
              <AlertCircle size={16} />
              {!canExecute
                ? "Fill Required Fields"
                : !squadReady
                  ? "Select Squads"
                  : `Missing ${missingExtraInputs[0]}`}
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
            className="animate-fade-in [padding:14px] [background:rgba(239,_68,_68,_0.08)] [border:1px_solid_rgba(239,_68,_68,_0.25)] [border-radius:var(--radius-md)] [margin-bottom:16px]"
          >
            <div className="[display:flex] [gap:10px] [align-items:flex-start]">
              <AlertCircle
                size={18}
                className="[color:var(--tier-danger)] [flex-shrink:0] [margin-top:2px]"
              />
              <div className="[flex:1]">
                <p className="[color:var(--tier-danger)] [font-size:0.9rem] [font-weight:600] [margin-bottom:4px]">
                  Execution Failed
                </p>
                <p className="[color:var(--text-secondary)] [font-size:0.82rem] [line-height:1.5]">
                  {error}
                </p>
              </div>
            </div>
            <button
              className="btn-ghost [margin-top:10px] [font-size:0.8rem] [display:flex] [align-items:center] [gap:6px]"
              onClick={runExecute}
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
