"""Shared transform helpers — string parsing, safe casts, HTML/emoji stripping."""
from __future__ import annotations

import re
from typing import Any, Dict, List


def _parse_avg_string(val: Any) -> Dict[str, int]:
    """
    Parses engine's "230 (15)" format into {avg: 230, count: 15}.
    Also handles plain numbers like 230 or "-".
    """
    if val is None or val == "-" or val == "" or val == 0:
        return {"avg": 0, "count": 0}

    val_str = str(val).strip()

    # Pattern: "230 (15)"
    match = re.match(r'^([\d.]+)\s*\((\d+)\)$', val_str)
    if match:
        return {"avg": round(float(match.group(1))), "count": int(match.group(2))}

    # Pattern: plain number "230" or "230.5"
    try:
        return {"avg": round(float(val_str)), "count": 0}
    except (ValueError, TypeError):
        return {"avg": 0, "count": 0}


def _parse_pct_string(val: Any) -> Dict[str, int]:
    """
    Parses engine's "57% (16)" format into {pct: 57, count: 16}.
    Also handles "57%" or plain "57".
    """
    if val is None or val == "-" or val == "":
        return {"pct": 0, "count": 0}

    val_str = str(val).strip()

    # Pattern: "57% (16)"
    match = re.match(r'^(\d+)%?\s*\((\d+)\)$', val_str)
    if match:
        return {"pct": int(match.group(1)), "count": int(match.group(2))}

    # Pattern: "57%" or plain "57"
    match = re.match(r'^(\d+)%?$', val_str)
    if match:
        return {"pct": int(match.group(1)), "count": 0}

    return {"pct": 0, "count": 0}


def _strip_emojis(text: Any) -> Any:
    """Removes all emoji characters and common decorators from a string."""
    if not isinstance(text, str):
        return text
    # Remove common emoji patterns used in the engine
    cleaned = re.sub(r'[🏏🥎⚖️🦁✈️🪙🌍🏰📉📅🏟️📊🔎❌\U00002705⚠️🚀💾🔧🧠⚙️🔄🚨💡🤝🌧️⚡]', '', text)
    return cleaned.strip()


def _safe_int(val: Any) -> int:
    """Converts a value to int safely, returns 0 for failures."""
    if val is None or val == "-" or val == "":
        return 0
    try:
        return int(float(val))
    except (ValueError, TypeError):
        return 0


def _safe_float(val: Any, decimals: int = 1) -> float:
    """Converts a value to float safely, returns 0.0 for failures."""
    if val is None or val == "-" or val == "":
        return 0.0
    try:
        return round(float(val), decimals)
    except (ValueError, TypeError):
        return 0.0


def _strip_html(text: Any) -> Any:
    """Removes all HTML tags from a string."""
    if not isinstance(text, str):
        return text
    return re.sub(r'<[^>]+>', '', text).strip()


def _extract_value(data_list: List[Dict[str, Any]], index: int) -> Any:
    """Safely extracts Value from a [{Metric, Value}] list by index."""
    if data_list is None or index >= len(data_list):
        return "-"
    return data_list[index].get("Value", "-")
