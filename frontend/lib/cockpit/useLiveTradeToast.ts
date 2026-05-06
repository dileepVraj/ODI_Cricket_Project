"use client";

import { useCallback, useEffect, useRef, useState } from "react";

/** @schema none -- frontend-only UI state */
export interface LiveTradeToastState {
    kind: "success" | "error";
    message: string;
}

export function useLiveTradeToast(timeoutMs: number = 3000) {
    const [toast, setToast] = useState<LiveTradeToastState | null>(null);
    const timerRef = useRef<number | null>(null);

    const clearToast = useCallback((): void => {
        if (timerRef.current !== null) {
            window.clearTimeout(timerRef.current);
            timerRef.current = null;
        }
        setToast(null);
    }, []);

    const showToast = useCallback((nextToast: LiveTradeToastState): void => {
        if (timerRef.current !== null) {
            window.clearTimeout(timerRef.current);
            timerRef.current = null;
        }

        setToast(nextToast);
        timerRef.current = window.setTimeout(() => {
            setToast(null);
            timerRef.current = null;
        }, timeoutMs);
    }, [timeoutMs]);

    useEffect(() => {
        return () => {
            if (timerRef.current !== null) {
                window.clearTimeout(timerRef.current);
            }
        };
    }, []);

    return {
        clearToast,
        showToast,
        toast,
    };
}
