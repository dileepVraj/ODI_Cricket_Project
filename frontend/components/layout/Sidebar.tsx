/**
 * Sidebar.tsx - Dynamic Sidebar Navigation (Layer 3)
 */
"use client";

import { useAppContext } from "@/lib/context";
import {
    ChevronLeft,
    ChevronRight,
    ChevronsRight,
    Home,
    Settings,
    LayoutGrid,
    Users,
    Crosshair,
    Cpu,
} from "lucide-react";
import { useState } from "react";

const GROUP_META: Record<string, { label: string; icon: React.ReactNode }> = {
    intelligence: { label: "Intelligence", icon: <Crosshair size={12} /> },
    players: { label: "Players", icon: <Users size={12} /> },
    operations: { label: "Operations", icon: <Cpu size={12} /> },
    system: { label: "System", icon: <Settings size={12} /> },
};

const ICON_MAP: Record<string, React.ReactNode> = {
    stadium: "🏟️",
    handshake: "🤝",
    "bar-chart": "📊",
    globe: "🌍",
    user: "👤",
    swords: "⚔️",
    target: "🎯",
    rocket: "🚀",
    default: "📂",
};

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

    const groups: Record<string, typeof manifest.categories> = {};
    for (const cat of manifest.categories) {
        const g = cat.group || "other";
        if (!groups[g]) groups[g] = [];
        groups[g].push(cat);
    }

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
                    className={`sidebar-item ${activeCategory === "dashboard" ? "active" : ""} [width:100%] [border:none] [font-family:inherit]`}
                    onClick={() => onCategorySelect("dashboard")}
                >
                    <Home size={18} />
                    {!isCollapsed && <span>Dashboard</span>}
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

                {Object.entries(groups).map(([groupKey, cats]) => {
                    const meta = GROUP_META[groupKey] || {
                        label: groupKey.charAt(0).toUpperCase() + groupKey.slice(1),
                        icon: <LayoutGrid size={12} />,
                    };

                    return (
                        <div key={groupKey}>
                            {!isCollapsed && <div className="sidebar-group-label">{meta.label}</div>}

                            {cats.map((cat) => {
                                const fnCount = cat.functions.length;
                                const iconNode = ICON_MAP[cat.icon] || ICON_MAP.default;

                                return (
                                    <button
                                        key={cat.key}
                                        id={`sidebar-${cat.key}`}
                                        className={`sidebar-item ${activeCategory === cat.key ? "active" : ""} [width:100%] [border:none] [font-family:inherit]`}
                                        onClick={() => onCategorySelect(cat.key)}
                                        title={isCollapsed ? cat.label : cat.description}
                                    >
                                        <span className="[font-size:1rem] [flex-shrink:0] [width:24px] [text-align:center]">
                                            {iconNode}
                                        </span>
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
