"""
core/match_pack/interpreters — re-export hub.
Import from the domain module directly for new code.
This hub exists so that existing import sites can migrate at their own pace.
"""
from __future__ import annotations

from core.match_pack.interpreters.h2h_interpreter import H2HInterpreter  # noqa: F401
from core.match_pack.interpreters.venue_interpreter import VenueInterpreter  # noqa: F401
from core.match_pack.interpreters.team_interpreter import TeamInterpreter  # noqa: F401
from core.match_pack.interpreters.player_interpreter import PlayerInterpreter  # noqa: F401
from core.match_pack.interpreters.summary_composer import MatchSummaryComposer  # noqa: F401


class MatchInterpreter(
    H2HInterpreter, VenueInterpreter, TeamInterpreter,
    PlayerInterpreter, MatchSummaryComposer
):
    """Backward-compat composite — exposes all domain methods on one object."""
    pass


__all__ = [
    "H2HInterpreter",
    "VenueInterpreter",
    "TeamInterpreter",
    "PlayerInterpreter",
    "MatchSummaryComposer",
    "MatchInterpreter",
]
