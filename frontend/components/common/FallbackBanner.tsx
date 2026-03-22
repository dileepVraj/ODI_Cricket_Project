"use client";

import { AlertTriangle } from "lucide-react";

interface FallbackBannerProps {
    message: string;
}

export default function FallbackBanner({ message }: FallbackBannerProps) {
    return (
        <div className="fallback-banner" role="alert">
            <AlertTriangle size={14} aria-hidden="true" />
            <span>{message}</span>
        </div>
    );
}
