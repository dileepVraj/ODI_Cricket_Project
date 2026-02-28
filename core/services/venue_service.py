from typing import List, Optional

import pandas as pd

from config.shared.venues import VENUE_MAP, get_venue_aliases, resolve_venue_id


class VenueService:
    """Pure stateless spatial resolver for venue and region filtering."""

    @staticmethod
    def resolve_stadium_id(stadium_name: str) -> str:
        """Resolve a stadium name to its canonical identifier using string matching."""
        if stadium_name in VENUE_MAP.values():
            return stadium_name
        match_key = next((key for key in VENUE_MAP if key.lower() in stadium_name.lower()), None)
        return VENUE_MAP.get(match_key, stadium_name) if match_key else stadium_name

    @staticmethod
    def _build_venue_mask(df: pd.DataFrame, venue_identifier: str) -> pd.Series:
        """
        Canonical venue matcher for in-memory DataFrames.
        Uses venue aliases across both `venue` and `venue_id`.
        """
        if df is None or df.empty:
            return pd.Series(dtype=bool)

        aliases = get_venue_aliases(venue_identifier)

        def _norm_token(value: str) -> str:
            return "".join(ch for ch in str(value).lower() if ch.isalnum())

        search_terms = {
            str(x).lower().strip()
            for x in (aliases + [venue_identifier])
            if x is not None and str(x).strip()
        }
        search_norm = {_norm_token(x) for x in search_terms if x}

        mask = pd.Series(False, index=df.index)
        if "venue" in df.columns:
            venue_lower = df["venue"].astype(str).str.lower().str.strip()
            venue_norm = venue_lower.str.replace(r"[^a-z0-9]+", "", regex=True)
            venue_base = venue_lower.str.replace(r"\([^)]*\)", "", regex=True).str.strip()
            venue_head = venue_base.str.split(",").str[0].str.strip()
            venue_base_norm = venue_base.str.replace(r"[^a-z0-9]+", "", regex=True)
            venue_head_norm = venue_head.str.replace(r"[^a-z0-9]+", "", regex=True)
            mask = (
                mask
                | venue_lower.isin(search_terms)
                | venue_norm.isin(search_norm)
                | venue_base_norm.isin(search_norm)
                | venue_head_norm.isin(search_norm)
            )

        if "venue_id" in df.columns:
            venue_id_lower = df["venue_id"].astype(str).str.lower().str.strip()
            venue_id_norm = venue_id_lower.str.replace(r"[^a-z0-9]+", "", regex=True)
            mask = mask | venue_id_lower.isin(search_terms) | venue_id_norm.isin(search_norm)

        return mask

    @staticmethod
    def _resolve_venue_output_label(df: pd.DataFrame, fallback: str) -> str:
        """Pick a stable output label (prefer canonical venue_id)."""
        if df is None or df.empty:
            return fallback
        if "venue_id" in df.columns and df["venue_id"].notna().any():
            return str(df["venue_id"].dropna().mode().iloc[0])
        if "venue" in df.columns and df["venue"].notna().any():
            return str(df["venue"].dropna().mode().iloc[0])
        return fallback

    @staticmethod
    def _get_continent_prefixes(continent: str) -> Optional[List[str]]:
        """Map UI continent labels to canonical venue-id prefixes."""
        continent_map = {
            "Asia": ["IND_", "PAK_", "SL_", "BAN_", "AFG_", "UAE_"],
            "Europe": ["ENG_", "IRE_", "SCO_", "NED_"],
            "Oceania": ["AUS_", "NZ_"],
            "Africa": ["SA_", "ZIM_"],
            "Americas": ["WI_", "USA_"],
        }
        return continent_map.get(continent)

    @staticmethod
    def _build_continent_mask(df: pd.DataFrame, continent: str) -> pd.Series:
        """
        Build a robust continent mask using:
        1) venue_id prefix when available
        2) raw venue prefix for canonical IDs stored in `venue`
        3) resolve_venue_id fallback for unmapped/null venue_id rows
        """
        if df is None or df.empty:
            return pd.Series(dtype=bool)

        if continent == "All":
            return pd.Series(True, index=df.index)

        prefixes = VenueService._get_continent_prefixes(continent)
        if not prefixes:
            return pd.Series(False, index=df.index)

        prefix_tuple = tuple(prefixes)
        mask = pd.Series(False, index=df.index)

        if "venue_id" in df.columns:
            venue_ids = df["venue_id"].fillna("").astype(str).str.upper()
            mask = mask | venue_ids.str.startswith(prefix_tuple)

        if "venue" in df.columns:
            venue_text = df["venue"].fillna("").astype(str).str.upper()
            mask = mask | venue_text.str.startswith(prefix_tuple)

            unique_venues = df["venue"].dropna().unique()
            lookup = {v: resolve_venue_id(v) for v in unique_venues}
            resolved_ids = df["venue"].map(lookup).fillna("").astype(str).str.upper()
            mask = mask | resolved_ids.str.startswith(prefix_tuple)

        return mask
