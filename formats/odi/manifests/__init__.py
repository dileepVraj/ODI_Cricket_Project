from typing import Any, cast

from formats.odi.manifests._config import (
    FORMAT_RULES, TACTICAL_THRESHOLDS, SPORT_CONSTANTS,
    ENGINE_DEFAULTS, PLAYER_RULES, PLAYER_CONTEXT_TYPES,
)
from formats.odi.manifests._venue import VENUE_CATEGORIES
from formats.odi.manifests._rivalry import RIVALRY_CATEGORIES
from formats.odi.manifests._team import TEAM_CATEGORIES
from formats.odi.manifests._player import PLAYER_CATEGORIES
from formats.odi.manifests._operations import OPERATIONS_CATEGORIES

MANIFEST = {
    # ── Format Identity ──────────────────────────────────────────────────
    "format_key": "odi",
    "format_label": "Men's ODI",
    "format_icon": "🏏",
    "version": "1.1",

    # ── Source Registry (TASK-046) ───────────────────────────────────────
    # Maps semantic source identifiers to API path templates.
    # Frontend resolves {format_key} and {team} at runtime.
    "source_registry": {
        "teams": {
            "path": "/api/v1/{format_key}/context/teams",
            "preload": True,
        },
        "venues": {
            "path": "/api/v1/{format_key}/context/venues",
            "preload": True,
        },
        "players": {
            "path": "/api/v1/{format_key}/context/players/{team}",
            "preload": False,
        },
        "host_countries": {
            "path": "/api/v1/{format_key}/context/host_countries",
            "preload": False,
        },
        "regions": {
            "path": "/api/v1/{format_key}/context/regions",
            "preload": False,
        },
    },

    # ── Navigation Root (TASK-046) ───────────────────────────────────────
    # Declares the default/home screen so frontend never hardcodes "dashboard".
    "navigation_root": {
        "key": "dashboard",
        "label": "Dashboard",
        "icon": "home",
    },

    # ── Context Fields ───────────────────────────────────────────────────
    # These define the global filter bar at the top of the UI.
    # Each function declares which of these it requires.
    "context_fields": {
        "venue": {
            "type": "combobox",
            "label": "🏟️ Venue",
            "required": False,
            "source": "venues",
        },
        "team_a": {
            "type": "dropdown",
            "label": "🏠 Home Team",
            "required": True,
            "source": "teams",
        },
        "team_b": {
            "type": "dropdown",
            "label": "✈️ Away Team",
            "required": True,
            "source": "teams",
        },
        "years": {
            "type": "number",
            "label": "📅 Years",
            "min": 1,
            "max": 50,
            "default": 5,
            "required": False,
        },
        "region": {
            "type": "dropdown",
            "label": "🌏 Region",
            "required": False,
            "options": ["All", "Asia", "Europe", "Oceania", "Africa", "Americas"],
        },
    },

    # ── Approved Output Types ────────────────────────────────────────────
    # Frontend renderer map. Adding a new type = adding a new React component.
    "output_types": [
        "report",            # Key-value stat cards (ReportCard)
        "table",             # Sortable data table (DataTable)
        "squad_comparison",  # Squad-vs-squad overview renderer
        "comparison_table",  # Side-by-side team comparison (ComparisonTable)
        "matrix_table",      # Opponent-per-row dominance matrix (MatrixTable)
        "form_table",        # Recent form with emoji indicators (FormTable)
        "profile_card",      # Player stat sheet (PlayerProfileCard)
        "prediction_card",   # Score projection display (PredictionCard)
        "matchup_table",     # Batter vs bowler grid (MatchupTable)
        "download_json",     # File download + preview (DownloadPanel)
        "phase_analysis",    # Venue phase breakdown (PhaseAnalysisCard)
        "venue_matchup_report", # High-fidelity dual-card matchup
        "home_fortress",
        "venue_bias_card",
    ],

    # ── Categories ───────────────────────────────────────────────────────
    # Each category becomes a sidebar item. Functions become tabs.
    "categories": [
        *VENUE_CATEGORIES,
        *RIVALRY_CATEGORIES,
        *TEAM_CATEGORIES,
        *PLAYER_CATEGORIES,
        *OPERATIONS_CATEGORIES,
    ],
}

def get_manifest_stats() -> dict[str, Any]:
    """Returns summary statistics about this manifest."""
    categories = cast(list[dict[str, Any]], MANIFEST["categories"])
    total_funcs = sum(len(cast(list[dict[str, Any]], cat["functions"])) for cat in categories)
    return {
        "format": MANIFEST["format_key"],
        "categories": len(categories),
        "functions": total_funcs,
        "output_types_used": sorted(set(
            cast(dict[str, Any], fn)["output_type"]
            for cat in categories
            for fn in cast(list[dict[str, Any]], cat["functions"])
        )),
        "engine_classes_used": sorted(set(
            cast(dict[str, Any], fn)["engine_class"]
            for cat in categories
            for fn in cast(list[dict[str, Any]], cat["functions"])
        )),
    }

__all__ = [
    "MANIFEST", "FORMAT_RULES", "TACTICAL_THRESHOLDS", "SPORT_CONSTANTS",
    "ENGINE_DEFAULTS", "PLAYER_RULES", "PLAYER_CONTEXT_TYPES",
    "get_manifest_stats",
]
