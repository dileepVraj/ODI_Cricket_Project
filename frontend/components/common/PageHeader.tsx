import { type LucideIcon } from "lucide-react";

interface PageHeaderProps {
    title: string;
    icon: LucideIcon;
    subtitle?: string;
}

export function PageHeader({ title, icon: Icon, subtitle }: PageHeaderProps) {
    return (
        <div className="page-header">
            <div className="page-header-row">
                <Icon className="page-header-icon" size={20} aria-hidden="true" />
                <h1 className="page-header-title">{title}</h1>
            </div>
            {subtitle && (
                <p className="page-header-subtitle">{subtitle}</p>
            )}
        </div>
    );
}
