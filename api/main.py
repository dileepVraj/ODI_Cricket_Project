"""api/main.py - FastAPI application."""

from __future__ import annotations

import logging
import os
import sys
from collections.abc import Callable

from fastapi import APIRouter, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from api.context_router import router as context_router  # noqa: E402
from api.discovery_router import router as discovery_router  # noqa: E402
from api.execute_router import router as execute_router  # noqa: E402
from api.legacy_router import router as legacy_router  # noqa: E402
from api.lifespan import run_startup_initialization  # noqa: E402
from api.schemas import ErrorResponse  # noqa: E402
from api.system_router import router as system_router  # noqa: E402
from config.settings import (  # noqa: E402
    API_DOCS_URL,
    API_HOST,
    API_PORT,
    API_REDOC_URL,
    CORS_ORIGINS,
    FINANCES_DB_PATH,
)

init_db: Callable[[str], None] | None = None
cockpit_router: APIRouter | None = None
cockpit_import_error: ImportError | None = None

try:
    from cockpit.database import init_db as cockpit_init_db  # noqa: E402
    from api.cockpit.router import cockpit_router as cockpit_router_impl  # noqa: E402
except ImportError as exc:  # pragma: no cover - environment dependent
    cockpit_import_error = exc
else:
    init_db = cockpit_init_db
    cockpit_router = cockpit_router_impl

finances_router_impl: APIRouter | None = None
finances_import_error: ImportError | None = None

try:
    from api.finances_router import finances_router as _finances_router_impl  # noqa: E402
    finances_router_impl = _finances_router_impl
except ImportError as exc:  # pragma: no cover - environment dependent
    finances_import_error = exc


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
app.include_router(system_router)
app.include_router(discovery_router)
app.include_router(execute_router)
if cockpit_router is not None:
    app.include_router(cockpit_router, prefix="/api/cockpit", tags=["Cockpit"])
if finances_router_impl is not None:
    app.include_router(finances_router_impl, prefix="/api/finances", tags=["Finances"])


@app.on_event("startup")
async def startup_event() -> None:
    """Initialize engine pool at API startup."""
    run_startup_initialization(logger)
    if init_db is None:
        if cockpit_import_error is not None:
            logger.warning("Cockpit module disabled: %s", cockpit_import_error)
        return
    init_db("ipl")
    init_db("odi")
    if finances_router_impl is not None:
        try:
            from cockpit.finances import FinancesStore  # noqa: E402
            finances_db_path = os.path.abspath(
                os.path.join(
                    PROJECT_ROOT,
                    os.getenv("FINANCES_DB_PATH", FINANCES_DB_PATH),
                )
            )
            app.state.finances = FinancesStore(finances_db_path)
            logger.info("FinancesStore initialized at %s", finances_db_path)
        except Exception as exc:  # pragma: no cover
            logger.warning("FinancesStore failed to initialize: %s", exc)


@app.on_event("shutdown")
async def shutdown_event() -> None:
    """Close long-lived app resources before the process exits."""
    finances = getattr(app.state, "finances", None)
    if finances is None:
        return
    try:
        finances.close()
    except Exception as exc:  # pragma: no cover
        logger.warning("FinancesStore failed to close: %s", exc)
    finally:
        app.state.finances = None


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


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=API_HOST, port=API_PORT)
