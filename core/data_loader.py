"""Shared CSV/Pickle loader (Phase 1 placeholder)."""

import os
import pandas as pd


def load_csv_or_pickle(csv_path: str) -> pd.DataFrame:
    """
    Self-healing pickle cache. Loads from pickle if newer than CSV, else rebuilds.
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


def create_data_source(format_config, fallback_csv_path=None):
    """
    Factory: Returns DataAccess (DuckDB) if available, otherwise a CSV DataFrame.
    Falls back to CSV if DuckDB is not installed or the db file is missing.
    """
    cfg = format_config or {}
    db_path = cfg.get("db_file")
    if db_path and os.path.exists(db_path):
        try:
            from core.data_access import DataAccess
            from core.exceptions import DataIntegrityError
            return DataAccess(db_path)
        except DataIntegrityError:
            raise # Crash Loud
        except Exception:
            pass # Fallback to CSV for other issues (e.g. library missing)

    csv_path = cfg.get("data_file") or fallback_csv_path
    if not csv_path:
        raise FileNotFoundError("No CSV path available for data source.")
    return load_csv_or_pickle(csv_path)
