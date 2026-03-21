import { type ReactNode } from "react";

interface FilterNoticeProps {
    label?: string;
    children: ReactNode;
}

export function FilterNotice({ label = "Filter Notice", children }: FilterNoticeProps) {
    return (
        <div className="filter-notice" role="note">
            <span className="filter-notice-label">{label}</span>
            <div className="filter-notice-body">{children}</div>
        </div>
    );
}
