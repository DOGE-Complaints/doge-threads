from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from functools import lru_cache
from typing import Any

from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from core.api.dependencies import ApiDependencies, build_api_dependencies
from core.api.envelope import build_error_envelope, ensure_trace_id
from core.api.handlers import handle_health, handle_readiness
from core.config import ConfigError
from core.logging_setup import configure_logging


@asynccontextmanager
async def _lifespan(_: FastAPI):
    deps = get_api_dependencies()
    configure_logging(
        deps.config.log_level,
        log_format=deps.config.log_format,
        log_debug_dir=deps.config.log_debug_dir,
    )
    logging.getLogger(__name__).info(
        "startup.config db_backend=%s profile=%s",
        deps.config.db_backend,
        deps.config.profile.value,
        extra={
            "db_backend": deps.config.db_backend,
            "profile": deps.config.profile.value,
            "stage": "api.startup",
        },
    )
    if deps.config.db_backend == "in_memory":
        logging.getLogger(__name__).warning(
            "startup.db_backend_in_memory",
            extra={"hint": "set DB_BACKEND=supabase for persistent remote writes"},
        )
    try:
        yield
    finally:
        logging.getLogger(__name__).info(
            "shutdown.lifecycle",
            extra={"stage": "api.shutdown"},
        )


app = FastAPI(
    title="doge-threads",
    version="0.1.0",
    lifespan=_lifespan,
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["x-trace-id", "authorization"],
)


@app.middleware("http")
async def runtime_exception_diagnostics(request: Request, call_next: Any) -> Any:
    trace_id = _read_trace_id(request)
    try:
        return await call_next(request)
    except Exception:
        logging.getLogger("core.api").exception(
            "api.http",
            extra={
                "stage": "api.http",
                "trace_id": trace_id,
                "path": request.url.path,
                "method": request.method,
            },
        )
        raise


@lru_cache(maxsize=1)
def _cached_dependencies() -> ApiDependencies:
    return build_api_dependencies()


def _clear_api_dependencies_cache() -> None:
    _cached_dependencies.cache_clear()
    build_api_dependencies.cache_clear()


def get_api_dependencies() -> ApiDependencies:
    return _cached_dependencies()


def _json_http_status(payload: dict[str, Any]) -> int:
    if "error" in payload and payload["error"]["code"] == "UNAUTHORIZED":
        return 401
    return 200


def _read_trace_id(request: Request) -> str:
    incoming = request.headers.get("x-trace-id")
    return ensure_trace_id(incoming)


@app.exception_handler(ConfigError)
async def config_error_handler(request: Request, exc: ConfigError) -> JSONResponse:
    trace_id = _read_trace_id(request)
    envelope = build_error_envelope(exc, trace_id=trace_id).as_dict()
    return JSONResponse(content=envelope, status_code=500)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    trace_id = _read_trace_id(request)
    envelope = build_error_envelope(exc, trace_id=trace_id).as_dict()
    return JSONResponse(content=envelope, status_code=500)


@app.get("/health")
async def health(
    request: Request,
    deps: ApiDependencies = Depends(get_api_dependencies),
) -> JSONResponse:
    payload = handle_health(deps, trace_id=_read_trace_id(request))
    return JSONResponse(content=payload, status_code=_json_http_status(payload))


@app.get("/ready")
async def readiness(
    request: Request,
    deps: ApiDependencies = Depends(get_api_dependencies),
) -> JSONResponse:
    payload = handle_readiness(deps, trace_id=_read_trace_id(request))
    return JSONResponse(content=payload, status_code=_json_http_status(payload))
