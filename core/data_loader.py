"""
Data Source Factory (v2.0 — DuckDB Single Source of Truth)

The ONLY way to get a data source at runtime.
Returns a DataAccess (DuckDB) instance — no CSV fallback.

Note: load_csv_or_pickle() is preserved for use by the PIPELINE SCRIPTS
      (json_converter.py, refinery_script.py) that process intermediate CSVs.
      It is NOT used at runtime by engines or the analyzer.
"""

import os
from typing import Any, Dict
import pandas as pd

from core.data_access import DataAccess
from core.exceptions import DataIntegrityError


def create_data_source(format_config: Dict[str, Any]) -> DataAccess:
    """
    Factory: Returns a DataAccess (DuckDB) instance.

    Single Source of Truth — no CSV fallback.
    Crashes loud if DuckDB is not available.

    Args:
        format_config: Format config dict containing 'db_file' key.

    Returns:
        DataAccess instance connected to the DuckDB database.

    Raises:
        DataIntegrityError: If the database schema is invalid.
        FileNotFoundError: If the database file doesn't exist.
    """
    cfg = format_config or {}
    db_path = cfg.get("db_file")

    if not db_path:
        raise FileNotFoundError(
            "No 'db_file' configured in format config. "
            "Run the data pipeline first: python scripts/update_data.py"
        )

    if not os.path.exists(db_path):
        raise FileNotFoundError(
            f"Database not found at '{db_path}'. "
            f"Run the data pipeline first: python scripts/update_data.py"
        )

    # DataIntegrityError propagates naturally (Crash Early, Crash Loud)
    return DataAccess(db_path)


def load_csv_or_pickle(csv_path: str) -> pd.DataFrame:
    """
    Self-healing pickle cache. Loads from pickle if newer than CSV, else rebuilds.

    NOTE: This function is ONLY used by pipeline scripts (json_converter.py,
    refinery_script.py) for processing intermediate CSVs. It is NOT used
    at runtime by engines or the CricketAnalyzer.
    """
    pkl_path = csv_path.replace('.csv', '.pkl')
    use_cache = False

    if os.path.exists(pkl_path):
        csv_mtime = os.path.getmtime(csv_path)
        pkl_mtime = os.path.getmtime(pkl_path)
        if pkl_mtime > csv_mtime:
            use_cache = True

    if use_cache:
        print(f"FAST LOAD: {pkl_path}")
        return pd.read_pickle(pkl_path)

    print(f"SLOW LOAD: {csv_path}")
    df = pd.read_csv(csv_path, low_memory=False)
    df.columns = df.columns.str.strip().str.lower()
    if 'start_date' in df.columns:
        df['start_date'] = pd.to_datetime(df['start_date'], errors='coerce')
        df['year'] = df['start_date'].dt.year
        if 'season' not in df.columns:
            df['season'] = df['year']
        if 'match_id' in df.columns:
            df = df.sort_values(['start_date', 'match_id'])
    df.to_pickle(pkl_path)
    return df
