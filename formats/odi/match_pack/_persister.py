"""Match pack persistence helpers."""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import TypeAlias

JsonValue: TypeAlias = str | int | float | bool | None | dict[str, "JsonValue"] | list["JsonValue"]
JsonObject: TypeAlias = dict[str, JsonValue]


class MatchPackPersister:
    """Owns report file creation and JSON serialization."""

    def __init__(self, reports_dir: Path | str | None = None) -> None:
        if reports_dir is None:
            self.reports_dir = Path(__file__).resolve().parents[1] / "reports"
        else:
            self.reports_dir = Path(reports_dir)

    def _save_report(self, match_pack: JsonObject, home: str, away: str) -> str:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"MatchPack_{home}_vs_{away}_{timestamp}.json"
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        filepath = self.reports_dir / filename

        with filepath.open("w", encoding="utf-8") as file_handle:
            json.dump(match_pack, file_handle, indent=2, ensure_ascii=False, default=str)

        return str(filepath)
