/**
 * components/renderers/SkeletonLoader.tsx — Loading Skeletons
 * 
 * Provides shimmer-effect skeleton loaders that approximate the shape
 * of each renderer type. Used while waiting for API responses.
 */
"use client";

interface SkeletonLoaderProps {
    outputType: string;
}

export default function SkeletonLoader({ outputType }: SkeletonLoaderProps) {
    switch (outputType) {
        case "report":
            return <ReportSkeleton />;
        case "comparison_table":
        case "table":
        case "matrix_table":
        case "form_table":
        case "matchup_table":
            return <TableSkeleton />;
        case "prediction_card":
            return <CardSkeleton />;
        case "profile_card":
            return <ProfileSkeleton />;
        case "download_json":
            return <CardSkeleton />;
        default:
            return <TableSkeleton />;
    }
}

// ═══════════════════════════════════════════════════════════════════════════
// SKELETON COMPONENTS
// ═══════════════════════════════════════════════════════════════════════════

function ShimmerBar({
    width = "100%",
    height = "14px",
    radius = "4px",
    style = {},
}: {
    width?: string;
    height?: string;
    radius?: string;
    style?: React.CSSProperties;
}) {
    return (
        <div
            style={{
                width,
                height,
                borderRadius: radius,
                background: "linear-gradient(90deg, var(--bg-active) 25%, var(--border) 50%, var(--bg-active) 75%)",
                backgroundSize: "200% 100%",
                animation: "shimmer 1.5s infinite ease-in-out",
                ...style,
            }}
        />
    );
}

function ReportSkeleton() {
    return (
        <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
            {/* Hero badge */}
            <div style={{ display: "flex", justifyContent: "center", padding: "16px" }}>
                <ShimmerBar width="200px" height="48px" radius="12px" />
            </div>
            {/* Dual bar */}
            <div style={{ display: "flex", gap: "12px", justifyContent: "center" }}>
                <ShimmerBar width="45%" height="32px" radius="8px" />
                <ShimmerBar width="45%" height="32px" radius="8px" />
            </div>
            {/* Stat grid */}
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: "12px" }}>
                {Array.from({ length: 6 }).map((_, i) => (
                    <div key={i} style={{ padding: "16px", background: "var(--bg-active)", borderRadius: "8px" }}>
                        <ShimmerBar width="60%" height="12px" style={{ marginBottom: "8px" }} />
                        <ShimmerBar width="40%" height="20px" />
                    </div>
                ))}
            </div>
        </div>
    );
}

function TableSkeleton() {
    return (
        <div style={{ display: "flex", flexDirection: "column", gap: "2px" }}>
            {/* Header row */}
            <div
                style={{
                    display: "grid",
                    gridTemplateColumns: "2fr 1fr 1fr 1fr 1fr",
                    gap: "12px",
                    padding: "12px 16px",
                    background: "var(--bg-surface)",
                    borderRadius: "8px 8px 0 0",
                }}
            >
                {Array.from({ length: 5 }).map((_, i) => (
                    <ShimmerBar key={i} width={i === 0 ? "80%" : "60%"} height="14px" />
                ))}
            </div>
            {/* Data rows */}
            {Array.from({ length: 8 }).map((_, row) => (
                <div
                    key={row}
                    style={{
                        display: "grid",
                        gridTemplateColumns: "2fr 1fr 1fr 1fr 1fr",
                        gap: "12px",
                        padding: "10px 16px",
                        background: row % 2 === 0 ? "var(--bg-active)" : "transparent",
                    }}
                >
                    {Array.from({ length: 5 }).map((_, col) => (
                        <ShimmerBar
                            key={col}
                            width={col === 0 ? `${70 + Math.random() * 20}%` : `${40 + Math.random() * 30}%`}
                            height="12px"
                        />
                    ))}
                </div>
            ))}
        </div>
    );
}

function CardSkeleton() {
    return (
        <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
            {/* Large card */}
            <div
                style={{
                    padding: "24px",
                    background: "var(--bg-active)",
                    borderRadius: "12px",
                    display: "flex",
                    flexDirection: "column",
                    alignItems: "center",
                    gap: "12px",
                }}
            >
                <ShimmerBar width="120px" height="48px" radius="8px" />
                <ShimmerBar width="200px" height="16px" />
                <ShimmerBar width="80%" height="24px" radius="12px" />
            </div>
            {/* Breakdown cards */}
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: "12px" }}>
                {Array.from({ length: 3 }).map((_, i) => (
                    <div key={i} style={{ padding: "16px", background: "var(--bg-active)", borderRadius: "8px" }}>
                        <ShimmerBar width="50%" height="12px" style={{ marginBottom: "8px" }} />
                        <ShimmerBar width="70%" height="20px" />
                    </div>
                ))}
            </div>
        </div>
    );
}

function ProfileSkeleton() {
    return (
        <div style={{ display: "flex", gap: "24px", padding: "16px" }}>
            {/* Avatar */}
            <ShimmerBar width="80px" height="80px" radius="50%" />
            {/* Info */}
            <div style={{ flex: 1, display: "flex", flexDirection: "column", gap: "10px" }}>
                <ShimmerBar width="200px" height="20px" />
                <div style={{ display: "flex", gap: "8px" }}>
                    <ShimmerBar width="80px" height="16px" radius="12px" />
                    <ShimmerBar width="100px" height="16px" radius="12px" />
                </div>
                {/* Stats grid */}
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: "8px", marginTop: "8px" }}>
                    {Array.from({ length: 6 }).map((_, i) => (
                        <div key={i} style={{ padding: "10px", background: "var(--bg-active)", borderRadius: "6px" }}>
                            <ShimmerBar width="50%" height="10px" style={{ marginBottom: "6px" }} />
                            <ShimmerBar width="40%" height="16px" />
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}
