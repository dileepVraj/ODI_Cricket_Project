import { SkeletonBar, SkeletonBlock } from "@/components/common/Skeleton";

// Shown by Next.js App Router during route transition to any module page.
// Matches the layout of the module page: header + tabs + content panel.

export default function ModuleLoading() {
    return (
        <div
            className="module-page"
            aria-busy="true"
            aria-live="polite"
            aria-label="Loading module"
        >
            {/* Page header skeleton */}
            <div className="page-header">
                <div className="page-header-row">
                    <SkeletonBlock width="20px" height="20px" />
                    <SkeletonBar width="160px" height="22px" />
                </div>
                <SkeletonBar width="260px" height="12px" />
            </div>

            {/* Function tabs skeleton */}
            <div className="module-tabs">
                {Array.from({ length: 3 }).map((_, i) => (
                    <SkeletonBar key={i} width="80px" height="28px" className="mr-1" />
                ))}
            </div>

            {/* Content area skeleton */}
            <SkeletonBlock height="300px" />
        </div>
    );
}
