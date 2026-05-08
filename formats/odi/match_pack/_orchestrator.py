"""Match pack orchestrator — wires assembler and persister into generate_pack."""
from __future__ import annotations

from pathlib import Path

from formats.odi.match_pack._assembler import JsonValue, MatchPackAssembler
from formats.odi.match_pack._persister import MatchPackPersister


def _strip_internal_keys(payload: JsonValue) -> JsonValue:
    """Recursively remove any keys that start with '_' from a pack dict."""
    if isinstance(payload, dict):
        return {k: _strip_internal_keys(v) for k, v in payload.items() if not k.startswith("_")}
    if isinstance(payload, list):
        return [_strip_internal_keys(item) for item in payload]
    return payload


class MatchPackOrchestrator:
    """Composes MatchPackAssembler and MatchPackPersister to produce a match pack.

    Single responsibility: coordinate the two helpers — assemble the pack,
    optionally persist it, return the result.  No business logic lives here.
    """

    def __init__(self, bot: object, reports_dir: Path | str | None = None) -> None:
        self.assembler = MatchPackAssembler(bot)
        self.persister = MatchPackPersister(reports_dir=reports_dir)

    def generate_pack(
        self,
        home: str,
        away: str,
        venue: str,
        home_xi: list[str],
        away_xi: list[str],
        context: dict[str, object],
        persist: bool = True,
    ) -> JsonValue | str:
        match_pack = self.assembler.generate_pack(home, away, venue, home_xi, away_xi, context)
        if isinstance(match_pack, dict):
            match_pack = _strip_internal_keys(match_pack)
        if persist and isinstance(match_pack, dict):
            return self.persister.save_report(match_pack, home, away)
        return match_pack
