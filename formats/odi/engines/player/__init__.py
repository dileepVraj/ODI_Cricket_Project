"""formats/odi/engines/player — PlayerEngine domain package."""
from ._squad import PlayerEngineSquad
from ._matchup import PlayerEngineMatchup
from ._profile import PlayerEngineProfile


class PlayerEngine(PlayerEngineSquad, PlayerEngineMatchup, PlayerEngineProfile):
    """PlayerEngine — composite hub. All logic in domain modules."""


__all__ = ["PlayerEngine"]
