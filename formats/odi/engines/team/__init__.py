"""formats/odi/engines/team ??? TeamEngine domain package."""
from ._venue import TeamVenueAnalyzer
from ._h2h import TeamH2HAnalyzer
from ._form import TeamFormAnalyzer


class TeamEngine(TeamVenueAnalyzer, TeamH2HAnalyzer, TeamFormAnalyzer):
    """TeamEngine ??? composite hub. All domain logic lives in _venue, _h2h, _form."""


__all__ = ["TeamEngine"]
