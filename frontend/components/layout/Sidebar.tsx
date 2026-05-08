"use client";

import { useEffect, useMemo, useState } from "react";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { ChevronLeft, ChevronRight, Home } from "lucide-react";
import { useAppContext } from "@/lib/context";
import { resolveIcon } from "@/lib/icons";
import { stripEmoji } from "@/lib/utils";
import type { ManifestCategory } from "@/lib/api";
import { NavItem } from "./SidebarNavItem";
import TradingGroup from "./TradingGroup";

function formatGroupLabel(groupKey: string): string {
    return groupKey
        .split(/[-_]/)
        .filter(Boolean)
        .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
        .join(" ");
}

function groupCategories(cats: ManifestCategory[]): Array<[string, ManifestCategory[]]> {
    const map = new Map<string, ManifestCategory[]>();
    for (const cat of cats) {
        const key = cat.group || cat.key;
        const existing = map.get(key);
        if (existing) {
            existing.push(cat);
            continue;
        }
        map.set(key, [cat]);
    }
    return Array.from(map.entries());
}

function isRouteActive(pathname: string, route: string): boolean {
    return pathname === route || pathname.startsWith(`${route}/`);
}

export default function Sidebar() {
    const router = useRouter();
    const pathname = usePathname();
    const searchParams = useSearchParams();
    const { manifest, isLoadingManifest } = useAppContext();
    const [isCollapsed, setIsCollapsed] = useState(false);

    useEffect(() => {
        const active = document.querySelector<HTMLElement>('[aria-current="page"]');
        active?.scrollIntoView({ block: "nearest", behavior: "instant" });
    }, [pathname]);

    const dashboardItem = useMemo(() => {
        const root = manifest?.navigation_root;
        if (!root) return { key: "dashboard", label: "Dashboard", Icon: Home };
        return {
            key: root.key,
            label: stripEmoji(root.label).trim(),
            Icon: resolveIcon(root.icon, Home),
        };
    }, [manifest?.navigation_root]);

    const groupedCats = useMemo(
        () => groupCategories(manifest?.categories ?? []),
        [manifest?.categories],
    );

    const isDashboardActive = pathname === "/" || pathname === `/${dashboardItem.key}`;

    function handleTradingDashboardClick() {
        const params = new URLSearchParams();
        const format = searchParams.get("format");
        if (format) {
            params.set("format", format);
        }
        params.set("action", "new");
        router.push(`/trading-dashboard?${params.toString()}`);
    }

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
                <NavItem
                    id="sidebar-dashboard"
                    Icon={dashboardItem.Icon}
                    label={dashboardItem.label}
                    active={isDashboardActive}
                    collapsed={isCollapsed}
                    iconSize={18}
                    onClick={() => router.push("/")}
                />

                <TradingGroup
                    key={pathname}
                    pathname={pathname}
                    isCollapsed={isCollapsed}
                    onExpandSidebar={() => setIsCollapsed(false)}
                    onOpenTradingDashboard={handleTradingDashboardClick}
                    onOpenHistory={() => router.push("/history")}
                />

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
                                active={isRouteActive(pathname, `/${cat.key}`)}
                                collapsed={isCollapsed}
                                onClick={() => router.push(`/${cat.key}`)}
                            />
                        ))}
                    </div>
                ))}
            </nav>

            <div className="sidebar-footer">
                <button
                    type="button"
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
