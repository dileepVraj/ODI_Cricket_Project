/**
 * Sidebar.tsx - Dynamic Sidebar Navigation (Layer 3)
 */
"use client";

import type { ManifestCategory } from "@/lib/api";
import { useAppContext } from "@/lib/context";
import {
    BarChart3,
    Building2,
    ChevronLeft,
    ChevronRight,
    ChevronsRight,
    Globe2,
    Handshake,
    Home,
    LayoutGrid,
    Rocket,
    Swords,
    Target,
    User,
    type LucideIcon,
} from "lucide-react";
import { useState } from "react";

const DASHBOARD_ITEM: { key: string; label: string; Icon: LucideIcon } = {
    key: "dashboard",
    label: "Dashboard",
    Icon: Home,
};

const CATEGORY_ICON_MAP: Record<string, LucideIcon> = {
    stadium: Building2,
    handshake: Handshake,
    "bar-chart": BarChart3,
    globe: Globe2,
    user: User,
    swords: Swords,
    target: Target,
    rocket: Rocket,
    default: LayoutGrid,
};

function formatGroupLabel(groupKey: string): string {
    return groupKey
        .split(/[-_]/)
        .filter(Boolean)
        .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
        .join(" ");
}

function groupCategories(categories: ManifestCategory[]): Array<[string, ManifestCategory[]]> {
    const groups = new Map<string, ManifestCategory[]>();

    for (const category of categories) {
        const groupKey = category.group || category.key;
        const existingGroup = groups.get(groupKey);

        if (existingGroup) {
            existingGroup.push(category);
            continue;
        }

        groups.set(groupKey, [category]);
    }

    return Array.from(groups.entries());
}

interface SidebarProps {
    activeCategory: string;
    onCategorySelect: (key: string) => void;
}

export default function Sidebar({ activeCategory, onCategorySelect }: SidebarProps) {
    const { manifest, isLoadingManifest } = useAppContext();
    const [isCollapsed, setIsCollapsed] = useState(false);
    const toggleSidebar = () => setIsCollapsed((prev) => !prev);

    if (isLoadingManifest || !manifest) {
        return (
            <aside
                id="sidebar"
                className="[width:var(--sidebar-width)] [background:var(--bg-surface)] [border-right:1px_solid_var(--border-subtle)] [padding:12px_8px] [display:flex] [flex-direction:column] [gap:8px] [flex-shrink:0] [overflow-y:auto]"
            >
                {[1, 2, 3, 4, 5, 6, 7].map((i) => (
                    <div key={i} className="skeleton [height:38px] [margin-bottom:4px]" />
                ))}
            </aside>
        );
    }

    const groupedCategories = groupCategories(manifest.categories);
    const sidebarWidth = isCollapsed
        ? "var(--sidebar-collapsed-width)"
        : "var(--sidebar-width)";

    return (
        <aside
            id="sidebar"
            className={`animate-slide-in [width:${sidebarWidth}] [min-width:${sidebarWidth}] [background:var(--bg-surface)] [border-right:1px_solid_var(--border-subtle)] [backdrop-filter:blur(12px)] [display:flex] [flex-direction:column] [flex-shrink:0] [transition:width_var(--transition-normal),_min-width_var(--transition-normal)] [overflow-y:auto] [overflow-x:hidden] [box-shadow:1px_0_12px_rgba(0,_0,_0,_0.2)] [z-index:40]`}
        >
            <div className="[padding:12px_8px] [flex:1]">
                <button
                    id="sidebar-dashboard"
                    className={`sidebar-item ${activeCategory === DASHBOARD_ITEM.key ? "active" : ""} [width:100%] [border:none] [font-family:inherit] ${isCollapsed ? "[justify-content:center]" : ""}`}
                    onClick={() => onCategorySelect(DASHBOARD_ITEM.key)}
                    title={isCollapsed ? DASHBOARD_ITEM.label : undefined}
                    aria-label={DASHBOARD_ITEM.label}
                >
                    <DASHBOARD_ITEM.Icon size={18} className="[flex-shrink:0]" />
                    {!isCollapsed && <span>{DASHBOARD_ITEM.label}</span>}
                </button>

                {isCollapsed && (
                    <button
                        id="sidebar-expand-toggle-top"
                        className="sidebar-item [width:100%] [border:none] [font-family:inherit] [justify-content:center] [margin-top:8px] [margin-bottom:6px] [color:var(--accent-primary)] [background:var(--accent-glow)] [border-color:var(--border-accent)]"
                        onClick={toggleSidebar}
                        title="Expand sidebar"
                        aria-label="Expand sidebar"
                    >
                        <ChevronsRight size={16} />
                    </button>
                )}

                {groupedCategories.map(([groupKey, categories]) => {
                    const groupLabel = formatGroupLabel(groupKey);

                    return (
                        <div key={groupKey}>
                            {!isCollapsed && <div className="sidebar-group-label">{groupLabel}</div>}

                            {categories.map((cat) => {
                                const fnCount = cat.functions.length;
                                const Icon = CATEGORY_ICON_MAP[cat.icon] || CATEGORY_ICON_MAP.default;

                                return (
                                    <button
                                        key={cat.key}
                                        id={`sidebar-${cat.key}`}
                                        className={`sidebar-item ${activeCategory === cat.key ? "active" : ""} [width:100%] [border:none] [font-family:inherit] ${isCollapsed ? "[justify-content:center]" : ""}`}
                                        onClick={() => onCategorySelect(cat.key)}
                                        title={isCollapsed ? cat.label : cat.description}
                                        aria-label={cat.label}
                                    >
                                        <Icon size={16} className="[flex-shrink:0]" />
                                        {!isCollapsed && (
                                            <>
                                                <span className="[flex:1] [text-align:left] [overflow:hidden] [text-overflow:ellipsis] [white-space:nowrap]">
                                                    {cat.label}
                                                </span>
                                                <span className="fn-count">{fnCount}</span>
                                            </>
                                        )}
                                    </button>
                                );
                            })}
                        </div>
                    );
                })}
            </div>

            <div className="[padding:8px] [border-top:1px_solid_var(--border-subtle)] [position:sticky] [bottom:0px] [background:var(--bg-surface)] [z-index:1]">
                <button
                    id="sidebar-collapse-toggle"
                    className={`sidebar-item [width:100%] [border:none] [font-family:inherit] ${isCollapsed ? "[justify-content:center]" : "[justify-content:flex-start]"}`}
                    onClick={toggleSidebar}
                    title={isCollapsed ? "Expand sidebar" : "Collapse sidebar"}
                    aria-label={isCollapsed ? "Expand sidebar" : "Collapse sidebar"}
                >
                    {isCollapsed ? <ChevronRight size={18} /> : <ChevronLeft size={18} />}
                    {!isCollapsed && <span>Collapse</span>}
                    {isCollapsed && (
                        <span className="[position:absolute] [width:1px] [height:1px] [padding:0px] [margin:-1px] [overflow:hidden] [clip:rect(0,_0,_0,_0)] [border:0px]">
                            Expand
                        </span>
                    )}
                </button>
            </div>
        </aside>
    );
}
