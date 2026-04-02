"""core/services/squad_service — backward-compat shim. Import from squad/ directly."""
from core.services.squad import SquadService  # noqa: F401
__all__ = ["SquadService"]
