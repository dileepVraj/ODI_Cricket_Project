"""
core/match_pack/transformer.py â€” re-export shim.
Backward compat for existing import sites. Remove once all sites migrated to transformers/.
"""
from __future__ import annotations
from core.match_pack.transformers.h2h_transformer import transform_h2h_slim, transform_h2h_report
from core.match_pack.transformers.venue_transformer import transform_venue_bias
from core.match_pack.transformers.team_transformer import transform_team_form, transform_dominance_matrix
from core.match_pack.transformers.player_transformer import transform_squad_comparison, transform_player_stats

__all__ = [
    "transform_h2h_slim", "transform_h2h_report",
    "transform_venue_bias",
    "transform_team_form", "transform_dominance_matrix",
    "transform_squad_comparison", "transform_player_stats",
]
