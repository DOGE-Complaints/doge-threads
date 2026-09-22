from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

try:
    import httpx
except Exception:  # pragma: no cover - optional in some local envs
    httpx = None

logger = logging.getLogger(__name__)

# Four 01-08 shell tables. Do not copy civic readiness sets.
REQUIRED_READINESS_TABLES: frozenset[str] = frozenset(
    {
        "thread_threads",
        "thread_comments",
        "thread_reaction_marks",
        "thread_attachment_refs",
    }
)


@dataclass
class SupabaseDatabase:
    """PostgREST httpx client for the shared node project."""

    base_url: str
    service_role_key: str
    timeout_s: float = 15.0

    @classmethod
    def from_http(
        cls,
        *,
        supabase_url: str,
        service_role_key: str,
        timeout_s: float = 15.0,
    ) -> SupabaseDatabase:
        if not supabase_url.startswith("http://") and not supabase_url.startswith(
            "https://"
        ):
            raise ValueError(f"Unsupported SUPABASE_URL: {supabase_url!r}.")
        if not service_role_key.strip():
            raise ValueError("SUPABASE_SERVICE_ROLE must be non-empty.")
        return cls(
            base_url=supabase_url.rstrip("/"),
            service_role_key=service_role_key.strip(),
            timeout_s=timeout_s,
        )

    def _client(self) -> Any:
        if httpx is None:
            raise RuntimeError(
                "Supabase HTTP backend requires httpx. Install dependency: httpx."
            )
        return httpx.Client(timeout=self.timeout_s)

    def _headers(self, *, prefer: str | None = None) -> dict[str, str]:
        headers = {
            "apikey": self.service_role_key,
            "Authorization": f"Bearer {self.service_role_key}",
            "Content-Type": "application/json",
        }
        if prefer is not None:
            headers["Prefer"] = prefer
        return headers

    def _request(
        self,
        *,
        method: str,
        path: str,
        params: dict[str, str] | None = None,
        json_body: Any = None,
        prefer: str | None = None,
    ) -> Any:
        logger.debug(
            "supabase.request",
            extra={"method": method, "path": path, "has_params": bool(params)},
        )
        try:
            with self._client() as client:
                response = client.request(
                    method=method,
                    url=f"{self.base_url}{path}",
                    headers=self._headers(prefer=prefer),
                    params=params,
                    json=json_body,
                )
            response.raise_for_status()
        except Exception:
            logger.exception(
                "supabase.request_failed",
                extra={"method": method, "path": path, "stage": "db.supabase"},
            )
            raise
        if response.text.strip():
            return response.json()
        return None

    def healthcheck(self) -> bool:
        """Connectivity only. Does not probe product or civic tables."""
        try:
            self._request(method="GET", path="/rest/v1/", params={"limit": "1"})
            return True
        except Exception:
            return False

    def required_tables_ready(self) -> bool:
        """True only when every name in REQUIRED_READINESS_TABLES probes OK."""
        try:
            for table_name in REQUIRED_READINESS_TABLES:
                self._request(
                    method="GET",
                    path=f"/rest/v1/{table_name}",
                    params={"select": "*", "limit": "1"},
                )
            return True
        except Exception:
            return False
