"""Match pack package boundary for ODI reports."""
from formats.odi.match_pack._assembler import MatchPackAssembler
from formats.odi.match_pack._formatter import MatchPackFormatter
from formats.odi.match_pack._orchestrator import MatchPackOrchestrator
from formats.odi.match_pack._persister import MatchPackPersister

class MatchPackGenerator(MatchPackOrchestrator):
    """Backward-compat alias for MatchPackOrchestrator. Declared as class for GATE3 visibility."""

    def generate_pack(
        self,
        home: str,
        away: str,
        venue: str,
        home_xi: list[str],
        away_xi: list[str],
        context: dict[str, object],
        persist: bool = True,
    ) -> object:
        return super().generate_pack(home, away, venue, home_xi, away_xi, context, persist=persist)


__all__ = [
    "MatchPackAssembler",
    "MatchPackFormatter",
    "MatchPackGenerator",
    "MatchPackOrchestrator",
    "MatchPackPersister",
]
