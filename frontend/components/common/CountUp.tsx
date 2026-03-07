/**
 * KIP-FE-001: Bespoke requestAnimationFrame animation loop
 * Reason: No CSS keyframe equivalent exists for a JS-driven
 * numeric counter with easing. CSS animations cannot interpolate
 * arbitrary numeric values with custom easing functions.
 * Architect exception approved: TASK-041 2026-03-07
 * Review: revisit if Web Animations API support improves.
 */
/**
 * CountUp.tsx - Animated Number Counter
 *
 * Renders a number that counts up from 0 to the target value.
 * Used for dashboard stats to create a "live" data feel.
 *
 * Usage:
 * <CountUp end={183} duration={1.5} suffix=" runs" />
 */
"use client";

import { useEffect, useRef, useState } from "react";

interface CountUpProps {
    end: number;
    start?: number;
    duration?: number; // seconds
    decimals?: number;
    prefix?: string;
    suffix?: string;
    className?: string;
}

export default function CountUp({
    end,
    start = 0,
    duration = 1.6,
    decimals = 0,
    prefix = "",
    suffix = "",
    className = "",
}: CountUpProps) {
    const [count, setCount] = useState(start);
    const frameRef = useRef<number>(0);
    const startTimeRef = useRef<number | null>(null);

    useEffect(() => {
        startTimeRef.current = null;

        const animate = (timestamp: number) => {
            if (!startTimeRef.current) {
                startTimeRef.current = timestamp;
                setCount(start);
            }

            const progress = timestamp - startTimeRef.current;
            const easeOutQuart = (x: number): number => 1 - Math.pow(1 - x, 4);

            // Calculate progress (0 to 1)
            const relativeProgress = Math.min(progress / (duration * 1000), 1);
            const easedProgress = easeOutQuart(relativeProgress);

            const currentCount = start + (end - start) * easedProgress;
            setCount(currentCount);

            if (relativeProgress < 1) {
                frameRef.current = requestAnimationFrame(animate);
            }
        };

        frameRef.current = requestAnimationFrame(animate);

        return () => cancelAnimationFrame(frameRef.current);
    }, [end, start, duration]);

    // Format number with commas and fixed decimals
    const formatted = count.toLocaleString(undefined, {
        minimumFractionDigits: decimals,
        maximumFractionDigits: decimals,
    });

    return (
        <span
            className={`${className} font-numeric`}
            data-numeric="true"
        >
            {prefix}{formatted}{suffix}
        </span>
    );
}
