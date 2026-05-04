"""Match pack assembler — coordinates chapter builders and assembles the final pack."""
from __future__ import annotations

from datetime import datetime
from typing import Any, TypeAlias

from config.shared.venues import get_country_from_venue_id, resolve_venue_id
from core.match_pack.interpreters import MatchInterpreter

from formats.odi.config.players import BOWLER_STYLES, PLAYER_ROLES
from formats.odi.config.rankings import ODI_RANKINGS
from formats.odi.match_pack._chapter1 import ChapterOneBuilder
from formats.odi.match_pack._chapter2 import ChapterTwoBuilder
from formats.odi.match_pack._chapter3 import ChapterThreeBuilder
from formats.odi.match_pack._chapter4 import ChapterFourBuilder
from formats.odi.match_pack._formatter import MatchPackFormatter

JsonValue: TypeAlias = str | int | float | bool | None | dict[str, "JsonValue"] | list["JsonValue"]


def _make_interpreter() -> "MatchInterpreter":
    """Presentation-domain facade — keeps core.match_pack out of __init__ call sites."""
    return MatchInterpreter(
        rankings=ODI_RANKINGS,
        bowler_styles=BOWLER_STYLES,
        player_roles=PLAYER_ROLES,
        format_key="odi",
    )


class MatchPackAssembler:
    """Coordinates the four chapter builders and assembles the final match-pack dict.

    Single responsibility: given a bot and match inputs, produce a complete
    match-pack data structure.  All chapter-specific logic lives in the chapter
    builder classes.
    """

    def __init__(self, bot: Any) -> None:
        self.bot = bot
        interpreter = _make_interpreter()
        narrator = MatchPackFormatter()
        self._ch1 = ChapterOneBuilder(bot, interpreter)
        self._ch2 = ChapterTwoBuilder(bot, interpreter)
        self._ch3 = ChapterThreeBuilder(bot, interpreter, narrator)
        self._ch4 = ChapterFourBuilder(bot, interpreter, narrator)
        self._interpreter = interpreter

    def generate_pack(
        self,
        home: str,
        away: str,
        venue: str,
        home_xi: list[str],
        away_xi: list[str],
        context: dict[str, object],
    ) -> JsonValue:
        host_country = get_country_from_venue_id(resolve_venue_id(venue) or venue)
        ch1 = self._ch1.build(home, away, host_country)
        ch2 = self._ch2.build(home, away, venue, context)
        ch3 = self._ch3.build(home, away, venue, home_xi, away_xi, context, ch2)
        ch4 = self._ch4.build(home, away, venue, home_xi, away_xi, context)
        all_chapters = {
            "Chapter_1_Macro_Context": ch1,
            "Chapter_2_Battlefield": ch2,
            "Chapter_3_Tactical_Engine": ch3,
            "Chapter_4_Player_Intelligence": ch4,
        }
        executive = self._interpreter.generate_executive_summary(
            all_chapters, home, away, context
        )
        return {
            "meta": {
                "report_type": "ODI_Match_Pack",
                "version": "3.2",
                "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "home_team": home,
                "away_team": away,
                "venue": venue,
                "home_xi": home_xi,
                "away_xi": away_xi,
                "match_context": context,
            },
            "Executive_Summary": executive,
            **all_chapters,
        }

