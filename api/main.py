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
import sys
import os
import io
import logging
from contextlib import redirect_stdout
from typing import Any, Dict, List

from fastapi import FastAPI, HTTPException, Path, Query
from fastapi.middleware.cors import CORSMiddleware

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from config.format_registry import get_format_manifest, get_format_engines
from api.engine_pool import initialize_pool, get_analyzer, get_active_formats, is_format_loaded
from api.models import (
    ExecuteRequest, ExecuteResponse, HealthResponse,
    ManifestResponse, FormatInfo, ContextTeamsResponse,
    ContextVenuesResponse, ContextPlayersResponse,
)
from api.serializers import serialize_engine_output

# ── Logging ──────────────────────────────────────────────────────────────
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("CricketAPI")

# ── FastAPI App ──────────────────────────────────────────────────────────
app = FastAPI(
    title="Cricket Algo-Trading API",
    description=(
        "Manifest-driven REST API for cricket analysis. "
        "Serves all engine functions for all formats via a single generic endpoint."
    ),
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS (for Next.js frontend at localhost:3000) ────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Lifecycle ────────────────────────────────────────────────────────────

@app.on_event("startup")
def startup_event():
    """Initialize engine pool at API startup."""
    logger.info("=" * 60)
    logger.info("🚀 CRICKET API STARTING — Initializing Engine Pool...")
    logger.info("=" * 60)
    initialize_pool()  # Auto-discovers formats with manifests
    active = get_active_formats()
    logger.info(f"✅ API READY — {len(active)} format(s) loaded: {list(active.keys())}")
    logger.info("=" * 60)


# ═══════════════════════════════════════════════════════════════════════════
# HEALTH CHECK
# ═══════════════════════════════════════════════════════════════════════════

@app.get("/health", response_model=HealthResponse, tags=["System"])
def health_check():
    """API health check — returns loaded formats and match counts."""
    active = get_active_formats()
    return HealthResponse(
        status="active" if active else "no_formats_loaded",
        formats_loaded=list(active.keys()),
        total_matches={k: v["matches"] for k, v in active.items()},
    )


# ═══════════════════════════════════════════════════════════════════════════
# FORMAT DISCOVERY
# ═══════════════════════════════════════════════════════════════════════════

@app.get("/api/formats", response_model=List[FormatInfo], tags=["Formats"])
def list_formats():
    """Returns metadata about all available formats for the Format Selector."""
    from config.format_registry import get_format_metadata
    return [FormatInfo(**fmt) for fmt in get_format_metadata()]


# ═══════════════════════════════════════════════════════════════════════════
# MANIFEST ENDPOINT
# ═══════════════════════════════════════════════════════════════════════════

@app.get("/api/{format_type}/manifest", response_model=ManifestResponse, tags=["Manifest"])
def get_manifest(format_type: str = Path(..., description="Format key (e.g., 'odi')")):
    """
    Returns the format's complete manifest.
    The frontend uses this to build sidebar, screens, tabs, and context bar.
    """
    _validate_format(format_type)
    try:
        manifest = get_format_manifest(format_type)
        return ManifestResponse(**manifest)
    except (ValueError, ImportError) as e:
        raise HTTPException(status_code=404, detail=f"No manifest for format '{format_type}': {e}")


# ═══════════════════════════════════════════════════════════════════════════
# CONTEXT ENDPOINTS (Populate dropdowns/comboboxes)
# ═══════════════════════════════════════════════════════════════════════════

@app.get("/api/{format_type}/context/teams", response_model=ContextTeamsResponse, tags=["Context"])
def get_teams(format_type: str = Path(..., description="Format key")):
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

    return ContextTeamsResponse(
        format_key=format_type,
        teams=sorted(teams),
    )


@app.get("/api/{format_type}/context/venues", response_model=ContextVenuesResponse, tags=["Context"])
def get_venues(format_type: str = Path(..., description="Format key")):
    """Returns all venues available in this format's dataset."""
    analyzer = _get_analyzer_or_404(format_type)

    venues = []
    if hasattr(analyzer, "match_df") and not analyzer.match_df.empty:
        df = analyzer.match_df
        venue_col = "venue_id" if "venue_id" in df.columns else "venue"
        if venue_col in df.columns:
            unique_venues = df[venue_col].dropna().unique()
            for v in sorted(unique_venues):
                # Convert venue ID to readable label
                # e.g., "IND_MUMBAI_WANKHEDE" → "Mumbai Wankhede"
                parts = str(v).split("_")
                if len(parts) >= 2:
                    label = " ".join(p.title() for p in parts[1:])
                    venues.append({"id": str(v), "label": label})
                else:
                    venues.append({"id": str(v), "label": str(v)})

    return ContextVenuesResponse(
        format_key=format_type,
        venues=venues,
    )


@app.get("/api/{format_type}/context/players/{team}", response_model=ContextPlayersResponse, tags=["Context"])
def get_players(
    format_type: str = Path(..., description="Format key"),
    team: str = Path(..., description="Team name"),
):
    """Returns active squad players for a specific team."""
    analyzer = _get_analyzer_or_404(format_type)

    players = []
    if hasattr(analyzer, "player_engine"):
        try:
            players = analyzer.player_engine.get_active_squad(team)
        except (AttributeError, KeyError):
            # Fallback: get unique players from metadata
            if hasattr(analyzer, "meta_df") and not analyzer.meta_df.empty:
                mask = analyzer.meta_df["team"] == team
                players = sorted(analyzer.meta_df[mask]["player"].unique().tolist())

    return ContextPlayersResponse(
        format_key=format_type,
        team=team,
        players=players if isinstance(players, list) else list(players),
    )


@app.get("/api/{format_type}/context/regions", tags=["Context"])
def get_regions(format_type: str = Path(..., description="Format key")):
    """Returns available regions/continents for filtering."""
    # Regions are static for now — read from manifest if declared
    try:
        manifest = get_format_manifest(format_type)
        region_field = manifest.get("context_fields", {}).get("region", {})
        options = region_field.get("options", ["All", "Asia", "Europe", "Oceania", "Africa", "Americas"])
    except (ValueError, ImportError):
        options = ["All", "Asia", "Europe", "Oceania", "Africa", "Americas"]

    return {"format_key": format_type, "regions": options}


# ═══════════════════════════════════════════════════════════════════════════
# GENERIC EXECUTE ENDPOINT (THE CORE)
# ═══════════════════════════════════════════════════════════════════════════

@app.post("/api/{format_type}/execute/{function_key}", response_model=ExecuteResponse, tags=["Execute"])
def execute_function(
    request: ExecuteRequest,
    format_type: str = Path(..., description="Format key (e.g., 'odi')"),
    function_key: str = Path(..., description="Function key from manifest (e.g., 'venue_bias')"),
):
    """
    Execute any engine function declared in the format's manifest.

    This is the SINGLE generic endpoint that serves ALL 17+ functions
    for ALL formats. The manifest maps function_key → engine_method.

    Request body:
        {"params": {"venue": "IND_MUMBAI_WANKHEDE", "years": 5, ...}}
    """
    analyzer = _get_analyzer_or_404(format_type)

    # 1. Look up function in manifest
    fn_def = _find_function_in_manifest(format_type, function_key)

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
    call_params = _map_params(fn_def, request.params)

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
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Engine error in {engine_class_name}.{engine_method_name}: {e}",
        )

    # 6. Serialize output
    serialized = serialize_engine_output(result)

    return ExecuteResponse(
        function_key=function_key,
        output_type=fn_def.get("output_type", "unknown"),
        data=serialized,
        metadata={
            "engine_class": engine_class_name,
            "engine_method": engine_method_name,
        },
    )


# ═══════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════

def _validate_format(format_type: str):
    """Raises 404 if format is not loaded."""
    if not is_format_loaded(format_type):
        active = get_active_formats()
        raise HTTPException(
            status_code=404,
            detail=f"Format '{format_type}' not available. Loaded: {list(active.keys())}",
        )


def _get_analyzer_or_404(format_type: str):
    """Returns the CricketAnalyzer for the format, or raises 404."""
    _validate_format(format_type)
    return get_analyzer(format_type)


def _find_function_in_manifest(format_type: str, function_key: str) -> dict:
    """Finds a function definition in the manifest by key."""
    try:
        manifest = get_format_manifest(format_type)
    except (ValueError, ImportError) as e:
        raise HTTPException(status_code=404, detail=f"No manifest for '{format_type}': {e}")

    for category in manifest.get("categories", []):
        for fn in category.get("functions", []):
            if fn["key"] == function_key:
                return fn

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


def _resolve_engine(analyzer, engine_class_name: str, format_type: str):
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


def _map_params(fn_def: dict, raw_params: dict) -> dict:
    """
    Maps request parameters to engine method arguments.

    CRITICAL: First filters raw_params to ONLY include keys listed in
    the function's required_context + optional recognized keys.
    This prevents "unexpected keyword argument" errors when the frontend
    sends ALL context values but the engine method only accepts a subset.

    Context field names from the frontend → engine parameter names:
        venue   → stadium_name / stadium_id / venue_id (depends on method)
        team_a  → home_team / team_name / batting_team
        team_b  → opp_team / away_team / bowling_team
        years   → years_back / years
        region  → continent / country_name
    """
    method_name = fn_def.get("engine_method", "")
    required = set(fn_def.get("required_context", []))
    
    # Also allow optional but recognized context keys like home_xi, away_xi, etc.
    optional_keys = {"home_xi", "away_xi", "player_name", "batter", "bowlers",
                     "match_time", "toss_result", "pitch_report", "context"}
    allowed_keys = required | optional_keys
    
    # Filter: only keep params that are in allowed_keys
    params = {k: v for k, v in raw_params.items() if k in allowed_keys}

    # ── Venue Mapping ────────────────────────────────────────────────────
    if "venue" in params:
        venue_val = params.pop("venue")
        # Different engine methods use different param names for venue
        if method_name in ("analyze_venue_phases",):
            params["stadium_id"] = venue_val
        elif method_name in ("predict_score",):
            params["venue_id"] = venue_val
        elif method_name in ("compare_squads",):
            params["venue_id"] = venue_val
        elif method_name in ("generate_pack",):
            params["venue"] = venue_val
        else:
            params["stadium_name"] = venue_val

    # ── Team Mapping ─────────────────────────────────────────────────────
    if "team_a" in params:
        team_a = params.pop("team_a")
        if method_name in ("predict_score",):
            params["batting_team"] = team_a
        elif method_name in ("compare_squads",):
            params["team_a_name"] = team_a
        elif method_name in ("analyze_squad_types",):
            params["team_name"] = team_a
        elif method_name in ("generate_pack",):
            params["home"] = team_a
        elif method_name in ("analyze_away_performance",
                              "analyze_global_performance", "analyze_team_form",
                              "analyze_continent_performance"):
            params["team_name"] = team_a
        elif method_name in ("analyze_home_dominance", "analyze_venue_phases"):
            params["home_team"] = team_a
        else:
            params["home_team"] = team_a

    if "team_b" in params:
        team_b = params.pop("team_b")
        if method_name in ("predict_score",):
            params["bowling_team"] = team_b
        elif method_name in ("compare_squads", "analyze_squad_types"):
            params["team_b_name"] = team_b
        elif method_name in ("generate_pack",):
            params["away"] = team_b
        elif method_name in ("analyze_player_profile",):
            params["opposition"] = team_b
        else:
            params["opp_team"] = team_b

    # ── Years Mapping ────────────────────────────────────────────────────
    if "years" in params:
        years_val = params.pop("years")
        if method_name in ("predict_score", "analyze_player_profile",
                            "compare_squads", "analyze_squad_types",
                            "analyze_venue_phases"):
            params["years"] = int(years_val)
        elif method_name == "analyze_team_form":
            params["limit"] = int(years_val)
        else:
            params["years_back"] = int(years_val)

    # ── Region Mapping ───────────────────────────────────────────────────
    if "region" in params:
        region_val = params.pop("region")
        if method_name == "analyze_country_h2h":
            params["country_name"] = region_val
        else:
            params["continent"] = region_val

    # ── Squad Lists (for squad-dependent functions) ──────────────────────
    # These come from the SquadBuilder UI component
    if "home_xi" in params:
        home_xi = params.pop("home_xi")
        if method_name in ("predict_score",):
            params["batting_players"] = home_xi
        elif method_name in ("compare_squads",):
            params["team_a_players"] = home_xi
        elif method_name in ("generate_pack",):
            params["home_xi"] = home_xi
        elif method_name in ("analyze_squad_types",):
            params["players"] = home_xi

    if "away_xi" in params:
        away_xi = params.pop("away_xi")
        if method_name in ("predict_score",):
            params["bowling_players"] = away_xi
        elif method_name in ("compare_squads",):
            params["team_b_players"] = away_xi
        elif method_name in ("generate_pack",):
            params["away_xi"] = away_xi
        elif method_name in ("analyze_squad_types",):
            params["opposition_bowlers"] = away_xi

    # ── Matchup-specific params ──────────────────────────────────────────
    if method_name == "get_matchups":
        if "batter" not in params and "player_name" in params:
            params["batter"] = params.pop("player_name")
        if "bowlers" not in params and "away_xi" in params:
            params["bowlers"] = params.pop("away_xi")

    # ── Match Pack context ───────────────────────────────────────────────
    if method_name == "generate_pack":
        context = {}
        for key in ("match_time", "toss_result", "pitch_report"):
            if key in params:
                context[key.replace("match_", "")] = params.pop(key)
        if context:
            params["context"] = context

    return params


# ═══════════════════════════════════════════════════════════════════════════
# RUN STANDALONE
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
