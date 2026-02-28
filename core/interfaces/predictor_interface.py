from abc import ABC, abstractmethod
from typing import Any, Dict, List, Tuple


class IPredictorEngine(ABC):
    """
    Strict contract for format-specific prediction engines.
    """

    @abstractmethod
    def calculate_smart_projection(self, player: str, role: str, venue_pattern: str) -> Tuple[float, str]:
        """Return projected player impact and status."""
        raise NotImplementedError

    def predict_score(
        self,
        batting_team: str,
        batting_players: List[str],
        bowling_team: str,
        bowling_players: List[str],
        venue_id: str,
        years: int = 5,
    ) -> Dict[str, Any]:
        """predict_score() is pending a Phase 12 rebuild. See predictor.py for rebuild requirements."""
        raise NotImplementedError(
            "predict_score() is pending a Phase 12 rebuild. "
            "See formats/odi/predictor.py for rebuild requirements."
        )

