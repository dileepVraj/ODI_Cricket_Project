"""Match pack orchestration boundary."""
from __future__ import annotations

from pathlib import Path

from formats.odi.match_pack._assembler import JsonValue, MatchPackAssembler
from formats.odi.match_pack._persister import JsonObject, MatchPackPersister


class MatchPackOrchestrator:
    """Compatibility orchestrator that composes helper boundaries."""

    def __init__(self, bot, reports_dir: Path | str | None = None) -> None:
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
        match_pack = self.assembler.generate_pack(
            home,
            away,
            venue,
            home_xi,
            away_xi,
            context,
            persist=False,
        )
        if isinstance(match_pack, dict):
            match_pack = self.assembler._strip_internal_keys(match_pack)
        if persist and isinstance(match_pack, dict):
            return self.persister._save_report(match_pack, home, away)
        return match_pack

    def _strip_internal_keys(self, payload: JsonValue) -> JsonValue:
        return self.assembler._strip_internal_keys(payload)

    def _save_report(self, match_pack: JsonObject, home: str, away: str) -> str:
        return self.persister._save_report(match_pack, home, away)
