"""
⚙️ GLOBAL SETTINGS & CONSTANTS
This file contains the mathematical constants and weights used in the algorithms.
Adjusting these values will affect Score Predictions and Smart Projections.
"""

# 🏟️ VENUE BASELINE SETTINGS
# Used in: predict_score()
VENUE_BASELINE_DEFAULT = 280  # Fallback if no venue history exists

# 🏏 BATTING STRENGTH MODEL
# Used in: predict_score()
STANDARD_BATTING_POTENTIAL = 300  # The denominator for Bat Strength (Total Avg of top order)
MIN_BAT_AVG_CAP = 5.0             # Floor for bad batters
MAX_BAT_AVG_CAP = 60.0            # Ceiling for statistical outliers

# ⚡ BOWLING PERMISSIVENESS MODEL
# Used in: predict_score()
STANDARD_BOWLING_ECONOMY = 5.5    # The denominator for Bowl Strength
MIN_BOWLS_FILTER = 60             # Ignore bowlers with fewer than X balls in career

# 🔮 SMART PROJECTION WEIGHTS (Law of Averages)
# Used in: _calculate_smart_projection()
# Formula: (Form * W1) + (Venue * W2) + (Career * W3)
WEIGHT_FORM = 0.50   # 50% Importance to Recent Form (Last 5)
WEIGHT_VENUE = 0.30  # 30% Importance to Venue History
WEIGHT_CAREER = 0.20 # 20% Importance to Career Class

# 📉 PREDICTION BUFFER
# Used to create the "Range" (e.g., 340 - 370)
PREDICTION_MARGIN = 15  # +/- 15 runs