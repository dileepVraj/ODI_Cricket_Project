/**
 * Sidebar.tsx — Dynamic Sidebar Navigation (Layer 3)
 * 
 * Built 100% from manifest.categories.
 * Groups categories by `group` field: intelligence, players, operations, system.
 * Rule F3: Zero format-specific code.
 */
"use client";

import { useAppContext } from "@/lib/context";
import {
    ChevronLeft,
    ChevronRight,
    Home,
    Settings,
    LayoutGrid,
    Users,
    Crosshair,
    Cpu,
} from "lucide-react";
import { useState } from "react";

// Map manifest group names → display labels and icons
const GROUP_META: Record<string, { label: string; icon: React.ReactNode }> = {
    intelligence: { label: "Intelligence", icon: <Crosshair size={12} /> },
    players: { label: "Players", icon: <Users size={12} /> },
    operations: { label: "Operations", icon: <Cpu size={12} /> },
    system: { label: "System", icon: <Settings size={12} /> },
};

// Map manifest icon strings → lucide components
const ICON_MAP: Record<string, React.ReactNode> = {
    stadium: "🏟️",
    handshake: "🤝",
    "bar-chart": "📊",
    globe: "🌍",
    user: "👤",
    swords: "⚔️",
    target: "🎯",
    rocket: "🚀",
    default: "📋",
};

interface SidebarProps {
    activeCategory: string;
    onCategorySelect: (key: string) => void;
}

export default function Sidebar({ activeCategory, onCategorySelect }: SidebarProps) {
    const { manifest, isLoadingManifest } = useAppContext();
    const [isCollapsed, setIsCollapsed] = useState(false);

    // ── Loading state ──────────────────────────────────────────────────
    if (isLoadingManifest || !manifest) {
        return (
            <aside
                id="sidebar"
                style={{
                    width: "var(--sidebar-width)",
                    background: "var(--bg-surface)",
                    borderRight: "1px solid var(--border-subtle)",
                    padding: "12px 8px",
                    display: "flex",
                    flexDirection: "column",
                    gap: "8px",
                    flexShrink: 0,
                    overflowY: "auto",
                }}
            >
                {[1, 2, 3, 4, 5, 6, 7].map((i) => (
                    <div key={i} className="skeleton" style={{ height: 38, marginBottom: 4 }} />
                ))}
            </aside>
        );
    }

    // ── Group categories by their `group` field ────────────────────────
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
            className="animate-slide-in"
            style={{
                width: sidebarWidth,
                minWidth: sidebarWidth,
                background: "var(--bg-surface)",
                borderRight: "1px solid var(--border-subtle)",
                display: "flex",
                flexDirection: "column",
                flexShrink: 0,
                transition: "width var(--transition-normal), min-width var(--transition-normal)",
                overflowY: "auto",
                overflowX: "hidden",
            }}
        >
            {/* ── Top section ────────────────────────────────────────────── */}
            <div style={{ padding: "12px 8px", flex: 1 }}>
                {/* Dashboard link */}
                <button
                    id="sidebar-dashboard"
                    className={`sidebar-item ${activeCategory === "dashboard" ? "active" : ""}`}
                    onClick={() => onCategorySelect("dashboard")}
                    style={{ width: "100%", border: "none", fontFamily: "inherit" }}
                >
                    <Home size={18} />
                    {!isCollapsed && <span>Dashboard</span>}
                </button>

                {/* ── Category groups ──────────────────────────────────────── */}
                {Object.entries(groups).map(([groupKey, cats]) => {
                    const meta = GROUP_META[groupKey] || {
                        label: groupKey.charAt(0).toUpperCase() + groupKey.slice(1),
                        icon: <LayoutGrid size={12} />,
                    };

                    return (
                        <div key={groupKey}>
                            {!isCollapsed && (
                                <div className="sidebar-group-label">
                                    {meta.label}
                                </div>
                            )}

                            {cats.map((cat) => {
                                const fnCount = cat.functions.length;
                                const iconNode = ICON_MAP[cat.icon] || ICON_MAP.default;

                                return (
                                    <button
                                        key={cat.key}
                                        id={`sidebar-${cat.key}`}
                                        className={`sidebar-item ${activeCategory === cat.key ? "active" : ""
                                            }`}
                                        onClick={() => onCategorySelect(cat.key)}
                                        title={isCollapsed ? cat.label : cat.description}
                                        style={{
                                            width: "100%",
                                            border: "none",
                                            fontFamily: "inherit",
                                        }}
                                    >
                                        <span
                                            style={{ fontSize: "1rem", flexShrink: 0, width: 24, textAlign: "center" }}
                                        >
                                            {iconNode}
                                        </span>
                                        {!isCollapsed && (
                                            <>
                                                <span
                                                    style={{
                                                        flex: 1,
                                                        textAlign: "left",
                                                        overflow: "hidden",
                                                        textOverflow: "ellipsis",
                                                        whiteSpace: "nowrap",
                                                    }}
                                                >
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

            {/* ── Collapse Toggle ────────────────────────────────────────── */}
            <div
                style={{
                    padding: "8px",
                    borderTop: "1px solid var(--border-subtle)",
                }}
            >
                <button
                    id="sidebar-collapse-toggle"
                    className="sidebar-item"
                    onClick={() => setIsCollapsed(!isCollapsed)}
                    style={{
                        width: "100%",
                        border: "none",
                        fontFamily: "inherit",
                        justifyContent: isCollapsed ? "center" : "flex-start",
                    }}
                >
                    {isCollapsed ? <ChevronRight size={18} /> : <ChevronLeft size={18} />}
                    {!isCollapsed && <span>Collapse</span>}
                </button>
            </div>
        </aside>
    );
}
