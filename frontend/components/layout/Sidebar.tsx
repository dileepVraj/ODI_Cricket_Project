"use client";

import { useEffect, useMemo, useState } from "react";
import { usePathname, useRouter } from "next/navigation";
import {
    BarChart3,
    Building2,
    ChevronLeft,
    ChevronRight,
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
import { useAppContext } from "@/lib/context";
import { Tooltip } from "@/components/common/Tooltip";
import { stripEmoji } from "@/lib/utils";
import type { ManifestCategory } from "@/lib/api";

// ── Icon registry ────────────────────────────────────────────────────────

const ICON_MAP: Record<string, LucideIcon> = {
    stadium:     Building2,
    handshake:   Handshake,
    "bar-chart": BarChart3,
    globe:       Globe2,
    user:        User,
    swords:      Swords,
    target:      Target,
    rocket:      Rocket,
    default:     LayoutGrid,
};

function resolveIcon(iconKey: string, fallback: LucideIcon = LayoutGrid): LucideIcon {
    return ICON_MAP[iconKey] ?? fallback;
}

// ── Grouping helpers ─────────────────────────────────────────────────────

function formatGroupLabel(groupKey: string): string {
    return groupKey
        .split(/[-_]/)
        .filter(Boolean)
        .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
        .join(" ");
}

function groupCategories(cats: ManifestCategory[]): Array<[string, ManifestCategory[]]> {
    const map = new Map<string, ManifestCategory[]>();
    for (const cat of cats) {
        const key = cat.group || cat.key;
        const existing = map.get(key);
        if (existing) { existing.push(cat); continue; }
        map.set(key, [cat]);
    }
    return Array.from(map.entries());
}

// ── NavItem ──────────────────────────────────────────────────────────────

interface NavItemProps {
    id?: string;
    Icon: LucideIcon;
    label: string;
    fnCount?: number;
    active: boolean;
    collapsed: boolean;
    iconSize?: number;
    onClick: () => void;
}

function NavItem({ id, Icon, label, fnCount, active, collapsed, iconSize = 16, onClick }: NavItemProps) {
    const cls = [
        "sidebar-item",
        active ? "sidebar-item-active" : "",
        collapsed ? "sidebar-item-collapsed" : "",
    ].filter(Boolean).join(" ");

    const btn = (
        <button
            id={id}
            className={cls}
            onClick={onClick}
            aria-label={label}
            aria-current={active ? "page" : undefined}
        >
            <span className="sidebar-item-icon" aria-hidden="true">
                <Icon size={iconSize} />
            </span>
            {!collapsed && (
                <>
                    <span className="sidebar-item-label">{label}</span>
                    {fnCount !== undefined && (
                        <span className="fn-count" aria-label={`${fnCount} functions`}>
                            {fnCount}
                        </span>
                    )}
                </>
            )}
        </button>
    );

    if (collapsed) {
        return (
            <Tooltip content={label} placement="right" className="w-full">
                {btn}
            </Tooltip>
        );
    }

    return btn;
}

// ── Sidebar ──────────────────────────────────────────────────────────────

export default function Sidebar() {
    const router   = useRouter();
    const pathname = usePathname();
    const { manifest, isLoadingManifest } = useAppContext();
    const [isCollapsed, setIsCollapsed] = useState(false);

    // Scroll active nav item into view when route changes
    useEffect(() => {
        const active = document.querySelector<HTMLElement>('[aria-current="page"]');
        active?.scrollIntoView({ block: "nearest", behavior: "instant" });
    }, [pathname]);

    const dashboardItem = useMemo(() => {
        const root = manifest?.navigation_root;
        if (!root) return { key: "dashboard", label: "Dashboard", Icon: Home };
        return {
            key:   root.key,
            label: stripEmoji(root.label).trim(),
            Icon:  resolveIcon(root.icon, Home),
        };
    }, [manifest?.navigation_root]);

    const groupedCats = useMemo(
        () => groupCategories(manifest?.categories ?? []),
        [manifest?.categories],
    );

    const isDashboardActive = pathname === "/" || pathname === `/${dashboardItem.key}`;
    const isActive = (key: string) =>
        pathname === `/${key}` || pathname.startsWith(`/${key}/`);

    // ── Skeleton while loading ────────────────────────────────────────────
    if (isLoadingManifest || !manifest) {
        return (
            <aside
                className="sidebar"
                style={{ width: "var(--sidebar-width)" }}
                aria-label="Navigation"
                aria-busy="true"
                aria-live="polite"
            >
                <div className="sidebar-nav">
                    {Array.from({ length: 8 }, (_, i) => (
                        <div key={i} className="skeleton h-9 mx-1 mb-1 rounded" />
                    ))}
                </div>
            </aside>
        );
    }

    return (
        <aside
            className="sidebar animate-fade-in"
            style={{ width: isCollapsed ? "var(--sidebar-collapsed-width)" : "var(--sidebar-width)" }}
            aria-label="Navigation"
        >
            <nav className="sidebar-nav">

                {/* Dashboard */}
                <NavItem
                    id="sidebar-dashboard"
                    Icon={dashboardItem.Icon}
                    label={dashboardItem.label}
                    active={isDashboardActive}
                    collapsed={isCollapsed}
                    iconSize={18}
                    onClick={() => router.push("/")}
                />

                {/* Grouped module categories */}
                {groupedCats.map(([groupKey, cats]) => (
                    <div key={groupKey}>
                        {!isCollapsed && (
                            <span className="sidebar-group-label">
                                {formatGroupLabel(groupKey)}
                            </span>
                        )}
                        {cats.map((cat) => (
                            <NavItem
                                key={cat.key}
                                id={`sidebar-${cat.key}`}
                                Icon={resolveIcon(cat.icon)}
                                label={stripEmoji(cat.label).trim()}
                                fnCount={cat.functions.length}
                                active={isActive(cat.key)}
                                collapsed={isCollapsed}
                                onClick={() => router.push(`/${cat.key}`)}
                            />
                        ))}
                    </div>
                ))}

            </nav>

            {/* Collapse toggle — sticky bottom */}
            <div className="sidebar-footer">
                <button
                    className="sidebar-collapse-btn"
                    onClick={() => setIsCollapsed((prev) => !prev)}
                    aria-label={isCollapsed ? "Expand sidebar" : "Collapse sidebar"}
                >
                    {isCollapsed ? <ChevronRight size={16} /> : <ChevronLeft size={16} />}
                    {!isCollapsed && <span>Collapse</span>}
                </button>
            </div>
        </aside>
    );
}
