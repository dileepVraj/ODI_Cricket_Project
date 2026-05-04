"use client";

import { useCallback, useEffect, useRef, useState } from "react";

/** @schema none -- frontend-only UI state */
export interface TimedSnackbarState {
    actionLabel: string;
    kind: "success" | "error";
    message: string;
    onAction: () => void | Promise<void>;
}

export function useTimedSnackbar(timeoutMs: number = 4000) {
    const [snackbar, setSnackbar] = useState<TimedSnackbarState | null>(null);
    const timerRef = useRef<number | null>(null);

    const clearSnackbar = useCallback((): void => {
        if (timerRef.current !== null) {
            window.clearTimeout(timerRef.current);
            timerRef.current = null;
        }
        setSnackbar(null);
    }, []);

    const showSnackbar = useCallback((next: TimedSnackbarState): void => {
        clearSnackbar();
        setSnackbar(next);
        timerRef.current = window.setTimeout(() => {
            setSnackbar(null);
            timerRef.current = null;
        }, timeoutMs);
    }, [clearSnackbar, timeoutMs]);

    useEffect(() => {
        return () => {
            if (timerRef.current !== null) {
                window.clearTimeout(timerRef.current);
            }
        };
    }, []);

    return {
        clearSnackbar,
        showSnackbar,
        snackbar,
    };
}
