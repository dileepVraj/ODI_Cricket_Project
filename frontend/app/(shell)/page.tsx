"use client";

import Link from "next/link";
import { Home, ChevronRight } from "lucide-react";
import { useAppContext } from "@/lib/context";
import { CategoryIcon } from "@/lib/icons";
import { SkeletonBar, SkeletonBlock } from "@/components/common/Skeleton";
import type { ManifestCategory } from "@/lib/api";

// ── Context tag derivation ────────────────────────────────────────────
// Maps manifest required_context keys to display tag labels.
// team_b collapses into TEAMS (same tag as team_a). years is skipped.

const CONTEXT_KEY_TAG: Record<string, string | null> = {
    venue:  "VENUE",
    team_a: "TEAMS",
    team_b: null,    // deduplicates into TEAMS via team_a normalisation
    years:  null,    // not meaningful on a navigation card
    region: "REGION",
};

function getContextTags(category: ManifestCategory): string[] {
    const seen = new Set<string>();
    const tags: string[] = [];
    for (const fn of category.functions) {
        for (const key of fn.required_context) {
            // Normalise: team_b and team_a both produce one "TEAMS" tag
            const normKey = key === "team_b" ? "team_a" : key;
            const tag = CONTEXT_KEY_TAG[normKey];
            if (tag !== undefined && tag !== null && !seen.has(tag)) {
                seen.add(tag);
                tags.push(tag);
            }
            // Handle any player-related keys not in the static map
            if (tag === undefined && key.includes("player") && !seen.has("PLAYER")) {
                seen.add("PLAYER");
                tags.push("PLAYER");
            }
        }
    }
    return tags;
}

// ── Module Card ───────────────────────────────────────────────────────

function ModuleCard({ category }: { category: ManifestCategory }) {
    const isPrediction = category.group === "prediction";
    const tags = getContextTags(category);
    const iconClass = isPrediction
        ? "card-module-icon card-module-icon--amber"
        : "card-module-icon card-module-icon--indigo";

    return (
        <Link
            href={`/${category.key}`}
            className="card-module"
            aria-label={`Go to ${category.label}`}
        >
            <div className="card-module-header">
                <div className={iconClass} aria-hidden="true">
                    <CategoryIcon iconKey={category.icon} size={18} />
                </div>
                <div className="card-module-arrow" aria-hidden="true">
                    <ChevronRight size={14} />
                </div>
            </div>

            <p className="card-module-name">{category.label}</p>
            <p className="card-module-desc">{category.description}</p>

            <div className="card-module-footer">
                <div className="card-module-tags" aria-label="Required context">
                    {tags.map((tag) => (
                        <span key={tag} className="card-module-tag">{tag}</span>
                    ))}
                </div>
                <span className="card-module-fn-count">
                    {category.functions.length} functions
                </span>
            </div>
        </Link>
    );
}

// ── Dashboard Skeleton (manifest still loading) ───────────────────────

function DashboardSkeleton() {
    return (
        <div className="dashboard-page" aria-busy="true" aria-live="polite" aria-label="Loading dashboard">
            <div className="dashboard-header">
                <div className="dashboard-header-title">
                    <SkeletonBlock width="20px" height="20px" />
                    <SkeletonBar width="120px" height="20px" />
                </div>
                <SkeletonBar width="180px" height="12px" />
            </div>
            <div className="dashboard-grid" aria-hidden="true">
                {Array.from({ length: 9 }).map((_, i) => (
                    <SkeletonBlock key={i} height="160px" />
                ))}
            </div>
        </div>
    );
}

// ── Dashboard Page ────────────────────────────────────────────────────

export default function DashboardPage() {
    const { manifest, isLoadingManifest } = useAppContext();

    if (isLoadingManifest || !manifest) {
        return <DashboardSkeleton />;
    }

    const subtitle = `${manifest.format_label} · ${manifest.categories.length} modules available`;

    return (
        <div className="dashboard-page">
            <div className="dashboard-header">
                <div className="dashboard-header-title">
                    <Home size={20} color="var(--accent-ui)" aria-hidden="true" />
                    <h1 className="page-title">Dashboard</h1>
                </div>
                <p className="page-subtitle">{subtitle}</p>
            </div>

            <div
                className="dashboard-grid"
                role="list"
                aria-label="Analysis modules"
            >
                {manifest.categories.map((category) => (
                    <div key={category.key} role="listitem">
                        <ModuleCard category={category} />
                    </div>
                ))}
            </div>
        </div>
    );
}
