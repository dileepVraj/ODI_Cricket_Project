"""
api/serializers.py — Engine Output Serializers (v1.0)

Converts Python engine outputs (DataFrames, numpy types, dataclasses, etc.)
into JSON-serializable Python dicts/lists.

This is the ADAPTER layer — it fixes non-JSON-friendly outputs WITHOUT
modifying the engines themselves (Rule F4: Don't Touch the Engines).
"""
import json
import numpy as np
import pandas as pd
from dataclasses import asdict, is_dataclass
from typing import Any, Dict, List, Union
from pydantic import BaseModel

DEFAULT_MAX_RECORD_ROWS = 500


def serialize_dataframe_records(
    data: pd.DataFrame,
    *,
    max_rows: int = DEFAULT_MAX_RECORD_ROWS,
    as_json_string: bool = False,
) -> Union[List[Dict[str, Any]], str]:
    """
    Serialize DataFrame records using a bounded, vectorized path.
    """
    if max_rows <= 0:
        raise ValueError("max_rows must be a positive integer.")

    if data is None or data.empty:
        return "[]" if as_json_string else []

    bounded = data.head(int(max_rows))
    payload = bounded.to_json(orient="records", date_format="iso")
    if as_json_string:
        return payload
    return json.loads(payload)

def serialize_engine_output(data: Any) -> Any:
    """
    Recursively serializes engine output to JSON-safe Python types.
    Handles DataFrames, Series, NumPy types, Dataclasses, and Pydantic models.
    """
    # None / NaN / Inf check
    if data is None:
        return None
    
    # Handle Numeric edge cases
    if isinstance(data, (float, np.floating)):
        if np.isnan(data) or np.isinf(data):
            return None
        return float(data)
    
    if isinstance(data, (int, np.integer)):
        return int(data)

    # pandas DataFrame → list of dicts
    if isinstance(data, pd.DataFrame):
        return serialize_dataframe_records(data, max_rows=DEFAULT_MAX_RECORD_ROWS, as_json_string=False)

    # pandas Series → dict
    if isinstance(data, pd.Series):
        return {str(k): serialize_engine_output(v) for k, v in data.to_dict().items()}

    # numpy ndarray → list
    if isinstance(data, np.ndarray):
        return serialize_engine_output(data.tolist())
    
    # numpy bool → bool
    if isinstance(data, np.bool_):
        return bool(data)

    # Pydantic models → dict
    if isinstance(data, BaseModel):
        return serialize_engine_output(data.model_dump())

    # dataclasses → dict (recursive)
    if is_dataclass(data) and not isinstance(data, type):
        return serialize_engine_output(asdict(data))

    # dict → recursively serialize values
    if isinstance(data, dict):
        serialized_dict = {str(k): serialize_engine_output(v) for k, v in data.items()}
        if {"wins", "defended", "chased", "bat1", "chase"}.issubset(serialized_dict):
            bat1 = serialized_dict.get("bat1")
            chase = serialized_dict.get("chase")
            if isinstance(bat1, dict):
                if bat1.get("high") is not None:
                    bat1["high"] = str(bat1["high"])
                if bat1.get("low") is not None:
                    bat1["low"] = str(bat1["low"])
            if isinstance(chase, dict) and chase.get("high") is not None:
                chase["high"] = str(chase["high"])
        return serialized_dict

    # list/tuple → recursively serialize elements
    if isinstance(data, (list, tuple)):
        return list(map(serialize_engine_output, data))

    # Timestamps
    if isinstance(data, pd.Timestamp):
        return data.isoformat()

    # Native types (str, bool) — pass through
    if isinstance(data, (str, bool)):
        return data

    # Fallback: convert to string
    return str(data)
