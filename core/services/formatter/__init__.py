from core.services.formatter._scenario_formatter import ScenarioFormatter
from core.services.formatter._squad_formatter import SquadStatsFormatter
from core.services.formatter._status_formatter import StatusFormatter
from core.services.formatter._tactical_formatter import TacticalFormatter
from core.services.formatter._tone_assigner import ToneAssigner


class ReportFormatter(StatusFormatter, ToneAssigner, SquadStatsFormatter, TacticalFormatter, ScenarioFormatter):
    """Hub -- MRO: ReportFormatter -> StatusFormatter -> ToneAssigner -> SquadStatsFormatter -> TacticalFormatter -> ScenarioFormatter."""

    pass


__all__ = ["ReportFormatter"]
