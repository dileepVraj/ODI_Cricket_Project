"""
GLOBAL SETTINGS & CONSTANTS

This module centralizes:
1) Environment-backed runtime configuration (API host/port, CORS, DB paths)
2) Global cricket constants shared across formats
"""
from __future__ import annotations

import os
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:
    def load_dotenv(dotenv_path: Path | str | None = None, override: bool = False) -> bool:
        return False


_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_ENV_PATH = _PROJECT_ROOT / ".env"
load_dotenv(dotenv_path=_ENV_PATH, override=False)


def _get_str(key: str, default: str) -> str:
    value = os.getenv(key)
    if value is None:
        return default
    stripped = value.strip()
    return stripped if stripped else default


def _get_int(key: str, default: int) -> int:
    value = os.getenv(key)
    if value is None:
        return default
    try:
        return int(value.strip())
    except ValueError:
        return default


def _get_bool(key: str, default: bool) -> bool:
    value = os.getenv(key)
    if value is None:
        return default
    normalized = value.strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False
    return default


def _get_csv_list(key: str, default_csv: str) -> list[str]:
    raw_value = _get_str(key, default_csv)
    return [item.strip() for item in raw_value.split(",") if item.strip()]


# =====================================================================
# ENVIRONMENT-BACKED RUNTIME CONFIG
# =====================================================================
API_HOST: str = _get_str("API_HOST", "127.0.0.1")
API_PORT: int = _get_int("API_PORT", 8000)
API_DEBUG: bool = _get_bool("API_DEBUG", False)
API_BASE_URL: str = _get_str("API_BASE_URL", f"http://{API_HOST}:{API_PORT}")
API_V1_PREFIX: str = _get_str("API_V1_PREFIX", "/api/v1")
API_LEGACY_PREFIX: str = _get_str("API_LEGACY_PREFIX", "/api")
API_DOCS_URL: str = _get_str("API_DOCS_URL", "/docs")
API_REDOC_URL: str = _get_str("API_REDOC_URL", "/redoc")
CORS_ORIGINS: list[str] = _get_csv_list(
    "CORS_ORIGINS",
    "http://localhost:3000,http://127.0.0.1:3000",
)
ODI_DB_PATH: str = _get_str("ODI_DB_PATH", "formats/odi/data/odi.duckdb")


# =====================================================================
# SMART PROJECTION WEIGHTS (Universal across all formats)
# Formula: (Form * W1) + (Venue * W2) + (Career * W3)
# =====================================================================
WEIGHT_FORM = 0.50    # 50% Importance to Recent Form (Last 5)
WEIGHT_VENUE = 0.30   # 30% Importance to Venue History
WEIGHT_CAREER = 0.20  # 20% Importance to Career Class

# =====================================================================
# FORMAT-SPECIFIC PREDICTION CONSTANTS
# These are imported by their respective format predictors.
# Kept here as DEFAULTS for backward compatibility - format configs OVERRIDE these.
# =====================================================================
VENUE_BASELINE_DEFAULT = 280       # Default venue baseline (ODI-calibrated)
STANDARD_BATTING_POTENTIAL = 300   # Denominator for Bat Strength model
MIN_BAT_AVG_CAP = 5.0              # Floor for bad batters
MAX_BAT_AVG_CAP = 60.0             # Ceiling for statistical outliers
STANDARD_BOWLING_ECONOMY = 5.5     # Denominator for Bowl Strength model
MIN_BOWLS_FILTER = 60              # Ignore bowlers with fewer than X balls
PREDICTION_MARGIN = 15             # +/- runs for prediction range

# =====================================================================
# NOTE: When adding a new format, override these in:
#   formats/{format}/config/settings.py -> FORMAT_CONFIG dict
# =====================================================================
