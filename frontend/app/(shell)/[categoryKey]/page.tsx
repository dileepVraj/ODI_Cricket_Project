"use client";

import { useState } from "react";
import { useParams, notFound } from "next/navigation";
import { useAppContext } from "@/lib/context";
import { PageHeader } from "@/components/common/PageHeader";
import { ErrorBoundary } from "@/components/common/ErrorBoundary";
import { ModuleFunctionPanel } from "@/components/layout/ModuleFunctionPanel";
import { SkeletonBar, SkeletonBlock } from "@/components/common/Skeleton";
import { resolveIcon } from "@/lib/icons";
import { stripEmoji } from "@/lib/utils";

// ── Skeleton while manifest loads ─────────────────────────────────────

function ModuleSkeleton() {
    return (
        <div
            className="module-page"
            aria-busy="true"
            aria-live="polite"
            aria-label="Loading module"
        >
            <div className="page-header">
                <div className="page-header-row">
                    <SkeletonBlock width="20px" height="20px" />
                    <SkeletonBar width="160px" height="22px" />
                </div>
                <SkeletonBar width="260px" height="12px" />
            </div>
            <div className="module-tabs">
                {Array.from({ length: 3 }).map((_, i) => (
                    <SkeletonBar key={i} width="80px" height="28px" className="mr-1" />
                ))}
            </div>
            <SkeletonBlock height="300px" />
        </div>
    );
}

// ── Module Page ───────────────────────────────────────────────────────

export default function ModulePage() {
    const { categoryKey } = useParams<{ categoryKey: string }>();
    const { manifest, isLoadingManifest } = useAppContext();
    const [activeTab, setActiveTab] = useState(0);

    if (isLoadingManifest || !manifest) {
        return <ModuleSkeleton />;
    }

    const category = manifest.categories.find((c) => c.key === categoryKey);
    if (!category || category.functions.length === 0) {
        notFound();
    }

    const safeTab = Math.min(activeTab, category.functions.length - 1);
    const activeFn = category.functions[safeTab];
    const Icon = resolveIcon(category.icon);
    const label = stripEmoji(category.label).trim();

    return (
        <div className="module-page">
            <PageHeader
                title={label}
                icon={Icon}
                subtitle={category.description}
            />

            {category.functions.length > 1 && (
                <div
                    className="module-tabs"
                    role="tablist"
                    aria-label={`${label} functions`}
                >
                    {category.functions.map((fn, i) => (
                        <button
                            key={fn.key}
                            role="tab"
                            aria-selected={i === safeTab}
                            aria-label={`Switch to ${fn.label}`}
                            className={`format-tab${i === safeTab ? " format-tab-active" : ""}`}
                            onClick={() => setActiveTab(i)}
                        >
                            {fn.label}
                        </button>
                    ))}
                </div>
            )}

            <ErrorBoundary fallbackMessage={`Failed to load ${label}.`}>
                <ModuleFunctionPanel
                    key={activeFn.key}
                    activeFn={activeFn}
                />
            </ErrorBoundary>
        </div>
    );
}
