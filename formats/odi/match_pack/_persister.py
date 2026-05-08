"""Match pack persistence — saves the assembled pack to disk as JSON."""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import TypeAlias

JsonValue: TypeAlias = str | int | float | bool | None | dict[str, "JsonValue"] | list["JsonValue"]
JsonObject: TypeAlias = dict[str, JsonValue]


class MatchPackPersister:
    """Owns report file creation and JSON serialisation.

    Single responsibility: given a match-pack dict, write it to disk and
    return the file path.  No knowledge of how the pack was built.
    """

    def __init__(self, reports_dir: Path | str | None = None) -> None:
        if reports_dir is None:
            self.reports_dir = Path(__file__).resolve().parents[1] / "reports"
        else:
            self.reports_dir = Path(reports_dir)

    def save_report(self, match_pack: JsonObject, home: str, away: str) -> str:
        """Write match_pack to a timestamped JSON file and return the file path."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"MatchPack_{home}_vs_{away}_{timestamp}.json"
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        filepath = self.reports_dir / filename

        with filepath.open("w", encoding="utf-8") as file_handle:
            json.dump(match_pack, file_handle, indent=2, ensure_ascii=False, default=str)

        return str(filepath)
