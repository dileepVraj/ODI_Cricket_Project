// frontend/app/loading.tsx
// Next.js App Router loading.tsx — auto-shown by framework while the dashboard
// page component suspends. Renders skeleton shapes matching the real layout.
import { SkeletonBar, SkeletonBlock } from "@/components/common/Skeleton";

export default function DashboardLoading() {
    return (
        <div className="dashboard-page" aria-busy="true" aria-label="Loading dashboard" aria-live="polite">
            {/* Header skeleton */}
            <div className="dashboard-header">
                <div className="dashboard-header-title">
                    <SkeletonBlock width="20px" height="20px" />
                    <SkeletonBar width="120px" height="20px" />
                </div>
                <SkeletonBar width="180px" height="12px" />
            </div>

            {/* 3×3 card grid skeleton */}
            <div className="dashboard-grid" aria-hidden="true">
                {Array.from({ length: 9 }).map((_, i) => (
                    <SkeletonBlock key={i} height="160px" />
                ))}
            </div>
        </div>
    );
}
