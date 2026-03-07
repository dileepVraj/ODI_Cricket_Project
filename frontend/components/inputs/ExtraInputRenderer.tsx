"use client";

import ExtraInputCombobox from "@/components/inputs/ExtraInputCombobox";
import ExtraInputSelect from "@/components/inputs/ExtraInputSelect";
import ExtraInputText from "@/components/inputs/ExtraInputText";

interface ExtraInputFieldDefinition {
    type: string;
    label: string;
    required?: boolean;
    source?: string;
    options?: string[];
}

interface ExtraInputRendererProps {
    formatKey: string;
    extraInputs: Record<string, ExtraInputFieldDefinition>;
    contextValues: Record<string, string | number>;
    values: Record<string, string>;
    onChange: (key: string, value: string) => void;
}

function isExtraInputFieldDefinition(value: unknown): value is ExtraInputFieldDefinition {
    if (!value || typeof value !== "object") {
        return false;
    }

    const record = value as Record<string, unknown>;
    return typeof record.type === "string" && typeof record.label === "string";
}

export default function ExtraInputRenderer({
    formatKey,
    extraInputs,
    contextValues,
    values,
    onChange,
}: ExtraInputRendererProps) {
    const fields = Object.entries(extraInputs).filter(([, value]) =>
        isExtraInputFieldDefinition(value)
    );

    if (fields.length === 0) {
        return null;
    }

    return (
        <div className="[display:flex] [flex-direction:column] [gap:12px] [margin-bottom:16px]">
            {fields.map(([key, field]) => {
                if (field.type === "combobox") {
                    return (
                        <ExtraInputCombobox
                            key={key}
                            formatKey={formatKey}
                            field={field}
                            contextValues={contextValues}
                            value={values[key] ?? ""}
                            onChange={(value) => onChange(key, value)}
                        />
                    );
                }

                if (field.type === "dropdown") {
                    return (
                        <ExtraInputSelect
                            key={key}
                            formatKey={formatKey}
                            field={field}
                            value={values[key] ?? ""}
                            onChange={(value) => onChange(key, value)}
                        />
                    );
                }

                return (
                    <ExtraInputText
                        key={key}
                        field={field}
                        value={values[key] ?? ""}
                        onChange={(value) => onChange(key, value)}
                    />
                );
            })}
        </div>
    );
}
