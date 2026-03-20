"use client";
import { useEffect, useState } from "react";
import { AlertCircle, Loader2, Zap } from "lucide-react";
import { executeFunction, type ExecuteResponse } from "@/lib/api";
import { useAppContext } from "@/lib/context";
import { stripEmoji } from "@/lib/utils";
import { ErrorBoundary } from "@/components/common/ErrorBoundary";
import ExtraInputRenderer from "@/components/inputs/ExtraInputRenderer";
import SquadBuilder from "@/components/inputs/SquadBuilder";
import { ExecuteErrorPanel } from "@/components/layout/CategoryBanners";
import FunctionRenderer from "@/components/renderers/FunctionRenderer";
import SkeletonLoader from "@/components/renderers/SkeletonLoader";
import { resolveSquadBuilderConfig, getExtraInputFields, getMissingContext, buildExecuteParams, formatExecuteError } from "@/lib/executeHelpers";
const CONTEXT_BADGE_CLASS_BY_COMPLETION: Record<"complete" | "incomplete", string> = { complete: "badge-elite", incomplete: "badge-caution" };
function resolveContextBadgeClass(isContextComplete: boolean): string { return CONTEXT_BADGE_CLASS_BY_COMPLETION[isContextComplete ? "complete" : "incomplete"]; }
function EmptyCategoryState({ title, message }: { title: string; message: string }) {
  return (
    <div className="glass-card animate-fade-in [padding:32px] [text-align:center] [max-width:500px] [margin:60px_auto]">
      <AlertCircle size={48} className="[color:var(--tier-caution)] [margin-bottom:16px]" />
      <h3 className="[font-size:1.1rem] [margin-bottom:8px]">{title}</h3>
      <p className="[color:var(--text-secondary)] [font-size:0.875rem]">{message}</p>
    </div>
  );
}
export function CategoryScreen({ categoryKey }: { categoryKey: string }) {
  const { manifest, activeFormat, contextValues, venues } = useAppContext();
  const [activeTab, setActiveTab] = useState(0);
  const [result, setResult] = useState<ExecuteResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [homeXI, setHomeXI] = useState<string[]>([]);
  const [awayXI, setAwayXI] = useState<string[]>([]);
  const [extraInputValues, setExtraInputValues] = useState<Record<string, string>>({});
  const [activeView, setActiveView] = useState<string>("");
  const getContextLabel = (key: string) => manifest?.context_fields?.[key]?.label ?? key.replace(/_/g, " ");
  useEffect(() => { setActiveTab(0); setResult(null); setError(null); setExtraInputValues({}); }, [categoryKey]);
  useEffect(() => { setResult(null); setError(null); setExtraInputValues({}); setActiveView(""); }, [activeTab]);
  if (!manifest) return null;
  const category = manifest.categories.find((c) => c.key === categoryKey);
  if (!category) return <EmptyCategoryState title="Category Not Found" message={`Category "${categoryKey}" is not in the ${manifest.format_label} manifest.`} />;
  if (!category.functions || category.functions.length === 0) return <EmptyCategoryState title="No Functions Available" message={`Category "${category.label}" has no runnable functions in the manifest.`} />;
  const safeActiveTab = Math.min(activeTab, category.functions.length - 1);
  const activeFn = category.functions[safeActiveTab];
  const rawActiveFn = activeFn as unknown as Record<string, unknown>;
  const executeBtns: Array<{ key: string; label: string }> = Array.isArray(rawActiveFn["execute_buttons"]) ? (rawActiveFn["execute_buttons"] as Array<{ key: string; label: string }>) : [];
  const hasMultiButtons = executeBtns.length > 0;
  const effectiveRequiredContext = activeFn.required_context;
  const missingContext = getMissingContext(effectiveRequiredContext, contextValues);
  const canExecute = missingContext.length === 0;
  const squadBuilderConfig = resolveSquadBuilderConfig(activeFn.extra_inputs);
  const needsSquadBuilder = squadBuilderConfig.enabled;
  const squadMaxPlayers = squadBuilderConfig.maxPlayers;
  const extraInputFields = getExtraInputFields(activeFn.extra_inputs);
  const squadReady = !needsSquadBuilder || (homeXI.length !== 0 && awayXI.length !== 0);
  const missingExtraInputs = Object.entries(extraInputFields).filter(([key, field]) => Boolean(field.required) && !extraInputValues[key]).map(([, field]) => field.label);
  const canRun = canExecute && squadReady && missingExtraInputs.length === 0;
  async function runExecute(view: string = "") {
    if (!activeFn || !activeFormat) return;
    setIsLoading(true); setError(null); setResult(null);
    if (view !== "") setActiveView(view);
    try {
      const params = buildExecuteParams({ requiredContext: effectiveRequiredContext, optionalContext: activeFn.optional_context ?? [], contextValues, needsSquadBuilder, homeXI, awayXI, extraInputValues });
      const res = await executeFunction(activeFormat, activeFn.key, params);
      if (view !== "") {
        const venueLabel = venues.find((v) => v.id === extraInputValues["venue_id"])?.label ?? "";
        const rawData = typeof res.data === "object" && res.data !== null && !Array.isArray(res.data) ? (res.data as Record<string, unknown>) : {};
        setResult({ ...res, data: { ...rawData, _view: view, _venue_label: venueLabel, _years_input: extraInputValues["years"] ?? "" } });
      } else { setResult(res); }
    } catch (err) { setError(formatExecuteError(err)); } finally { setIsLoading(false); }
  }
  return (
    <div className="animate-fade-in">
      <div className="[margin-bottom:12px]">
        <h2 className="[font-size:1.35rem] [font-weight:700] [color:var(--text-primary)] [margin-bottom:4px]">{stripEmoji(category.label)}</h2>
        <p className="[color:var(--text-muted)] [font-size:0.85rem]">{category.description}</p>
      </div>
      <div className="[display:flex] [gap:4px] [margin-bottom:20px] [overflow-x:auto] [padding-bottom:4px]">
        {category.functions.map((fn, i) => (
          <button key={fn.key} id={`tab-${fn.key}`} aria-label={`Switch to ${fn.label} analysis`} className={`format-tab ${i === safeActiveTab ? "active" : ""}`} onClick={() => { setActiveTab(i); setResult(null); setError(null); }}>
            {fn.label}
          </button>
        ))}
      </div>
      <div className="[padding-top:16px]">
        <div className="[display:flex] [justify-content:space-between] [align-items:flex-start] [margin-bottom:16px] [flex-wrap:wrap] [gap:12px]">
          <div>
            <h3 className="[font-size:1.05rem] [font-weight:700] [color:var(--text-primary)] [margin-bottom:4px]">{activeFn.label}</h3>
          </div>
          <div className="[display:flex] [gap:8px] [align-items:center]">
            {effectiveRequiredContext.map((key) => {
              const val = contextValues[key];
              const isContextComplete = Boolean(val && val !== "" && val !== "All");
              return ( <span key={key} className={`badge ${resolveContextBadgeClass(isContextComplete)}`}>{stripEmoji(getContextLabel(key))}: {isContextComplete ? String(val) : "needed"}</span> );
            })}
          </div>
        </div>
        {!canExecute && (
          <p className="[font-size:0.78rem] [color:var(--text-muted)] [margin-bottom:12px]">
            Requires: {missingContext.map(getContextLabel).join(', ')}
          </p>
        )}
        {Object.keys(extraInputFields).length > 0 && activeFormat && (
          <ExtraInputRenderer formatKey={activeFormat} extraInputs={extraInputFields} contextValues={contextValues} values={extraInputValues} onChange={(key, val) => setExtraInputValues((prev) => ({ ...prev, [key]: val }))} />
        )}
        {needsSquadBuilder && activeFormat && (
          <SquadBuilder formatKey={activeFormat} teamA={String(contextValues.team_a || "")} teamB={String(contextValues.team_b || "")} maxPlayers={squadMaxPlayers} homeXI={homeXI} awayXI={awayXI} onHomeXIChange={setHomeXI} onAwayXIChange={setAwayXI} />
        )}
        {canExecute && squadReady && missingExtraInputs.length > 0 && (
          <p className="[font-size:0.78rem] [color:var(--text-muted)] [margin-bottom:12px]">
            Requires: {missingExtraInputs.join(', ')}
          </p>
        )}
        {hasMultiButtons ? (
          <div className="[display:flex] [gap:8px] [margin-bottom:20px]">
            {executeBtns.map((btn) => (
              <button key={btn.key} id={`execute-${activeFn.key}-${btn.key}`} aria-label={`Execute ${btn.label} analysis`} className={`btn-primary [display:flex] [align-items:center] [gap:8px] ${isLoading || !canRun ? "[opacity:0.5] [cursor:not-allowed]" : "[opacity:1] [cursor:pointer]"}`} onClick={() => runExecute(btn.key)} disabled={isLoading || !canRun}>
                {isLoading && activeView === btn.key ? ( <><Loader2 size={16} className="animate-spin" />Executing...</> ) : ( <><Zap size={16} />{btn.label}</> )}
              </button>
            ))}
          </div>
        ) : (
          <button id={`execute-${activeFn.key}`} aria-label="Execute analysis" className={`${result !== null && !isLoading ? 'btn-ghost' : 'btn-primary'} [margin-bottom:20px] [display:flex] [align-items:center] [gap:8px] ${isLoading || !canRun ? "[opacity:0.5] [cursor:not-allowed]" : "[opacity:1] [cursor:pointer]"}`} onClick={() => runExecute()} disabled={isLoading || !canRun}>
            {isLoading
              ? (<><Loader2 size={16} className="animate-spin" />Executing...</>)
              : !canRun
              ? (<>{!canExecute ? "Fill Required Fields" : !squadReady ? "Select Squads" : `Missing ${missingExtraInputs[0]}`}</>)
              : result !== null
              ? (<>Re-run</>)
              : (<><Zap size={16} />Execute Analysis</>)
            }
          </button>
        )}
        {error && <ExecuteErrorPanel error={error} onRetry={() => runExecute(activeView)} />}
        {isLoading && ( <div className="animate-fade-in" aria-live="polite" aria-busy="true" aria-label="Loading analysis..."><SkeletonLoader outputType={activeFn.output_type} /></div> )}
        {result && !isLoading && (
          <div aria-live="polite" className="animate-fade-in">
            <ErrorBoundary>
              <FunctionRenderer outputType={result.output_type} data={result.data} homeXI={homeXI} awayXI={awayXI} homeTeamName={String(contextValues.team_a || "")} awayTeamName={String(contextValues.team_b || "")} />
            </ErrorBoundary>
          </div>
        )}
      </div>
    </div>
  );
}
