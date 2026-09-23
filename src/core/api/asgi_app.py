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
from core.api.social_handlers import (
    CommentWriteBody,
    ReactionWriteBody,
    handle_create_comment,
    handle_knobs,
    handle_reaction,
    handle_tree,
)
from core.api.product_auth import product_write_bearer as apply_product_write_bearer
from core.api.security import UnauthorizedError
from core.config import ConfigError
from core.domain.errors import (
    AttachmentRefError,
    DiscussionStoreError,
    ReactionMarkError,
    ThreadContextError,
    WriteDeniedError,
)
from core.identity.me_client import IdentityMeError
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

# HTTP-04: PUT required for reactions (U4 origin lockdown still OOS).
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST", "PUT", "OPTIONS"],
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
    if "error" not in payload:
        return 200
    code = payload["error"]["code"]
    if code == "UNAUTHORIZED":
        return 401
    if code == "FORBIDDEN":
        return 403
    return 200


def product_write_bearer(
    request: Request,
    deps: ApiDependencies = Depends(get_api_dependencies),
) -> str:
    """Named FastAPI Depends for product write handlers (HTTP-03…05). No route bind here."""
    return apply_product_write_bearer(request, deps)


def _read_trace_id(request: Request) -> str:
    incoming = request.headers.get("x-trace-id")
    return ensure_trace_id(incoming)


def _envelope_response(request: Request, exc: Exception, *, fallback_status: int | None = None) -> JSONResponse:
    envelope = build_error_envelope(exc, trace_id=_read_trace_id(request)).as_dict()
    status = fallback_status if fallback_status is not None else _json_http_status(envelope)
    return JSONResponse(content=envelope, status_code=status)


@app.exception_handler(UnauthorizedError)
async def unauthorized_error_handler(request: Request, exc: UnauthorizedError) -> JSONResponse:
    return _envelope_response(request, exc)


@app.exception_handler(WriteDeniedError)
async def write_denied_error_handler(request: Request, exc: WriteDeniedError) -> JSONResponse:
    return _envelope_response(request, exc)


@app.exception_handler(IdentityMeError)
async def identity_me_error_handler(request: Request, exc: IdentityMeError) -> JSONResponse:
    return _envelope_response(request, exc)


@app.exception_handler(DiscussionStoreError)
async def discussion_store_error_handler(request: Request, exc: DiscussionStoreError) -> JSONResponse:
    return _envelope_response(request, exc)


@app.exception_handler(ThreadContextError)
async def thread_context_error_handler(request: Request, exc: ThreadContextError) -> JSONResponse:
    return _envelope_response(request, exc)


@app.exception_handler(ReactionMarkError)
async def reaction_mark_error_handler(request: Request, exc: ReactionMarkError) -> JSONResponse:
    return _envelope_response(request, exc)


@app.exception_handler(AttachmentRefError)
async def attachment_ref_error_handler(request: Request, exc: AttachmentRefError) -> JSONResponse:
    return _envelope_response(request, exc)


@app.exception_handler(ConfigError)
async def config_error_handler(request: Request, exc: ConfigError) -> JSONResponse:
    return _envelope_response(request, exc, fallback_status=500)


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


@app.get("/threads/knobs")
async def threads_knobs(
    request: Request,
    deps: ApiDependencies = Depends(get_api_dependencies),
) -> JSONResponse:
    payload = handle_knobs(deps, trace_id=_read_trace_id(request))
    return JSONResponse(content=payload, status_code=_json_http_status(payload))


@app.get("/threads/issues/{issue_id}")
async def threads_tree(
    issue_id: str,
    request: Request,
    deps: ApiDependencies = Depends(get_api_dependencies),
) -> JSONResponse:
    payload = handle_tree(deps, issue_id, trace_id=_read_trace_id(request))
    return JSONResponse(content=payload, status_code=_json_http_status(payload))


@app.post("/threads/issues/{issue_id}/comments")
async def threads_create_comment(
    issue_id: str,
    request: Request,
    payload: CommentWriteBody,
    token: str = Depends(product_write_bearer),
    deps: ApiDependencies = Depends(get_api_dependencies),
) -> JSONResponse:
    body = handle_create_comment(
        deps,
        issue_id,
        payload,
        token,
        trace_id=_read_trace_id(request),
    )
    return JSONResponse(content=body, status_code=_json_http_status(body))


@app.put("/threads/issues/{issue_id}/reactions")
async def threads_reaction(
    issue_id: str,
    request: Request,
    payload: ReactionWriteBody,
    token: str = Depends(product_write_bearer),
    deps: ApiDependencies = Depends(get_api_dependencies),
) -> JSONResponse:
    body = handle_reaction(
        deps,
        issue_id,
        payload,
        token,
        trace_id=_read_trace_id(request),
    )
    return JSONResponse(content=body, status_code=_json_http_status(body))
