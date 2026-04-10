"""Route helper utilities for API validation and engine resolution."""

from __future__ import annotations

from typing import List, TypedDict, cast

from fastapi import HTTPException

from api.context_builder import AnalyzerProtocol
from api.engine_pool import get_active_formats, get_analyzer, is_format_loaded
from config.format_registry import get_format_engines, get_format_manifest


class ManifestFunction(TypedDict, total=False):
    key: str
    engine_class: str
    engine_method: str
    output_type: str
    required_context: List[str]


class RequestValidator:
    @staticmethod
    def validate_format(format_key: str) -> None:
        """Raises 404 if format is not loaded."""
        if not is_format_loaded(format_key):
            active = get_active_formats()
            raise HTTPException(
                status_code=404,
                detail=f"Format '{format_key}' not available. Loaded: {list(active.keys())}",
            )

    @staticmethod
    def get_analyzer_or_404(format_key: str) -> AnalyzerProtocol:
        """Returns the CricketAnalyzer for the format, or raises 404."""
        RequestValidator.validate_format(format_key)
        return cast(AnalyzerProtocol, get_analyzer(format_key))

    @staticmethod
    def find_function_in_manifest(
        analyzer: AnalyzerProtocol,
        function_key: str,
    ) -> ManifestFunction:
        """Finds a function definition in the manifest by key."""
        format_key = cast(str, getattr(analyzer, "format_type", ""))
        try:
            manifest = get_format_manifest(format_key)
        except (ValueError, ImportError) as exc:
            raise HTTPException(status_code=404, detail=f"No manifest for '{format_key}': {exc}")

        for category in manifest.get("categories", []):
            if not isinstance(category, dict):
                continue
            for fn in category.get("functions", []):
                if isinstance(fn, dict) and fn.get("key") == function_key:
                    return cast(ManifestFunction, fn)

        all_keys = [
            fn["key"]
            for cat in manifest.get("categories", [])
            for fn in cat.get("functions", [])
        ]
        raise HTTPException(
            status_code=404,
            detail=(
                f"Function '{function_key}' not found in {format_key} manifest. "
                f"Available: {all_keys}"
            ),
        )


class EngineResolver:
    @staticmethod
    def resolve(engine_class_name: str, analyzer: AnalyzerProtocol) -> object:
        """Resolves which engine instance to use based on engine_class from manifest."""
        engine_map = {
            "TeamEngine": "team_engine",
            "PlayerEngine": "player_engine",
            "PredictorEngine": "predictor_engine",
        }

        format_key = cast(str, getattr(analyzer, "format_type", ""))

        if engine_class_name == "MatchPackGenerator":
            engines = get_format_engines(format_key)
            generator_cls = engines.get("MatchPackGenerator")
            if generator_cls is None:
                raise HTTPException(
                    status_code=500,
                    detail=f"MatchPackGenerator not found for format '{format_key}'",
                )
            return generator_cls(analyzer)

        attr_name = engine_map.get(engine_class_name)
        if attr_name is None:
            raise HTTPException(
                status_code=500,
                detail=(
                    f"Unknown engine class: '{engine_class_name}'. "
                    f"Known: {list(engine_map.keys())}"
                ),
            )

        engine_instance = getattr(analyzer, attr_name, None)
        if engine_instance is None:
            raise HTTPException(
                status_code=500,
                detail=f"Engine '{engine_class_name}' not initialized for format '{format_key}'",
            )

        return engine_instance
