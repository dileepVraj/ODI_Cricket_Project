"use client";

import Link from "next/link";
import { ArrowRight } from "lucide-react";
import { useAppContext } from "@/lib/context";

interface QuickLinkItem {
    label: string;
    href: string;
    icon?: React.ReactNode;
}

export default function QuickLinks({ links }: { links: QuickLinkItem[] }) {
    const { activeFormat } = useAppContext();
    if (!links || links.length === 0) return null;

    const resolveHref = (href: string): string => {
        if (!href.includes(":format")) return href;
        if (!activeFormat) return href.replace("/:format", "");
        return href.replace(":format", encodeURIComponent(activeFormat));
    };

    return (
        <div className="[display:flex] [gap:8px] [flex-wrap:wrap] [margin-top:16px] [padding-top:16px] [border-top:1px_solid_var(--border-subtle)]">
            {links.map((link, i) => (
                <Link
                    key={i}
                    href={resolveHref(link.href)}
                    className="quick-link-chip [display:inline-flex] [align-items:center] [gap:6px] [padding:6px_12px] [font-size:0.75rem] [font-weight:600] [background:var(--bg-elevated)] [color:var(--accent-primary)] [border:1px_solid_var(--border-subtle)] [text-decoration:none] [transition:all_0.2s_ease] hover:[background:var(--bg-hover)] hover:[border-color:var(--accent-primary)]"
                >
                    {link.icon || <ArrowRight size={12} />}
                    {link.label}
                </Link>
            ))}
        </div>
    );
}
