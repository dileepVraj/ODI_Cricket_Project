"""Chapter 1 builder -- Macro Context (H2H, form, home/away dominance)."""
from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from core.match_pack.transformers.h2h_transformer import transform_h2h_slim
from core.match_pack.transformers.team_transformer import transform_dominance_matrix, transform_team_form

from formats.odi.match_pack._silent_call import silent_call

_log = logging.getLogger(__name__)


def _build_h2h_section(
    bot: Any, interpreter: Any, home: str, away: str
) -> Dict[str, Any]:
    """Fetch and interpret 4Y and 8Y global H2H records."""
    section: Dict[str, Any] = {}
    _log.debug("1.1 Global H2H (4Y)")
    raw_h2h_4y = silent_call(bot.analyze_global_h2h, home, away, 4)
    if raw_h2h_4y:
        data = transform_h2h_slim(raw_h2h_4y, home, away)
        section["global_h2h_4y"] = interpreter.interpret_h2h(data, home, away, "Last 4 Years")
    _log.debug("1.1b Global H2H (8Y Secondary)")
    raw_h2h_8y = silent_call(bot.analyze_global_h2h, home, away, 8)
    if raw_h2h_8y:
        data = transform_h2h_slim(raw_h2h_8y, home, away)
        section["global_h2h_8y"] = interpreter.interpret_h2h(data, home, away, "Last 8 Years")
    return section


def _build_form_section(
    bot: Any, interpreter: Any, home: str, away: str
) -> Dict[str, Any]:
    """Fetch and interpret recent form for both home and away teams."""
    _log.debug("1.2 Home Team Form")
    home_form: Dict[str, Any] = {}
    raw_home_global = silent_call(bot.check_recent_form, home, "All", "All", 10)
    if raw_home_global:
        data = transform_team_form(raw_home_global, home)
        home_form["global"] = interpreter.interpret_form(data, "Global")
    raw_home_vs = silent_call(bot.check_recent_form, home, away, "All", 10)
    if raw_home_vs:
        data = transform_team_form(raw_home_vs, home)
        home_form["vs_opponent"] = interpreter.interpret_form(data, f"vs {away}")

    _log.debug("1.2b Away Team Form")
    away_form: Dict[str, Any] = {}
    raw_away_global = silent_call(bot.check_recent_form, away, "All", "All", 10)
    if raw_away_global:
        data = transform_team_form(raw_away_global, away)
        away_form["global"] = interpreter.interpret_form(data, "Global")
    raw_away_vs = silent_call(bot.check_recent_form, away, home, "All", 10)
    if raw_away_vs:
        data = transform_team_form(raw_away_vs, away)
        away_form["vs_opponent"] = interpreter.interpret_form(data, f"vs {home}")
    return {"home_form": home_form, "away_form": away_form}


def _build_country_h2h_section(
    bot: Any,
    interpreter: Any,
    home: str,
    away: str,
    host_country: Optional[str],
) -> Dict[str, Any]:
    """Fetch and interpret country H2H given a pre-resolved host country."""
    if not host_country:
        return {}
    _log.debug("1.3 Country H2H (8Y)")
    raw_country = silent_call(bot.analyze_country_h2h, home, away, host_country, 8)
    if not raw_country or not isinstance(raw_country, dict):
        return {}
    summary = raw_country.get("summary", {})
    home_stats = raw_country.get("team_a", {}).get("stats", {})
    away_stats = raw_country.get("team_b", {}).get("stats", {})
    data = {
        "matches_played": summary.get("matches", 0),
        "home_wins": home_stats.get("wins", 0),
        "away_wins": away_stats.get("wins", 0),
        "no_result": summary.get("tie_nr", 0),
        "home_win_pct": summary.get("win_pct", 0),
        "home_won_batting_first": home_stats.get("defended", 0),
        "home_won_chasing": home_stats.get("chased", 0),
        "away_won_batting_first": away_stats.get("defended", 0),
        "away_won_chasing": away_stats.get("chased", 0),
    }
    return {
        "country_h2h": interpreter.interpret_h2h(data, home, away, f"In {host_country}, 8Y")
    }


def _build_dominance_sections(
    bot: Any, interpreter: Any, home: str, away: str
) -> Dict[str, Any]:
    """Fetch and interpret home dominance and away performance matrices."""
    section: Dict[str, Any] = {}
    _log.debug("1.4 Home Dominance (4Y)")
    raw_dom = silent_call(bot.analyze_home_dominance, home, 4)
    if raw_dom:
        data = transform_dominance_matrix(raw_dom, home)
        section["home_dominance"] = interpreter.interpret_dominance(data, home, "HOME")
    _log.debug("1.5 Away Performance (4Y)")
    raw_away = silent_call(bot.analyze_away_performance, away, 4)
    if raw_away:
        data = transform_dominance_matrix(raw_away, away)
        section["away_performance"] = interpreter.interpret_dominance(data, away, "AWAY")
    return section


class ChapterOneBuilder:
    """Builds Chapter 1: Macro Context -- one job, one reason to change."""

    def __init__(self, bot: Any, interpreter: Any) -> None:
        self.bot = bot
        self.interpreter = interpreter

    def build(self, home: str, away: str, host_country: Optional[str] = None) -> Dict[str, Any]:
        """Orchestrate all macro-context sections into one chapter dict."""
        return {
            "chapter_description": (
                "High-level rivalry and momentum analysis. Covers head-to-head records, "
                "recent form for both teams, and home/away performance matrices."
            ),
            **_build_h2h_section(self.bot, self.interpreter, home, away),
            **_build_form_section(self.bot, self.interpreter, home, away),
            **_build_country_h2h_section(self.bot, self.interpreter, home, away, host_country),
            **_build_dominance_sections(self.bot, self.interpreter, home, away),
        }
