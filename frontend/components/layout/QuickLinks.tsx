"use client";

import { ArrowRight } from "lucide-react";
import type { QuickLink } from "@/lib/api";

/**
 * QuickLinks — renders manifest-driven quick_links as hash-navigation chips.
 *
 * Each link navigates to a category via the URL hash (#category_key),
 * which the AppShell's hashchange listener picks up to switch views.
 */
export default function QuickLinks({ links }: { links: QuickLink[] }) {
    if (!links || links.length === 0) return null;

    const handleClick = (categoryKey: string) => {
        window.location.hash = categoryKey;
    };

    return (
        <div className="[display:flex] [gap:8px] [flex-wrap:wrap] [margin-top:16px] [padding-top:16px] [border-top:1px_solid_var(--border-subtle)]">
            {links.map((link) => (
                <button
                    key={link.category_key}
                    type="button"
                    onClick={() => handleClick(link.category_key)}
                    className="quick-link-chip [display:inline-flex] [align-items:center] [gap:6px] [padding:6px_12px] [font-size:0.75rem] [font-weight:600] [background:var(--bg-elevated)] [color:var(--accent-primary)] [border:1px_solid_var(--border-subtle)] [cursor:pointer] [font-family:inherit] [transition:all_0.2s_ease] hover:[background:var(--bg-hover)] hover:[border-color:var(--accent-primary)]"
                >
                    <ArrowRight size={12} />
                    {link.label}
                </button>
            ))}
        </div>
    );
}
