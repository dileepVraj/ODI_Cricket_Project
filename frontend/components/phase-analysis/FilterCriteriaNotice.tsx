"use client";

interface FilterCriteria {
    min_first_innings_balls?: number;
    min_first_innings_overs?: number;
    keep_all_outs?: boolean;
    keep_successful_chases?: boolean;
    drop_short_no_result_only?: boolean;
}

export default function FilterCriteriaNotice({
    criteria,
}: {
    criteria: FilterCriteria;
}) {
    const overs = criteria.min_first_innings_overs ?? 45;
    const firstBalls = criteria.min_first_innings_balls ?? 270;
    const keepAllOuts = criteria.keep_all_outs !== false;
    const keepChases = criteria.keep_successful_chases !== false;
    const dropShortNoResultOnly = criteria.drop_short_no_result_only !== false;

    return (
        <div className="[background:var(--bg-elevated)] [border:1px_solid_var(--border-subtle)] [border-left:3px_solid_var(--tier-caution)] [border-radius:var(--radius-md)] [padding:10px_12px]">
            <div className="[font-size:0.72rem] [font-weight:700] [letter-spacing:0.05em] [text-transform:uppercase] [color:var(--text-secondary)] [margin-bottom:4px]">
                Filter Criteria
            </div>
            <div className="[font-size:0.82rem] [color:var(--text-muted)] [line-height:1.5]">
                {`Baseline rule: 1st innings should be >= ${overs} overs (${firstBalls} balls). `}
                {keepAllOuts ? "All-out innings are retained even below 45 overs. " : ""}
                {keepChases ? "Successful chases are retained regardless of chase score. " : ""}
                {dropShortNoResultOnly ? "Only short no-result/abandoned anomalies are excluded." : ""}
            </div>
        </div>
    );
}
