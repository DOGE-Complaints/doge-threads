from __future__ import annotations

from dataclasses import dataclass
from os import environ
from typing import Any, Mapping

import httpx

from core.config import AppConfig

DEFAULT_REQUEST_TIMEOUT_S = 10.0


class GatewayClientError(Exception):
    """Gateway outbound transport failure."""


@dataclass(frozen=True)
class GatewayClient:
    """httpx client for GATEWAY_BASE_URL. Path is caller-supplied; no named route."""

    base_url: str
    timeout_s: float = DEFAULT_REQUEST_TIMEOUT_S
    service_token: str | None = None

    def service_headers(self) -> dict[str, str]:
        token = (self.service_token or "").strip()
        if not token:
            return {}
        return {
            "Authorization": f"Bearer {token}",
            "X-Service-Token": token,
        }

    def request(self, method: str, path: str, **kwargs: Any) -> httpx.Response:
        relative = path if path.startswith("/") else f"/{path}"
        url = f"{self.base_url.rstrip('/')}{relative}"
        headers = dict(self.service_headers())
        extra = kwargs.pop("headers", None)
        if extra:
            headers.update(extra)
        try:
            with httpx.Client(timeout=self.timeout_s) as client:
                return client.request(method, url, headers=headers, **kwargs)
        except httpx.TimeoutException as exc:
            raise GatewayClientError("Gateway request timed out.") from exc
        except httpx.HTTPError as exc:
            raise GatewayClientError("Gateway request failed.") from exc


def build_gateway_client_from_config(
    config: AppConfig,
    *,
    service_token: str | None = None,
    env: Mapping[str, str] | None = None,
) -> GatewayClient | None:
    base = config.gateway_base_url
    if base is None:
        return None
    token = service_token
    if token is None:
        source = env if env is not None else environ
        raw = source.get("SERVICE_API_TOKEN")
        token = raw.strip() if raw and raw.strip() else None
    return GatewayClient(
        base_url=base,
        timeout_s=DEFAULT_REQUEST_TIMEOUT_S,
        service_token=token,
    )
