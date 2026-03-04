"""Startup and lifespan helpers for the FastAPI application."""
from __future__ import annotations

import logging

from api.engine_pool import get_active_formats, initialize_pool


def run_startup_initialization(logger: logging.Logger) -> None:
    """Initialize engine pool and emit startup readiness logs."""
    logger.info("=" * 60)
    logger.info("\U0001F680 CRICKET API STARTING \u2014 Initializing Engine Pool...")
    logger.info("=" * 60)
    initialize_pool()
    active = get_active_formats()
    logger.info(f"\u2705 API READY \u2014 {len(active)} format(s) loaded: {list(active.keys())}")
    logger.info("=" * 60)

