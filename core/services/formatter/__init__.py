from core.services.formatter._display_formatter import DisplayFormatter
from core.services.formatter._status_formatter import StatusFormatter
from core.services.formatter._tone_assigner import ToneAssigner


class ReportFormatter(StatusFormatter, ToneAssigner, DisplayFormatter):
    """Hub -- MRO: ReportFormatter -> StatusFormatter -> ToneAssigner -> DisplayFormatter."""

    pass


__all__ = ["ReportFormatter"]
