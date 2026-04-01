"""
core/match_pack/transformers — re-export hub.
Import from the domain module directly for new code.
This hub exists so that existing import sites can migrate at their own pace.
"""
from __future__ import annotations

from core.match_pack.transformers.h2h_transformer import (
    transform_h2h_report,
    transform_h2h_slim,
)
from core.match_pack.transformers.player_transformer import (
    transform_player_stats,
    transform_squad_comparison,
)
from core.match_pack.transformers.team_transformer import (
    transform_dominance_matrix,
    transform_team_form,
)
from core.match_pack.transformers.venue_transformer import transform_venue_bias

__all__ = [
    "transform_h2h_slim",
    "transform_h2h_report",
    "transform_venue_bias",
    "transform_team_form",
    "transform_dominance_matrix",
    "transform_squad_comparison",
    "transform_player_stats",
]
