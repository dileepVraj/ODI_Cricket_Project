"use client";

import type { LiveTradeToastState } from "@/lib/cockpit/useLiveTradeToast";

interface LiveTradeToastProps {
    toast: LiveTradeToastState;
}

export default function LiveTradeToast({ toast }: LiveTradeToastProps) {
    return (
        <div
            className={`live-trade-toast live-trade-toast--${toast.kind} animate-slide-in-right`}
            role={toast.kind === "error" ? "alert" : "status"}
            aria-live="polite"
            aria-atomic="true"
        >
            {toast.message}
        </div>
    );
}
