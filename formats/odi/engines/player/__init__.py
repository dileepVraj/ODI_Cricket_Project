"""formats/odi/engines/player — PlayerEngine domain package.
Partial hub: _matchup.py and PlayerEngineMatchup are added in TASK-177b.
"""
from ._squad import PlayerEngineSquad
from ._profile import PlayerEngineProfile

class PlayerEngine(PlayerEngineSquad, PlayerEngineProfile):
    """Partial hub — matchup domain (PlayerEngineMatchup) added in TASK-177b."""

__all__ = ["PlayerEngine"]
