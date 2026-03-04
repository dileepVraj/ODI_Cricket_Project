"""
api/main.py — FastAPI Application (v2.0 — Manifest-Driven)

The entire API is format-aware and manifest-driven.
One generic /execute/{function_key} endpoint serves ALL engine functions
for ALL formats — no hardcoded routes per function.

Endpoints:
    GET  /health                              → API health check
    GET  /api/formats                         → Available formats
    GET  /api/{format_type}/manifest          → Format manifest (drives UI)
    GET  /api/{format_type}/context/teams     → Team list
    GET  /api/{format_type}/context/venues    → Venue list
    GET  /api/{format_type}/context/players/{team} → Player list
    GET  /api/{format_type}/context/regions   → Region list
    POST /api/{format_type}/execute/{function_key} → Execute any engine function
"""
import os
import sys
import logging
import io
from typing import Dict, List, TypedDict, cast
from contextlib import redirect_stdout
import pandas as pd
from fastapi import FastAPI, HTTPException, Path, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.routing import APIRouter

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from config.format_registry import get_format_manifest, get_format_engines
from config.settings import (
    API_DOCS_URL,
    API_HOST,
    API_LEGACY_PREFIX,
    API_PORT,
    API_REDOC_URL,
    API_V1_PREFIX,
    CORS_ORIGINS,
)
from api.engine_pool import initialize_pool, get_analyzer, get_active_formats, is_format_loaded
from api.context_builder import (
    AnalyzerProtocol,
    EngineCallParams,
    _engine_default_int,
    _inject_player_engine_context,
    _inject_team_engine_context,
)
from api.schemas import (
    ExecuteRequest, ExecuteResponse, ErrorResponse,
    ManifestResponse, TeamsResponse, VenuesResponse, PlayersResponse,
    RegionsResponse, HostCountriesResponse, HealthResponse, FormatMetadata
)
from api.serializers import serialize_engine_output
from core.services import (
    ParamMapperService, EnrichmentService, PlayerService,
    SerializationService
)


class ManifestFunction(TypedDict, total=False):
    key: str
    engine_class: str
    engine_method: str
    output_type: str
    required_context: List[str]

# ── Logging ──────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("CricketAPI")

# ── FastAPI App ──────────────────────────────────────────────────────────
app = FastAPI(
    title="Cricket Algo-Trading API",
    description=(
        "Manifest-driven REST API for cricket analysis. "
        "Serves all engine functions for all formats via a single generic endpoint."
    ),
    version="2.0.0",
    docs_url=API_DOCS_URL,
    redoc_url=API_REDOC_URL,
)

# ── CORS (for Next.js frontend at localhost:3000) ────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Lifecycle ────────────────────────────────────────────────────────────

@app.on_event("startup")
def startup_event() -> None:
    """Initialize engine pool at API startup."""
    logger.info("=" * 60)
    logger.info("🚀 CRICKET API STARTING — Initializing Engine Pool...")
    logger.info("=" * 60)
    initialize_pool()  # Auto-discovers formats with manifests
    active = get_active_formats()
    logger.info(f"✅ API READY — {len(active)} format(s) loaded: {list(active.keys())}")
    logger.info("=" * 60)


# ── Global Error Handling ────────────────────────────────────────────────

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error="HTTP_ERROR",
            detail=exc.detail,
            status_code=exc.status_code
        ).model_dump()
    )

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled Exception: %s", exc)
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="INTERNAL_SERVER_ERROR",
            detail="An internal error occurred. Check server logs for details.",
            status_code=500
        ).model_dump()
    )

# ── V1 API Router ────────────────────────────────────────────────────────
v1_router = APIRouter(prefix=API_V1_PREFIX)

# ═══════════════════════════════════════════════════════════════════════════
# HEALTH CHECK
# ═══════════════════════════════════════════════════════════════════════════

@app.get("/health", response_model=HealthResponse, tags=["System"])
def health_check() -> HealthResponse:
    """API health check — returns loaded formats and match counts."""
    active = get_active_formats()
    return {
        "status": "active" if active else "no_formats_loaded",
        "formats_loaded": list(active.keys()),
        "total_matches": {k: v["matches"] for k, v in active.items()},
    }

# ═══════════════════════════════════════════════════════════════════════════
# FORMAT DISCOVERY
# ═══════════════════════════════════════════════════════════════════════════

@v1_router.get("/formats", response_model=List[FormatMetadata], tags=["Formats"])
def list_formats() -> List[FormatMetadata]:
    """Returns metadata about all available formats for the Format Selector."""
    from config.format_registry import get_format_metadata
    return get_format_metadata()


@v1_router.get("/{format_type}/manifest", response_model=ManifestResponse, tags=["Manifest"])
def get_manifest(format_type: str = Path(..., description="Format key (e.g., 'odi')")) -> ManifestResponse:
    """
    Returns the format's complete manifest.
    The frontend uses this to build sidebar, screens, tabs, and context bar.
    """
    _validate_format(format_type)
    try:
        manifest = get_format_manifest(format_type)
        return manifest
    except (ValueError, ImportError) as e:
        raise HTTPException(status_code=404, detail=f"No manifest for format '{format_type}': {e}")


# ═══════════════════════════════════════════════════════════════════════════
# CONTEXT ENDPOINTS (Populate dropdowns/comboboxes)
# ═══════════════════════════════════════════════════════════════════════════

@v1_router.get("/{format_type}/context/teams", response_model=TeamsResponse, tags=["Context"])
def get_teams(format_type: str = Path(..., description="Format key")) -> TeamsResponse:
    """Returns all teams available in this format's dataset."""
    analyzer = _get_analyzer_or_404(format_type)

    # Extract unique teams from both batting positions
    teams = set()
    if hasattr(analyzer, "match_df") and not analyzer.match_df.empty:
        df = analyzer.match_df
        if "team_bat_1" in df.columns:
            teams.update(df["team_bat_1"].dropna().unique())
        if "team_bat_2" in df.columns:
            teams.update(df["team_bat_2"].dropna().unique())

    return TeamsResponse(
        format_key=format_type,
        teams=sorted(teams),
    )


@v1_router.get("/{format_type}/context/venues", response_model=VenuesResponse, tags=["Context"])
def get_venues(format_type: str = Path(..., description="Format key")) -> VenuesResponse:
    """Returns all venues available in this format, formatted for UI selectors."""
    analyzer = _get_analyzer_or_404(format_type)
    from config.shared.venues import VENUE_MAP

    venues_list = []
    if hasattr(analyzer, "match_df") and not analyzer.match_df.empty:
        df = analyzer.match_df
        if "venue" in df.columns:
            unique_ids = df["venue"].dropna().unique()
            for vid in unique_ids:
                label = VENUE_MAP.get(vid, vid.replace("_", " ").title())
                venues_list.append({"id": str(vid), "label": str(label)})

    return VenuesResponse(
        format_key=format_type,
        venues=sorted(venues_list, key=lambda x: x["label"]),
    )


@v1_router.get("/{format_type}/context/players/{team}", response_model=PlayersResponse, tags=["Context"])
def get_players(
    team: str = Path(..., description="Team name (or 'All')"),
    format_type: str = Path(..., description="Format key"),
) -> PlayersResponse:
    """Returns unique players from the dataset, optionally filtered by team."""
    analyzer = _get_analyzer_or_404(format_type)
    team_norm = str(team).strip()
    players = []

    if team_norm.lower() == "all":
        if hasattr(analyzer, "player_df") and not analyzer.player_df.empty:
            players = sorted(analyzer.player_df["player"].dropna().astype(str).unique().tolist())
        else:
            if hasattr(analyzer, "meta_df") and not analyzer.meta_df.empty:
                players = sorted(analyzer.meta_df["player"].dropna().astype(str).unique().tolist())
    else:
        if hasattr(analyzer, "player_engine"):
            try:
                player_engine = analyzer.player_engine
                last_xi = []
                active_squad = []
                team_matches = pd.DataFrame()
                match_balls = pd.DataFrame()

                if hasattr(player_engine, "get_last_match_xi"):
                    dal = getattr(analyzer, "dal", None)
                    if dal is not None:
                        team_matches = dal.get_matches(team_a=team_norm)
                        if not team_matches.empty and "match_id" in team_matches.columns:
                            recent_match_ids = (
                                team_matches.sort_values("start_date", ascending=False)["match_id"]
                                .astype(str)
                                .dropna()
                                .unique()
                                .tolist()[:_engine_default_int(analyzer, "recent_match_ids_limit", 1)]
                            )
                            if recent_match_ids:
                                match_balls = dal.get_balls(match_ids=recent_match_ids)
                    last_xi = player_engine.get_last_match_xi(
                        team_norm,
                        team_matches=team_matches,
                        match_balls_df=match_balls,
                    ) or []
                if hasattr(player_engine, "get_active_squad"):
                    active_squad = player_engine.get_active_squad(team_norm) or []

                if last_xi:
                    seen = set()
                    merged = []
                    for name in [*last_xi, *active_squad]:
                        key = str(name).strip()
                        if key and key not in seen:
                            seen.add(key)
                            merged.append(key)
                    players = merged
                else:
                    players = active_squad
            except (AttributeError, KeyError):
                if hasattr(analyzer, "meta_df") and not analyzer.meta_df.empty:
                    mask = analyzer.meta_df["team"] == team_norm
                    players = sorted(analyzer.meta_df[mask]["player"].unique().tolist())

    return PlayersResponse(
        format_key=format_type,
        team=team_norm,
        players=players,
    )


@v1_router.get("/{format_type}/context/regions", response_model=RegionsResponse, tags=["Context"])
def get_regions(format_type: str = Path(..., description="Format key")) -> RegionsResponse:
    """Returns available regions/continents for filtering."""
    try:
        manifest = get_format_manifest(format_type)
        region_field = manifest.get("context_fields", {}).get("region", {})
        options = region_field.get("options", ["All", "Asia", "Europe", "Oceania", "Africa", "Americas"])
    except (ValueError, ImportError):
        options = ["All", "Asia", "Europe", "Oceania", "Africa", "Americas"]

    return RegionsResponse(format_key=format_type, regions=options)


@v1_router.get("/{format_type}/context/host_countries", response_model=HostCountriesResponse, tags=["Context"])
def get_host_countries(format_type: str = Path(..., description="Format key")) -> HostCountriesResponse:
    """Returns available host countries inferred from venue_id prefixes."""
    analyzer = _get_analyzer_or_404(format_type)
    countries = []
    if hasattr(analyzer, "match_df") and not analyzer.match_df.empty:
        df = analyzer.match_df
        if "venue_id" in df.columns:
            from config.shared.venues import list_host_countries_from_venue_ids
            venue_ids = df["venue_id"].dropna().astype(str).unique().tolist()
            countries = list_host_countries_from_venue_ids(venue_ids)
    return HostCountriesResponse(format_key=format_type, countries=countries)


# ═══════════════════════════════════════════════════════════════════════════
# GENERIC EXECUTE ENDPOINT (THE CORE)
# ═══════════════════════════════════════════════════════════════════════════

@v1_router.post("/{format_type}/execute/{function_key}", response_model=ExecuteResponse, tags=["Execute"])
def execute_function(
    request: ExecuteRequest,
    format_type: str = Path(..., description="Format key (e.g., 'odi')"),
    function_key: str = Path(..., description="Function key from manifest (e.g., 'venue_bias')"),
) -> ExecuteResponse:
    """
    Execute any engine function declared in the format's manifest.
    Strictly validated by ExecuteRequest schema.
    """
    analyzer = _get_analyzer_or_404(format_type)
    fn_def = _find_function_in_manifest(format_type, function_key)

    # 1.5 Preemptive Validation: Check for missing required context
    required_fields = fn_def.get("required_context", [])
    provided_params = request.params.model_dump(exclude_none=True)
    
    missing = []
    for field in required_fields:
        val = provided_params.get(field)
        # Check for None, empty string, or "needed" (placeholder)
        if val is None or val == "" or (field == "venue" and val == "needed"):
            missing.append(field)
            
    if missing:
        raise HTTPException(
            status_code=400,
            detail=f"Required selection missing: Please provide {', '.join(missing)} before executing this analysis."
        )

    engine_class_name = fn_def["engine_class"]
    engine_method_name = fn_def["engine_method"]

    # 2. Resolve engine instance
    engine_instance = _resolve_engine(analyzer, engine_class_name, format_type)

    # 3. Resolve method
    if not hasattr(engine_instance, engine_method_name):
        raise HTTPException(
            status_code=500,
            detail=f"Method '{engine_method_name}' not found on {engine_class_name}",
        )
    method = getattr(engine_instance, engine_method_name)

    # 4. Map context params to engine method arguments
    # .model_dump(exclude_none=True) ensures we only pass explicitly provided values.
    call_params = cast(
        EngineCallParams,
        ParamMapperService.map_params(fn_def, request.params.model_dump(exclude_none=True)),
    )
    call_params = _inject_team_engine_context(
        analyzer=analyzer,
        engine_class_name=engine_class_name,
        engine_method_name=engine_method_name,
        call_params=call_params,
    )
    call_params = _inject_player_engine_context(
        analyzer=analyzer,
        engine_class_name=engine_class_name,
        engine_method_name=engine_method_name,
        call_params=call_params,
    )

    # 5. Call engine method (suppress stdout — engines print HTML for the UI)
    try:
        captured_output = io.StringIO()
        with redirect_stdout(captured_output):
            result = method(**call_params)
    except TypeError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Parameter error calling {engine_class_name}.{engine_method_name}: {e}",
        )
    except HTTPException:
        raise
    except (AttributeError, KeyError, ValueError, RuntimeError) as e:
        raise HTTPException(
            status_code=500,
            detail=f"Engine error in {engine_class_name}.{engine_method_name}: {e}",
        )

    # 6. Domain Mapping & Serialization
    # First, try to wrap domain dataclasses in Pydantic schemas for strict validation.
    schematized = SerializationService.wrap_as_schema(result)
    serialized = serialize_engine_output(schematized)

    # 6a. Squad comparison schema parity:
    # Keep Truth-Bridge nested payload contract under `Payload`.
    if engine_method_name == "compare_squads" and isinstance(serialized, dict):
        serialized = SerializationService.serialize_compare_squads_payload(serialized)

    # 6b. Player profile venue fallback:
    # Some datasets do not carry `at_venue` context in player_df, so engine returns
    # venue_stats=None even when venue_id is provided. Build venue batting stats
    # from raw ball-by-ball data in adapter layer (Rule F4).
    if (
        engine_method_name == "analyze_player_profile"
        and isinstance(serialized, dict)
        and call_params.get("venue_id")
        and not serialized.get("venue_stats")
    ):
        fallback_venue_stats = PlayerService.build_player_venue_stats_fallback(
            analyzer=analyzer,
            player_name=str(serialized.get("name") or call_params.get("player_name") or ""),
            venue_id=str(call_params.get("venue_id") or ""),
            years=int(call_params.get("years") or _engine_default_int(analyzer, "venue_stats_fallback_years", 1)),
        )
        if fallback_venue_stats:
            serialized["venue_stats"] = fallback_venue_stats

    # 6c. Special handling for generate_pack:
    #     API calls pass persist=False, so engine returns in-memory dict payload.
    #     Keep a safe fallback for legacy filepath responses without request-time file I/O.
    if engine_method_name == "generate_pack":
        if isinstance(serialized, str):
            serialized = {"filepath": serialized, "status": "generated"}
        elif isinstance(serialized, dict):
            serialized.setdefault("status", "generated")

    # 7. Enrich with Match Audit records (extract from MATCH_IDS)
    serialized = EnrichmentService.enrich_with_match_audit(serialized, analyzer)

    return ExecuteResponse(
        function_key=function_key,
        output_type=fn_def.get("output_type", "unknown"),
        data=serialized,
        metadata={
            "engine_class": engine_class_name,
            "engine_method": engine_method_name,
            "format": format_type,
        },
    )

# ── Mount V1 Router ──────────────────────────────────────────────────────
app.include_router(v1_router)

# ── Backward Compatibility Redirects ─────────────────────────────────────
@app.get(f"{API_LEGACY_PREFIX}/formats", response_model=List[FormatMetadata], tags=["Legacy"], include_in_schema=False)
def legacy_formats() -> List[FormatMetadata]:
    return list_formats()

@app.get(f"{API_LEGACY_PREFIX}/{{format_type}}/manifest", response_model=ManifestResponse, tags=["Legacy"], include_in_schema=False)
def legacy_manifest(format_type: str) -> ManifestResponse:
    return get_manifest(format_type)

@app.get(f"{API_LEGACY_PREFIX}/{{format_type}}/context/teams", response_model=TeamsResponse, tags=["Legacy"], include_in_schema=False)
def legacy_teams(format_type: str) -> TeamsResponse:
    return get_teams(format_type)

@app.get(f"{API_LEGACY_PREFIX}/{{format_type}}/context/venues", response_model=VenuesResponse, tags=["Legacy"], include_in_schema=False)
def legacy_venues(format_type: str) -> VenuesResponse:
    return get_venues(format_type)

@app.get(f"{API_LEGACY_PREFIX}/{{format_type}}/context/players/{{team}}", response_model=PlayersResponse, tags=["Legacy"], include_in_schema=False)
def legacy_players(format_type: str, team: str) -> PlayersResponse:
    return get_players(team=team, format_type=format_type)

@app.get(f"{API_LEGACY_PREFIX}/{{format_type}}/context/regions", response_model=RegionsResponse, tags=["Legacy"], include_in_schema=False)
def legacy_regions(format_type: str) -> RegionsResponse:
    return get_regions(format_type)

@app.get(f"{API_LEGACY_PREFIX}/{{format_type}}/context/host_countries", response_model=HostCountriesResponse, tags=["Legacy"], include_in_schema=False)
def legacy_host_countries(format_type: str) -> HostCountriesResponse:
    return get_host_countries(format_type)

@app.post(f"{API_LEGACY_PREFIX}/{{format_type}}/execute/{{function_key}}", response_model=ExecuteResponse, tags=["Legacy"], include_in_schema=False)
def legacy_execute(request: ExecuteRequest, format_type: str, function_key: str) -> ExecuteResponse:
    return execute_function(request=request, format_type=format_type, function_key=function_key)


# ═══════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════

def _validate_format(format_type: str) -> None:
    """Raises 404 if format is not loaded."""
    if not is_format_loaded(format_type):
        active = get_active_formats()
        raise HTTPException(
            status_code=404,
            detail=f"Format '{format_type}' not available. Loaded: {list(active.keys())}",
        )


def _get_analyzer_or_404(format_type: str) -> AnalyzerProtocol:
    """Returns the CricketAnalyzer for the format, or raises 404."""
    _validate_format(format_type)
    return cast(AnalyzerProtocol, get_analyzer(format_type))


def _find_function_in_manifest(format_type: str, function_key: str) -> ManifestFunction:
    """Finds a function definition in the manifest by key."""
    try:
        manifest = get_format_manifest(format_type)
    except (ValueError, ImportError) as e:
        raise HTTPException(status_code=404, detail=f"No manifest for '{format_type}': {e}")

    for category in manifest.get("categories", []):
        if not isinstance(category, dict):
            continue
        for fn in category.get("functions", []):
            if isinstance(fn, dict) and fn.get("key") == function_key:
                return cast(ManifestFunction, fn)

    # Not found — provide helpful error
    all_keys = [
        fn["key"]
        for cat in manifest.get("categories", [])
        for fn in cat.get("functions", [])
    ]
    raise HTTPException(
        status_code=404,
        detail=f"Function '{function_key}' not found in {format_type} manifest. "
               f"Available: {all_keys}",
    )


def _resolve_engine(analyzer: AnalyzerProtocol, engine_class_name: str, format_type: str) -> object:
    """Resolves which engine instance to use based on engine_class from manifest."""
    engine_map = {
        "TeamEngine": "team_engine",
        "PlayerEngine": "player_engine",
        "PredictorEngine": "predictor_engine",
    }

    if engine_class_name == "MatchPackGenerator":
        # MatchPackGenerator needs special initialization — it takes the facade itself
        engines = get_format_engines(format_type)
        generator_cls = engines.get("MatchPackGenerator")
        if generator_cls is None:
            raise HTTPException(
                status_code=500,
                detail=f"MatchPackGenerator not found for format '{format_type}'",
            )
        return generator_cls(analyzer)

    attr_name = engine_map.get(engine_class_name)
    if attr_name is None:
        raise HTTPException(
            status_code=500,
            detail=f"Unknown engine class: '{engine_class_name}'. Known: {list(engine_map.keys())}",
        )

    engine_instance = getattr(analyzer, attr_name, None)
    if engine_instance is None:
        raise HTTPException(
            status_code=500,
            detail=f"Engine '{engine_class_name}' not initialized for format '{format_type}'",
        )

    return engine_instance


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=API_HOST, port=API_PORT)
