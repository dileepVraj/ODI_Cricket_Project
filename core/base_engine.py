"""
core/base_engine.py
Shared base engine helpers and utilities.

All format-specific engines can inherit from BaseEngine
to get common safe-math and data utilities.
"""
import logging

logger = logging.getLogger("CricketAnalyzer")


class BaseEngine:
    """Base class providing shared utilities for all engine types."""

    def __init__(self, format_rules=None):
        self.rules = format_rules or {}

    @staticmethod
    def _safe_int(value, default=0):
        """Safely convert a value to int, returning default on failure."""
        try:
            return int(value)
        except (ValueError, TypeError):
            return default

    @staticmethod
    def _safe_float(value, default=0.0):
        """Safely convert a value to float, returning default on failure."""
        try:
            return float(value)
        except (ValueError, TypeError):
            return default

    @staticmethod
    def _safe_divide(numerator, denominator, default=0):
        """Safe division — never divides by zero."""
        if denominator and denominator > 0:
            return numerator / denominator
        return default

    @staticmethod
    def _get_avg_with_count(total, count):
        """Calculate average with zero-division protection."""
        return total / count if count else 0

    @staticmethod
    def _format_pct(value, decimals=1):
        """Format a value as a percentage string."""
        return f"{round(value, decimals)}%"
