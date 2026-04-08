"""Match pack orchestration boundary."""
from __future__ import annotations

from pathlib import Path

from formats.odi.match_pack._assembler import JsonValue, MatchPackAssembler
from formats.odi.match_pack._legacy import load_legacy_generator
from formats.odi.match_pack._persister import JsonObject, MatchPackPersister

_LegacyMatchPackGenerator = load_legacy_generator()


class MatchPackOrchestrator(_LegacyMatchPackGenerator):
    """Compatibility orchestrator that composes helper boundaries."""

    def __init__(self, bot, reports_dir: Path | str | None = None) -> None:
        super().__init__(bot)
        self.assembler = MatchPackAssembler()
        self.persister = MatchPackPersister(reports_dir=reports_dir)

    def _strip_internal_keys(self, payload: JsonValue) -> JsonValue:
        return self.assembler._strip_internal_keys(payload)

    def _save_report(self, match_pack: JsonObject, home: str, away: str) -> str:
        return self.persister._save_report(match_pack, home, away)
