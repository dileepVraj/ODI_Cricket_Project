"""
GLOBAL SETTINGS & CONSTANTS

This file contains TRULY GLOBAL settings that apply across all cricket formats.
Format-specific constants (like prediction baselines) belong in their
respective format config files (e.g., formats/odi/config/settings.py).
"""

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
# Kept here as DEFAULTS for backward compatibility — format configs OVERRIDE these.
# =====================================================================
VENUE_BASELINE_DEFAULT = 280       # Default venue baseline (ODI-calibrated)
STANDARD_BATTING_POTENTIAL = 300   # Denominator for Bat Strength model
MIN_BAT_AVG_CAP = 5.0             # Floor for bad batters
MAX_BAT_AVG_CAP = 60.0            # Ceiling for statistical outliers
STANDARD_BOWLING_ECONOMY = 5.5    # Denominator for Bowl Strength model
MIN_BOWLS_FILTER = 60             # Ignore bowlers with fewer than X balls
PREDICTION_MARGIN = 15            # +/- runs for prediction range

# =====================================================================
# NOTE: When adding a new format, override these in:
#   formats/{format}/config/settings.py → FORMAT_CONFIG dict
#
# Example for T20I:
#   VENUE_BASELINE_DEFAULT = 165
#   STANDARD_BATTING_POTENTIAL = 180
#   PREDICTION_MARGIN = 10
# =====================================================================