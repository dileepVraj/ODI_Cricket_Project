"""api/main.py - FastAPI application."""

from __future__ import annotations

import io
import logging
import os
import sys
from contextlib import redirect_stdout
from typing import List, cast

from fastapi import FastAPI, HTTPException, Path, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.routing import APIRouter
from pydantic import JsonValue

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from api.context_builder import (  # noqa: E402
    EngineCallParams,
    _inject_player_engine_context,
    _inject_team_engine_context,
)
from api.context_router import router as context_router  # noqa: E402
from api.engine_pool import get_active_formats  # noqa: E402
from api.execution_service import ExecutionService  # noqa: E402
from api.legacy_router import router as legacy_router  # noqa: E402
from api.lifespan import run_startup_initialization  # noqa: E402
from api.route_helpers import EngineResolver, RequestValidator  # noqa: E402
from api.schemas import (  # noqa: E402
    ErrorResponse,
    ExecuteRequest,
    ExecuteResponse,
    FormatMetadata,
    HealthResponse,
    ManifestResponse,
)
from api.serializers import serialize_engine_output  # noqa: E402
from config.format_registry import get_format_manifest  # noqa: E402
from config.settings import (  # noqa: E402
    API_DOCS_URL,
    API_HOST,
    API_PORT,
    API_REDOC_URL,
    API_V1_PREFIX,
    CORS_ORIGINS,
)
from core.services import (  # noqa: E402
    ParamMapperService,
    SerializationService,
)
from core.interfaces.serialization_types import ManifestFunctionDef  # noqa: E402


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("CricketAPI")


app = FastAPI(
    title="Cricket Algo-Trading API",
    description=(
        "Manifest-driven REST API for cricket analysis. "
        "Serves engine functions for all formats via a single endpoint."
    ),
    version="2.0.0",
    docs_url=API_DOCS_URL,
    redoc_url=API_REDOC_URL,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(context_router)
app.include_router(legacy_router)
@app.on_event("startup")
def startup_event() -> None:
    """Initialize engine pool at API startup."""
    run_startup_initialization(logger)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error="HTTP_ERROR",
            detail=exc.detail,
            status_code=exc.status_code,
        ).model_dump(),
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled Exception: %s", exc)
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="INTERNAL_SERVER_ERROR",
            detail="An internal error occurred. Check server logs for details.",
            status_code=500,
        ).model_dump(),
    )
v1_router = APIRouter(prefix=API_V1_PREFIX)


@app.get("/health", response_model=HealthResponse, tags=["System"])
def health_check() -> HealthResponse:
    """API health check - returns loaded formats and match counts."""
    active = get_active_formats()
    return HealthResponse(
        status="active" if active else "no_formats_loaded",
        formats_loaded=list(active.keys()),
        total_matches={k: v["matches"] for k, v in active.items()},
    )


@v1_router.get("/formats", response_model=List[FormatMetadata], tags=["Formats"])
def list_formats() -> List[FormatMetadata]:
    """Returns metadata about all available formats for the Format Selector."""
    from config.format_registry import get_format_metadata

    return get_format_metadata()


@v1_router.get("/{format_type}/manifest", response_model=ManifestResponse, tags=["Manifest"])
def get_manifest(
    format_type: str = Path(..., description="Format key (e.g., 'odi')"),
) -> ManifestResponse:
    """Returns the format's complete manifest."""
    RequestValidator.validate_format(format_type)
    try:
        return cast(ManifestResponse, get_format_manifest(format_type))
    except (ValueError, ImportError) as exc:
        raise HTTPException(
            status_code=404,
            detail=f"No manifest for format '{format_type}': {exc}",
        )


@v1_router.post("/{format_type}/execute/{function_key}", response_model=ExecuteResponse, tags=["Execute"])
def execute_function(
    request: ExecuteRequest,
    format_type: str = Path(..., description="Format key (e.g., 'odi')"),
    function_key: str = Path(..., description="Function key from manifest (e.g., 'venue_bias')"),
) -> ExecuteResponse:
    """Execute any engine function declared in the format's manifest."""
    analyzer = RequestValidator.get_analyzer_or_404(format_type)
    fn_def = RequestValidator.find_function_in_manifest(analyzer, function_key)

    required_fields = fn_def.get("required_context", [])
    provided_params = request.params.model_dump(exclude_none=True)

    missing = []
    for field in required_fields:
        val = provided_params.get(field)
        if val is None or val == "" or (field == "venue" and val == "needed"):
            missing.append(field)

    if missing:
        raise HTTPException(
            status_code=400,
            detail=(
                "Required selection missing: Please provide "
                f"{', '.join(missing)} before executing this analysis."
            ),
        )

    engine_class_name = fn_def["engine_class"]
    engine_method_name = fn_def["engine_method"]

    engine_instance = EngineResolver.resolve(engine_class_name, analyzer)

    if not hasattr(engine_instance, engine_method_name):
        raise HTTPException(
            status_code=500,
            detail=f"Method '{engine_method_name}' not found on {engine_class_name}",
        )
    method = getattr(engine_instance, engine_method_name)

    call_params = cast(
        EngineCallParams,
        ParamMapperService.map_params(
            cast(ManifestFunctionDef, fn_def),
            request.params.model_dump(exclude_none=True),
        ),
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

    try:
        captured_output = io.StringIO()
        with redirect_stdout(captured_output):
            result = method(**call_params)
    except TypeError as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Parameter error calling {engine_class_name}.{engine_method_name}: {exc}",
        )
    except HTTPException:
        raise
    except (AttributeError, KeyError, ValueError, RuntimeError) as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Engine error in {engine_class_name}.{engine_method_name}: {exc}",
        )

    schematized = SerializationService.wrap_as_schema(result)
    serialized = serialize_engine_output(schematized)

    serialized = ExecutionService.post_process(
        engine_method_name=engine_method_name,
        serialized=serialized,
        call_params=dict(call_params),
        analyzer=analyzer,
    )

    return ExecuteResponse(
        function_key=function_key,
        output_type=fn_def.get("output_type", "unknown"),
        data=cast(JsonValue, serialized),
        metadata={
            "engine_class": engine_class_name,
            "engine_method": engine_method_name,
            "format": format_type,
        },
    )


app.include_router(v1_router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=API_HOST, port=API_PORT)
