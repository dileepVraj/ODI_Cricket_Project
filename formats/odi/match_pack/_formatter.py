"""Match pack narrative helpers -- re-export facade for backward compatibility."""

from formats.odi.match_pack._matchup_narrative import MatchupNarrativeBuilder
from formats.odi.match_pack._phase_narrative import PhaseNarrativeBuilder
from formats.odi.match_pack._squad_narrative import SquadNarrativeBuilder


class MatchPackFormatter(SquadNarrativeBuilder, MatchupNarrativeBuilder, PhaseNarrativeBuilder):
    """Backward-compatibility composite. Prefer focused builders for new code."""
