"""Match pack assembly helpers."""
from __future__ import annotations

from typing import TypeAlias

JsonValue: TypeAlias = str | int | float | bool | None | dict[str, "JsonValue"] | list["JsonValue"]


class MatchPackAssembler:
    """Owns recursive cleanup of internal match-pack keys."""

    def _strip_internal_keys(self, payload: JsonValue) -> JsonValue:
        if isinstance(payload, dict):
            return {
                key: self._strip_internal_keys(value)
                for key, value in payload.items()
                if not key.startswith("_")
            }
        if isinstance(payload, list):
            return [self._strip_internal_keys(item) for item in payload]
        return payload
