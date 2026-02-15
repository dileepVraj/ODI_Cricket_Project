"""
api/serializers.py — Engine Output Serializers (v1.0)

Converts Python engine outputs (DataFrames, numpy types, dataclasses, etc.)
into JSON-serializable Python dicts/lists.

This is the ADAPTER layer — it fixes non-JSON-friendly outputs WITHOUT
modifying the engines themselves (Rule F4: Don't Touch the Engines).
"""
import numpy as np
import pandas as pd
from dataclasses import asdict, is_dataclass
from typing import Any


def serialize_engine_output(data: Any) -> Any:
    """
    Recursively serializes engine output to JSON-safe Python types.

    Handles:
        - pandas DataFrame → list of dicts
        - pandas Series → dict
        - numpy int/float → Python int/float
        - numpy ndarray → list
        - dataclasses → dict
        - nested dicts/lists → recursively serialized
        - NaN/None → None

    Args:
        data: Any engine output (dict, DataFrame, list, scalar, etc.)

    Returns:
        JSON-serializable Python object.
    """
    # None / NaN
    if data is None:
        return None

    # pandas DataFrame → list of dicts
    if isinstance(data, pd.DataFrame):
        # Convert to records, then recursively clean each row
        records = data.to_dict(orient="records")
        return [serialize_engine_output(row) for row in records]

    # pandas Series → dict
    if isinstance(data, pd.Series):
        return {str(k): serialize_engine_output(v) for k, v in data.to_dict().items()}

    # numpy scalar types → Python native
    if isinstance(data, (np.integer,)):
        return int(data)
    if isinstance(data, (np.floating,)):
        val = float(data)
        if np.isnan(val) or np.isinf(val):
            return None
        return val
    if isinstance(data, np.bool_):
        return bool(data)
    if isinstance(data, np.ndarray):
        return [serialize_engine_output(x) for x in data.tolist()]

    # Python float NaN check
    if isinstance(data, float):
        if np.isnan(data) or np.isinf(data):
            return None
        return data

    # dataclasses → dict (recursive)
    if is_dataclass(data) and not isinstance(data, type):
        return serialize_engine_output(asdict(data))

    # dict → recursively serialize values
    if isinstance(data, dict):
        return {str(k): serialize_engine_output(v) for k, v in data.items()}

    # list/tuple → recursively serialize elements
    if isinstance(data, (list, tuple)):
        return [serialize_engine_output(item) for item in data]

    # Timestamps
    if isinstance(data, pd.Timestamp):
        return data.isoformat()

    # Native types (str, int, bool) — pass through
    if isinstance(data, (str, int, bool)):
        return data

    # Fallback: convert to string
    return str(data)
