"use client";

import { useEffect, useState } from "react";
import { AlertCircle, Loader2, Users, Zap } from "lucide-react";
import { executeFunction, type ExecuteResponse } from "@/lib/api";
import { useAppContext } from "@/lib/context";
import { ErrorBoundary } from "@/components/common/ErrorBoundary";
import ExtraInputRenderer from "@/components/inputs/ExtraInputRenderer";
import SquadBuilder from "@/components/inputs/SquadBuilder";
import FunctionRenderer from "@/components/renderers/FunctionRenderer";
import SkeletonLoader from "@/components/renderers/SkeletonLoader";

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

export function CategoryScreen({ categoryKey }: { categoryKey: string }) {
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

  useEffect(() => {
    setActiveTab(0);
    setResult(null);
    setError(null);
    setExtraInputValues({});
  }, [categoryKey]);

  useEffect(() => {
    setResult(null);
    setError(null);
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
  const squadBuilderConfig = resolveSquadBuilderConfig(activeFn.extra_inputs);
  const needsSquadBuilder = squadBuilderConfig.enabled;
  const squadMaxPlayers = squadBuilderConfig.maxPlayers;
  const extraInputFields = getExtraInputFields(activeFn.extra_inputs);
  const squadReady = !needsSquadBuilder || (homeXI.length !== 0 && awayXI.length !== 0);
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

      <div className="glass-card [padding:24px]">
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

        {error && (
          <div
            role="alert"
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

        {isLoading && (
          <div className="animate-fade-in">
            <SkeletonLoader outputType={activeFn.output_type} />
          </div>
        )}

        {result && !isLoading && (
          <div aria-live="polite" className="animate-fade-in">
            <ErrorBoundary>
              <FunctionRenderer
                outputType={result.output_type}
                data={result.data}
              />
            </ErrorBoundary>
          </div>
        )}
      </div>
    </div>
  );
}
