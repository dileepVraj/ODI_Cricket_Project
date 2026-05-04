export const baseThClass =
    "[padding:11px_14px] [border-bottom:1px_solid_var(--border-default)] [color:var(--text-muted)] [font-weight:600] [font-size:0.72rem] [letter-spacing:0.02em] [white-space:nowrap]";

export const thClass = (align: "left" | "right") =>
    `${baseThClass} ${align === "left" ? "[text-align:left]" : "[text-align:right]"}`;

export const baseTdClass =
    "[padding:11px_14px] font-numeric [color:var(--text-primary)]";

export const tdClass = (align: "left" | "right") =>
    `${baseTdClass} ${align === "left" ? "[text-align:left]" : "[text-align:right]"}`;

export function accentBarClass(accentColor: string): string {
    if (accentColor === "var(--accent-ui)") return "[background:var(--accent-ui)]";
    if (accentColor === "var(--tier-strong)") return "[background:var(--tier-strong)]";
    if (accentColor === "var(--accent-data)") return "[background:var(--accent-data)]";
    return "[background:var(--tier-strong)]";
}

export function fmtNum(val: unknown): string {
    if (val === null || val === undefined) return "-";
    const n = Number(val);
    if (Number.isNaN(n)) return String(val);
    return n.toFixed(1);
}
