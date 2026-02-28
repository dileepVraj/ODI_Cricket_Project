from typing import Optional
import pandas as pd
from config.shared.venues import get_venue_aliases

from core.interfaces.team_types import PlayerAnalyzerPort, PlayerVenueStatsFallbackPayload

class PlayerService:
    """
    Industry Standard Player Service.
    Handles player-specific logic, fallbacks, and data aggregation that 
    doesn't belong in the core headless engines.
    """

    @classmethod
    def build_player_venue_stats_fallback(cls, analyzer: PlayerAnalyzerPort, player_name: str, venue_id: str, years: int = 50) -> Optional[PlayerVenueStatsFallbackPayload]:
        """
        Adapter fallback for player_profile venue stats.
        Computes batting context at selected venue using the DataAccess Layer (DuckDB).
        
        NOTE: This was refactored in v5.1 to use the DAL instead of the deprecated raw_df.
        """
        if not player_name or not venue_id:
            return None

        dal = getattr(analyzer, "dal", None)
        if dal is None:
            return None

        try:
            # 1. Fetch relevant balls from DAL (v5.1 optimization)
            # We fetch all balls for this player first, then filter by venue and years.
            # This is more efficient than loading 1.3M rows.
            df = dal.get_balls(players=[player_name])
            if df.empty:
                return None

            # 2. Filter by Venue
            aliases = get_venue_aliases(venue_id)
            alias_set = {str(v).lower().strip() for v in aliases}
            venue_mask = df["venue"].astype(str).str.lower().str.strip().isin(alias_set)
            
            # 3. Filter by Player (should already be mostly filtered by DAL, but ensure striker)
            player_mask = df["striker"].astype(str) == player_name
            
            filtered = df[venue_mask & player_mask].copy()
            if filtered.empty:
                return None

            # 4. Filter by Years
            if "start_date" in filtered.columns:
                filtered["start_date"] = pd.to_datetime(filtered["start_date"], errors="coerce")
                ref_date = filtered["start_date"].max()
                if pd.notna(ref_date) and years and years > 0:
                    cutoff = ref_date - pd.DateOffset(years=years)
                    filtered = filtered[filtered["start_date"] >= cutoff].copy()
                    if filtered.empty:
                        return None

            # 5. Calculate Stats
            runs_col = "runs_off_bat"
            if runs_col not in filtered.columns:
                return None

            balls_col = "is_legal_ball"
            if balls_col in filtered.columns:
                balls = int(filtered[balls_col].fillna(0).astype(int).sum())
            else:
                balls = int(len(filtered))

            innings_keys = ["match_id", "innings"]
            available_keys = [k for k in innings_keys if k in filtered.columns]
            
            if available_keys:
                inning_runs = filtered.groupby(available_keys)[runs_col].sum()
                innings = int(len(inning_runs))
                highest = int(inning_runs.max()) if not inning_runs.empty else 0
                centuries = int((inning_runs >= 100).sum())
                fifties = int(((inning_runs >= 50) & (inning_runs < 100)).sum())
            else:
                innings = 0
                highest = 0
                centuries = 0
                fifties = 0

            runs = int(filtered[runs_col].sum())

            if "player_dismissed" in filtered.columns and available_keys:
                out_rows = filtered[filtered["player_dismissed"].astype(str) == player_name]
                dismissals = int(len(out_rows.groupby(available_keys))) if not out_rows.empty else 0
            else:
                dismissals = 0

            average = round((runs / dismissals), 2) if dismissals > 0 else float(runs)
            strike_rate = round((runs / balls) * 100, 1) if balls > 0 else 0.0

            return {
                "batting": {
                    "innings": innings,
                    "runs": runs,
                    "average": average,
                    "strike_rate": strike_rate,
                    "highest_score": highest,
                    "centuries": centuries,
                    "fifties": fifties,
                },
                "bowling": None,
            }
        except (AttributeError, KeyError, TypeError, ValueError, RuntimeError, OSError) as e:
            import logging
            logging.getLogger("CricketAPI").warning(f"PlayerService fallback failed: {e}")
            return None
