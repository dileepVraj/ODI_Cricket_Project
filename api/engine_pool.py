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
from typing import Dict, Optional

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from config.format_registry import FORMATS, get_format_manifest

logger = logging.getLogger("CricketAPI")

# ── The Pool ─────────────────────────────────────────────────────────────
# Maps format_key → CricketAnalyzer instance
_engine_pool: Dict[str, object] = {}

# Track which formats have manifests (only these are API-ready)
_active_formats: Dict[str, dict] = {}


def initialize_pool(formats: list = None):
    """
    Initialize CricketAnalyzer instances for the specified formats.
    Only formats WITH a valid manifest are loaded.

    Args:
        formats: List of format keys to load. If None, loads all with manifests.
    """
    global _engine_pool, _active_formats

    # Lazy import to avoid circular imports at module level
    from engine import CricketAnalyzer

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
            analyzer = CricketAnalyzer(format_type=fmt_key)

            _engine_pool[fmt_key] = analyzer
            _active_formats[fmt_key] = {
                "label": FORMATS[fmt_key]["label"],
                "icon": FORMATS[fmt_key]["icon"],
                "matches": len(analyzer.match_df) if hasattr(analyzer, "match_df") else 0,
            }
            logger.info(f"   ✅ {fmt_key.upper()} ready — {_active_formats[fmt_key]['matches']} matches")

        except FileNotFoundError as e:
            logger.warning(f"   ⚠️ {fmt_key.upper()} skipped — data file not found: {e}")
        except (ImportError, AttributeError) as e:
            logger.warning(f"   ⚠️ {fmt_key.upper()} skipped — engine error: {e}")
        except Exception as e:
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
