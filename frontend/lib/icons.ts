// frontend/lib/icons.ts
// Shared icon registry — maps manifest icon string keys to Lucide components.
// Used by Sidebar.tsx and the dashboard page.tsx.
import {
    BarChart3,
    Building2,
    Clock,
    Coins,
    Columns,
    Compass,
    Crosshair,
    Download,
    FileText,
    Flag,
    Globe2,
    Grid3X3,
    Handshake,
    Home,
    IdCard,
    LayoutGrid,
    MapPin,
    Plane,
    Rocket,
    Shield,
    Swords,
    Target,
    TrendingDown,
    User,
    Users,
    type LucideIcon,
} from "lucide-react";

export const ICON_MAP: Record<string, LucideIcon> = {
    stadium:       Building2,
    handshake:     Handshake,
    "bar-chart":   BarChart3,
    globe:         Globe2,
    user:          User,
    swords:        Swords,
    target:        Target,
    rocket:        Rocket,
    home:          Home,
    download:      Download,
    coin:          Coins,
    "map-marker":  MapPin,
    shield:        Shield,
    clock:         Clock,
    flag:          Flag,
    compass:       Compass,
    plane:         Plane,
    "trending-down": TrendingDown,
    "id-card":     IdCard,
    users:         Users,
    columns:       Columns,
    grid:          Grid3X3,
    crosshair:     Crosshair,
    "file-text":   FileText,
    default:       LayoutGrid,
};

export function resolveIcon(iconKey: string, fallback: LucideIcon = LayoutGrid): LucideIcon {
    return ICON_MAP[iconKey] ?? fallback;
}
