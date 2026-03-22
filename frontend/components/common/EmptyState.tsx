"use client";

import { InboxIcon } from "lucide-react";

interface EmptyStateProps {
    message: string;
    title?: string;
    actionLabel?: string;
}

export default function EmptyState({ title, message }: EmptyStateProps) {
    return (
        <div className="empty-state" role="status" aria-live="polite">
            <InboxIcon size={28} className="empty-state-icon" aria-hidden="true" />
            {title && <p className="empty-state-title">{title}</p>}
            <p className="empty-state-text">{message}</p>
        </div>
    );
}
