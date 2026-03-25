"use client";

import type { VenueBiasData } from "@/lib/types";

export function getVenueBiasData(data: unknown): VenueBiasData | null {
    if (typeof data !== "object" || data === null) return null;
    const rec = data as Record<string, unknown>;
    if (typeof rec.bat1_win_pct !== "number" || typeof rec.chase_win_pct !== "number") return null;
    return rec as unknown as VenueBiasData;
}
