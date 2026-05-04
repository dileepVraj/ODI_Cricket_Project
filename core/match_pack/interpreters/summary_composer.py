"""
core/match_pack/interpreters.summary_composer -- re-export facade for backward compatibility.
New code should import directly from the focused interpreter modules.
"""
from __future__ import annotations

from core.match_pack.interpreters._condition_interpreter import ConditionInterpreter
from core.match_pack.interpreters._roster_interpreter import RosterInterpreter
from core.match_pack.interpreters._summary_interpreter import SummaryInterpreter


class MatchSummaryComposer(ConditionInterpreter, RosterInterpreter, SummaryInterpreter):
    """Backward-compatibility composite. Prefer focused classes for new code."""

    pass
