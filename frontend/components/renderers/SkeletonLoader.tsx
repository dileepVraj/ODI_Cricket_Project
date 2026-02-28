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

function ShimmerBar({ className = "" }: { className?: string }) {
    return (
        <div
            className={`[background:linear-gradient(90deg,_var(--bg-active)_25%,_var(--border)_50%,_var(--bg-active)_75%)] [background-size:200%_100%] animate-pulse rounded ${className}`}
        />
    );
}

function ReportSkeleton() {
    return (
        <div className="[display:flex] [flex-direction:column] [gap:16px]">
            <div className="[display:flex] [justify-content:center] [padding:16px]">
                <ShimmerBar className="[width:200px] [height:48px] [border-radius:12px]" />
            </div>
            <div className="[display:flex] [gap:12px] [justify-content:center]">
                <ShimmerBar className="[width:45%] [height:32px] [border-radius:8px]" />
                <ShimmerBar className="[width:45%] [height:32px] [border-radius:8px]" />
            </div>
            <div className="[display:grid] [grid-template-columns:1fr_1fr_1fr] [gap:12px]">
                {Array.from({ length: 6 }).map((_, i) => (
                    <div key={i} className="[padding:16px] [background:var(--bg-active)] [border-radius:8px]">
                        <ShimmerBar className="[width:60%] [height:12px] [margin-bottom:8px]" />
                        <ShimmerBar className="[width:40%] [height:20px]" />
                    </div>
                ))}
            </div>
        </div>
    );
}

function TableSkeleton() {
    const colWidths = ["[width:80%]", "[width:60%]", "[width:60%]", "[width:60%]", "[width:60%]"];
    const rowWidths = ["[width:74%]", "[width:58%]", "[width:46%]", "[width:67%]", "[width:52%]"];

    return (
        <div className="[display:flex] [flex-direction:column] [gap:2px]">
            <div className="[display:grid] [grid-template-columns:2fr_1fr_1fr_1fr_1fr] [gap:12px] [padding:12px_16px] [background:var(--bg-surface)] [border-radius:8px_8px_0_0]">
                {colWidths.map((w, i) => (
                    <ShimmerBar key={i} className={`${w} [height:14px]`} />
                ))}
            </div>

            {Array.from({ length: 8 }).map((_, row) => (
                <div
                    key={row}
                    className={`[display:grid] [grid-template-columns:2fr_1fr_1fr_1fr_1fr] [gap:12px] [padding:10px_16px] ${row % 2 === 0 ? "[background:var(--bg-active)]" : "[background:transparent]"}`}
                >
                    {rowWidths.map((w, col) => (
                        <ShimmerBar key={col} className={`${w} [height:12px]`} />
                    ))}
                </div>
            ))}
        </div>
    );
}

function CardSkeleton() {
    return (
        <div className="[display:flex] [flex-direction:column] [gap:16px]">
            <div className="[padding:24px] [background:var(--bg-active)] [border-radius:12px] [display:flex] [flex-direction:column] [align-items:center] [gap:12px]">
                <ShimmerBar className="[width:120px] [height:48px] [border-radius:8px]" />
                <ShimmerBar className="[width:200px] [height:16px]" />
                <ShimmerBar className="[width:80%] [height:24px] [border-radius:12px]" />
            </div>
            <div className="[display:grid] [grid-template-columns:1fr_1fr_1fr] [gap:12px]">
                {Array.from({ length: 3 }).map((_, i) => (
                    <div key={i} className="[padding:16px] [background:var(--bg-active)] [border-radius:8px]">
                        <ShimmerBar className="[width:50%] [height:12px] [margin-bottom:8px]" />
                        <ShimmerBar className="[width:70%] [height:20px]" />
                    </div>
                ))}
            </div>
        </div>
    );
}

function ProfileSkeleton() {
    return (
        <div className="[display:flex] [gap:24px] [padding:16px]">
            <ShimmerBar className="[width:80px] [height:80px] [border-radius:9999px]" />
            <div className="[flex:1] [display:flex] [flex-direction:column] [gap:10px]">
                <ShimmerBar className="[width:200px] [height:20px]" />
                <div className="[display:flex] [gap:8px]">
                    <ShimmerBar className="[width:80px] [height:16px] [border-radius:12px]" />
                    <ShimmerBar className="[width:100px] [height:16px] [border-radius:12px]" />
                </div>
                <div className="[display:grid] [grid-template-columns:1fr_1fr_1fr] [gap:8px] [margin-top:8px]">
                    {Array.from({ length: 6 }).map((_, i) => (
                        <div key={i} className="[padding:10px] [background:var(--bg-active)] [border-radius:6px]">
                            <ShimmerBar className="[width:50%] [height:10px] [margin-bottom:6px]" />
                            <ShimmerBar className="[width:40%] [height:16px]" />
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}
