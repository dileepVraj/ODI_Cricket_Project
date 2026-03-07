"use client";

interface ExtraInputFieldDefinition {
    type: string;
    label: string;
    required?: boolean;
}

interface ExtraInputTextProps {
    field: ExtraInputFieldDefinition;
    value: string;
    onChange: (value: string) => void;
}

function sanitizeLabel(label: string): string {
    return label.replace(/[^\w\s]/g, "").trim() || "value";
}

export default function ExtraInputText({
    field,
    value,
    onChange,
}: ExtraInputTextProps) {
    const label = sanitizeLabel(field.label);

    return (
        <div className="[display:flex] [flex-direction:column] [gap:6px]">
            <label className="[font-size:0.8rem] [font-weight:600] [color:var(--text-secondary)]">
                {field.label}
                {field.required ? (
                    <span className="[color:var(--tier-danger)] [margin-left:4px]">*</span>
                ) : null}
            </label>

            {field.type === "textarea" ? (
                <textarea
                    value={value}
                    onChange={(event) => onChange(event.target.value)}
                    placeholder={`Enter ${label}`}
                    rows={4}
                    className="context-input [resize:vertical]"
                />
            ) : (
                <input
                    type="text"
                    value={value}
                    onChange={(event) => onChange(event.target.value)}
                    placeholder={`Enter ${label}`}
                    className="context-input"
                />
            )}
        </div>
    );
}
