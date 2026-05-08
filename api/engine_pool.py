"""
api/engine_pool.py — Engine Initialization Pool (v1.0)

Singleton pattern: each format's CricketAnalyzer is initialized ONCE at startup.
Not per-request (too slow — data loading takes seconds).

Thread-safe via simple module-level dict (Python's GIL handles read-only access).
Write operations (init) happen only at startup.
"""
import os
import sys
import logging
import importlib
from typing import Any, Dict, Optional

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from config.format_registry import (  # noqa: E402
    FORMATS, 
    get_format_manifest, 
    get_format_engines, 
    get_format_config
)
from core.data_loader import create_data_source  # noqa: E402

logger = logging.getLogger("CricketAPI")

# ── The Pool ─────────────────────────────────────────────────────────────
# ── The Analyzer Facade ──────────────────────────────────────────────────
class FormatAnalyzer:
    """
    Format-aware analyzer facade that satisfies AnalyzerProtocol.
    Wires together individual strategy engines with pre-loaded data.
    """
    def __init__(self, format_type: str, format_rules: dict[str, Any]):
        self.format_type = format_type
        self.format_rules = format_rules
        
        # 1. Get Registry Assets
        engines = get_format_engines(format_type)
        format_config = get_format_config(format_type)
        
        # 2. Initialize DAL (DuckDB)
        self.dal = create_data_source(format_config)
        
        # 3. Pre-load DataFrames for Engines
        self.match_df = self.dal.get_matches()
        self.phase_df = self.dal.get_phase_stats()
        self.player_df = self.dal.get_player_stats()
        self.meta_df = self.dal.get_player_metadata()
        self.squads_df = self.dal.get_squads()
        
        # 4. Instantiate Strategy Engines
        team_cls = engines.get("TeamEngine")
        player_cls = engines.get("PlayerEngine")
        predictor_cls = engines.get("PredictorEngine")
        
        if team_cls:
            self.team_engine = team_cls(
                match_df=self.match_df,
                phase_df=self.phase_df,
                dal=self.dal,
                format_rules=self.format_rules
            )
        else:
            self.team_engine = None

        if player_cls:
            self.player_engine = player_cls(
                player_df=self.player_df,
                meta_df=self.meta_df,
                squads_df=self.squads_df,
                dal=self.dal,
                format_rules=self.format_rules
            )
        else:
            self.player_engine = None

        if predictor_cls:
            self.predictor_engine = predictor_cls(
                player_df=self.player_df,
                dal=self.dal,
                format_config=format_config,
                format_rules=self.format_rules
            )
        else:
            self.predictor_engine = None

    # ── MatchPackGenerator Compatibility Proxies ──────────────────────────
    # These methods delegate to team_engine to satisfy legacy Facade calls.

    def analyze_global_h2h(self, *args, **kwargs):
        if self.team_engine:
            return self.team_engine.analyze_global_h2h(*args, **kwargs)
        return None

    def check_recent_form(self, *args, **kwargs):
        if self.team_engine:
            return self.team_engine.analyze_team_form(*args, **kwargs)
        return None

    def analyze_country_h2h(self, *args, **kwargs):
        if self.team_engine:
            return self.team_engine.analyze_country_h2h(*args, **kwargs)
        return None

    def analyze_home_dominance(self, *args, **kwargs):
        if self.team_engine:
            return self.team_engine.analyze_home_dominance(*args, **kwargs)
        return None

    def analyze_away_performance(self, *args, **kwargs):
        if self.team_engine:
            return self.team_engine.analyze_away_performance(*args, **kwargs)
        return None

    def analyze_home_fortress(self, *args, **kwargs):
        if self.team_engine:
            return self.team_engine.analyze_home_fortress(*args, **kwargs)
        return None

    def analyze_venue_matchup(self, *args, **kwargs):
        if self.team_engine:
            return self.team_engine.analyze_venue_matchup_structured(*args, **kwargs)
        return None

    def analyze_venue_bias(self, *args, **kwargs):
        if self.team_engine:
            return self.team_engine.analyze_venue_bias(*args, **kwargs)
        return None

    def analyze_venue_phases(self, *args, **kwargs):
        if self.team_engine:
            return self.team_engine.analyze_venue_phases(*args, **kwargs)
        return None


# ── The Pool ─────────────────────────────────────────────────────────────
# Maps format_key → FormatAnalyzer instance
_engine_pool: Dict[str, object] = {}

# Track which formats have manifests (only these are API-ready)
_active_formats: Dict[str, dict] = {}


def initialize_pool(formats: Optional[list[str]] = None):
    """
    Initialize CricketAnalyzer instances for the specified formats.
    Only formats WITH a valid manifest are loaded.

    Args:
        formats: List of format keys to load. If None, loads all with manifests.
    """
    global _engine_pool, _active_formats

    # Engines are initialized via FormatAnalyzer

    if formats is None:
        # Auto-detect: only load formats that have manifests
        formats = []
        for fmt_key in FORMATS:
            try:
                get_format_manifest(fmt_key)
                formats.append(fmt_key)
            except (ValueError, ImportError):
                logger.info(f"   Skipping '{fmt_key}' — no manifest found")

    logger.info(f"Initializing Engine Pool for formats: {formats}")

    for fmt_key in formats:
        try:
            logger.info(f"   Loading {fmt_key.upper()}...")
            try:
                get_format_config(fmt_key)
            except (AttributeError, ImportError):
                logger.info(f"   Skipping '{fmt_key}' - no format config found")
                continue

            format_rules: dict[str, Any] = {}
            try:
                manifest_module = importlib.import_module(f"{FORMATS[fmt_key]['module']}.manifest")
                format_rules = getattr(manifest_module, "FORMAT_RULES", {}) or {}
            except (ImportError, KeyError, AttributeError):
                format_rules = {}

            analyzer = FormatAnalyzer(
                format_type=fmt_key,
                format_rules=format_rules,
            )

            _engine_pool[fmt_key] = analyzer
            _active_formats[fmt_key] = {
                "label": FORMATS[fmt_key]["label"],
                "icon": FORMATS[fmt_key]["icon"],
                "matches": len(analyzer.match_df) if hasattr(analyzer, "match_df") else 0,
            }
            logger.info(f"   ✅ {fmt_key.upper()} ready — {len(analyzer.match_df)} matches")

        except FileNotFoundError as e:
            logger.warning(f"   ⚠️ {fmt_key.upper()} skipped — data file not found: {e}")
        except (ImportError, AttributeError) as e:
            logger.warning(f"   ⚠️ {fmt_key.upper()} skipped — engine error: {e}")
        except (KeyError, TypeError, ValueError, RuntimeError, OSError) as e:
            logger.error(f"   ❌ {fmt_key.upper()} FAILED: {e}")


def get_analyzer(format_type: str):
    """
    Returns the CricketAnalyzer instance for the given format.

    Args:
        format_type: Format key (e.g., "odi", "t20i")

    Returns:
        CricketAnalyzer instance

    Raises:
        KeyError: If the format is not loaded in the pool.
    """
    if format_type not in _engine_pool:
        available = list(_engine_pool.keys())
        raise KeyError(
            f"Format '{format_type}' not loaded. "
            f"Available formats: {available}"
        )
    return _engine_pool[format_type]


def get_active_formats() -> Dict[str, dict]:
    """Returns metadata about all loaded formats."""
    return _active_formats.copy()


def is_format_loaded(format_type: str) -> bool:
    """Check if a format is loaded and ready."""
    return format_type in _engine_pool
