from core.services.match_filter_service import MatchStatus


class StatusFormatter:
    MATCH_STATUS_LABELS = {
        int(MatchStatus.STATUS_OK): "Included",
        int(MatchStatus.STATUS_NR_DROP): "Excluded (No Result)",
        int(MatchStatus.STATUS_SHORT_FIRST_DROP): "Excluded (Short 1st)",
        int(MatchStatus.STATUS_SHORT_SECOND_DROP): "Excluded (Short 2nd)",
        int(MatchStatus.STATUS_DROP): "Excluded",
    }

    MATCH_STATUS_ICONS = {
        int(MatchStatus.STATUS_OK): "\u2705",
        int(MatchStatus.STATUS_NR_DROP): "\u2614",
        int(MatchStatus.STATUS_SHORT_FIRST_DROP): "\u2614",
        int(MatchStatus.STATUS_SHORT_SECOND_DROP): "\u2614",
        int(MatchStatus.STATUS_DROP): "\u2614",
    }

    MATCH_STATUS_TONES = {
        int(MatchStatus.STATUS_OK): "elite",
        int(MatchStatus.STATUS_NR_DROP): "caution",
        int(MatchStatus.STATUS_SHORT_FIRST_DROP): "caution",
        int(MatchStatus.STATUS_SHORT_SECOND_DROP): "caution",
        int(MatchStatus.STATUS_DROP): "caution",
    }

    @staticmethod
    def normalize_match_status_code(value: int | float | str | None) -> int:
        if value is None:
            return int(MatchStatus.STATUS_OK)
        try:
            return int(float(value))
        except (TypeError, ValueError):
            return int(MatchStatus.STATUS_OK)

    @staticmethod
    def format_match_status(status_code: int | float | str | None) -> str:
        code = StatusFormatter.normalize_match_status_code(status_code)
        label = StatusFormatter.MATCH_STATUS_LABELS.get(code, StatusFormatter.MATCH_STATUS_LABELS[int(MatchStatus.STATUS_OK)])
        icon = StatusFormatter.MATCH_STATUS_ICONS.get(code, StatusFormatter.MATCH_STATUS_ICONS[int(MatchStatus.STATUS_OK)])
        return f"{icon} {label}"

    @staticmethod
    def match_status_tone(status_code: int | float | str | None) -> str:
        code = StatusFormatter.normalize_match_status_code(status_code)
        return StatusFormatter.MATCH_STATUS_TONES.get(code, "muted")
