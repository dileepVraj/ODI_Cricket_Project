"""Execution post-processing -- domain-specific fixup rules extracted from execute_function."""

from __future__ import annotations

import logging
from typing import Any, cast

from api.context_builder import AnalyzerProtocol, EngineCallParams, _engine_default_int
from api.serializers import serialize_engine_output
from core.interfaces.player_types import PlayerAnalyzerPort
from core.interfaces.serialization_types import ManifestFunctionDef
from core.interfaces.team_types import AnalyzerEngineProtocol
from core.services import EnrichmentService, ParamMapperService, PlayerService, SerializationService


class ExecutionService:
    """Applies domain-specific post-processing after an engine method call."""

    def __init__(self) -> None:
        self._log = logging.getLogger(__name__)

    def map_call_params(
        self,
        fn_def: dict,
        raw_params: dict,
    ) -> EngineCallParams:
        """Map raw request params to engine call params via ParamMapperService."""
        self._log.debug("Mapping params for function: %s", fn_def.get("key"))
        return cast(
            EngineCallParams,
            ParamMapperService.map_params(
                cast(ManifestFunctionDef, fn_def),
                raw_params,
            ),
        )

    def serialize(self, result: Any) -> Any:
        """Wrap engine result in schema and serialize for API response."""
        self._log.debug("Serializing result of type: %s", type(result).__name__)
        schematized = SerializationService.wrap_as_schema(result)
        return serialize_engine_output(schematized)

    def post_process(
        self,
        engine_method_name: str,
        serialized: Any,
        call_params: dict[str, Any],
        analyzer: AnalyzerProtocol,
    ) -> Any:
        """
        Apply all domain-specific fixup rules to the engine output.

        Called once per request, after the engine result has been serialized.
        Returns the (possibly modified) serialized result.
        """
        self._log.debug("Post-processing output of: %s", engine_method_name)
        # Case 1 -- analyze_player_profile: add venue stats if missing
        if (
            engine_method_name == "analyze_player_profile"
            and isinstance(serialized, dict)
            and call_params.get("venue_id")
            and not serialized.get("venue_stats")
        ):
            fallback_venue_stats = PlayerService.build_player_venue_stats_fallback(
                analyzer=cast(PlayerAnalyzerPort, analyzer),
                player_name=str(
                    serialized.get("name") or call_params.get("player_name") or ""
                ),
                venue_id=str(call_params.get("venue_id") or ""),
                years=int(
                    call_params.get("years")
                    or _engine_default_int(analyzer, "venue_stats_fallback_years", 1)
                ),
            )
            if fallback_venue_stats:
                serialized["venue_stats"] = fallback_venue_stats

        # Case 2 -- generate_pack: normalise response shape
        if engine_method_name == "generate_pack":
            if isinstance(serialized, str):
                serialized = {"filepath": serialized, "status": "generated"}
            elif isinstance(serialized, dict):
                serialized.setdefault("status", "generated")

        # Case 3 -- all methods: attach match audit data
        serialized = EnrichmentService.enrich_with_match_audit(
            serialized,
            cast(AnalyzerEngineProtocol, analyzer),
        )

        return serialized
