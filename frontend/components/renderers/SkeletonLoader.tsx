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

function ReportSkeleton() {
    return (
        <div className="[display:flex] [flex-direction:column] [gap:16px]">
            <div className="[display:flex] [justify-content:center] [padding:16px]">
                <div className="skeleton [width:200px] [height:48px] [border-radius:var(--radius-lg)]" />
            </div>
            <div className="[display:flex] [gap:12px] [justify-content:center]">
                <div className="skeleton [width:45%] [height:32px] [border-radius:var(--radius-md)]" />
                <div className="skeleton [width:45%] [height:32px] [border-radius:var(--radius-md)]" />
            </div>
            <div className="[display:grid] [grid-template-columns:1fr_1fr_1fr] [gap:12px]">
                {Array.from({ length: 6 }).map((_, i) => (
                    <div key={i} className="[padding:16px] [background:var(--bg-active)] [border-radius:var(--radius-md)]">
                        <div className="skeleton [width:60%] [height:12px] [margin-bottom:8px]" />
                        <div className="skeleton [width:40%] [height:20px]" />
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
            <div className="[display:grid] [grid-template-columns:2fr_1fr_1fr_1fr_1fr] [gap:12px] [padding:12px_16px] [background:var(--bg-surface)] [border-radius:var(--radius-md)_var(--radius-md)_0_0]">
                {colWidths.map((w, i) => (
                    <div key={i} className={`skeleton ${w} [height:14px]`} />
                ))}
            </div>

            {Array.from({ length: 8 }).map((_, row) => (
                <div
                    key={row}
                    className={`[display:grid] [grid-template-columns:2fr_1fr_1fr_1fr_1fr] [gap:12px] [padding:10px_16px] ${row % 2 === 0 ? "[background:var(--bg-active)]" : "[background:transparent]"}`}
                >
                    {rowWidths.map((w, col) => (
                        <div key={col} className={`skeleton ${w} [height:12px]`} />
                    ))}
                </div>
            ))}
        </div>
    );
}

function CardSkeleton() {
    return (
        <div className="[display:flex] [flex-direction:column] [gap:16px]">
            <div className="[padding:24px] [background:var(--bg-active)] [border-radius:var(--radius-lg)] [display:flex] [flex-direction:column] [align-items:center] [gap:12px]">
                <div className="skeleton [width:120px] [height:48px] [border-radius:var(--radius-md)]" />
                <div className="skeleton [width:200px] [height:16px]" />
                <div className="skeleton [width:80%] [height:24px] [border-radius:var(--radius-lg)]" />
            </div>
            <div className="[display:grid] [grid-template-columns:1fr_1fr_1fr] [gap:12px]">
                {Array.from({ length: 3 }).map((_, i) => (
                    <div key={i} className="[padding:16px] [background:var(--bg-active)] [border-radius:var(--radius-md)]">
                        <div className="skeleton [width:50%] [height:12px] [margin-bottom:8px]" />
                        <div className="skeleton [width:70%] [height:20px]" />
                    </div>
                ))}
            </div>
        </div>
    );
}

function ProfileSkeleton() {
    return (
        <div className="[display:flex] [gap:24px] [padding:16px]">
            <div className="skeleton [width:80px] [height:80px] [border-radius:9999px]" />
            <div className="[flex:1] [display:flex] [flex-direction:column] [gap:10px]">
                <div className="skeleton [width:200px] [height:20px]" />
                <div className="[display:flex] [gap:8px]">
                    <div className="skeleton [width:80px] [height:16px] [border-radius:var(--radius-lg)]" />
                    <div className="skeleton [width:100px] [height:16px] [border-radius:var(--radius-lg)]" />
                </div>
                <div className="[display:grid] [grid-template-columns:1fr_1fr_1fr] [gap:8px] [margin-top:8px]">
                    {Array.from({ length: 6 }).map((_, i) => (
                        <div key={i} className="[padding:10px] [background:var(--bg-active)] [border-radius:6px]">
                            <div className="skeleton [width:50%] [height:10px] [margin-bottom:6px]" />
                            <div className="skeleton [width:40%] [height:16px]" />
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}
