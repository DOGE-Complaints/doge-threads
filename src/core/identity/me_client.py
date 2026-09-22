from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

import httpx

from core.config import AppConfig

DEFAULT_REQUEST_TIMEOUT_S = 10.0


class IdentityMeError(Exception):
    """Identity /me transport or response parse failure (fail-closed)."""


@dataclass(frozen=True)
class IdentityMeClient:
    """GET /me with forwarded Authorization: Bearer (gateway etalon)."""

    base_url: str
    timeout_s: float = DEFAULT_REQUEST_TIMEOUT_S

    def fetch_me(self, bearer_token: str) -> dict[str, Any] | None:
        token = bearer_token.strip()
        if not token:
            return None
        try:
            with httpx.Client(timeout=self.timeout_s) as client:
                response = client.get(
                    f"{self.base_url.rstrip('/')}/me",
                    headers={"Authorization": f"Bearer {token}"},
                )
        except httpx.TimeoutException as exc:
            raise IdentityMeError("Identity /me timed out.") from exc
        except httpx.HTTPError as exc:
            raise IdentityMeError("Identity /me request failed.") from exc

        if response.status_code in {401, 403}:
            return None
        if response.status_code >= 500:
            raise IdentityMeError(f"Identity /me returned {response.status_code}.")

        try:
            body: Any = response.json()
        except ValueError as exc:
            raise IdentityMeError("Identity /me returned invalid JSON.") from exc
        if not isinstance(body, dict):
            raise IdentityMeError("Identity /me returned non-object JSON.")
        return body


def parse_me_identity_verified(body: Mapping[str, Any]) -> bool | None:
    """Parse data.identity_verified only (gateway etalon; missing → None)."""
    data = body.get("data")
    if not isinstance(data, Mapping):
        raise IdentityMeError("Invalid /me response: missing data object.")
    if "identity_verified" not in data:
        return None
    raw = data.get("identity_verified")
    if not isinstance(raw, bool):
        raise IdentityMeError("Invalid /me response: identity_verified must be bool.")
    return raw


def build_identity_me_from_config(config: AppConfig) -> IdentityMeClient | None:
    base = config.identity_base_url
    if base is None:
        return None
    return IdentityMeClient(
        base_url=base,
        timeout_s=DEFAULT_REQUEST_TIMEOUT_S,
    )
