"""core/match_pack/interpreter — backward-compat shim. Import from interpreters/ directly."""
from core.match_pack.interpreters import MatchInterpreter  # noqa: F401
__all__ = ["MatchInterpreter"]
