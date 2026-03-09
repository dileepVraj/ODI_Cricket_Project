"use client";

export default function StatPill({ label, value }: { label: string; value: string }) {
    return (
        <div className="[text-align:center] [min-width:50px]">
            <div className="[font-size:0.6rem] [text-transform:uppercase] [color:var(--text-disabled)] [font-weight:600]">{label}</div>
            <div className="[font-size:1rem] [font-weight:700] [color:var(--text-primary)] font-numeric">{value}</div>
        </div>
    );
}
