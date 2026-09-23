"""t01 — DOGESTONIA_SCHEMA_* in ENV_SCHEMA + example.env (S1)."""

from __future__ import annotations

from pathlib import Path

from core.config import ENV_SCHEMA, load_config_from_env

_EXAMPLE = Path(__file__).resolve().parents[1] / "example.env"


def test_env_schema_lists_dogestonia_schema_keys() -> None:
    names = {spec.name for spec in ENV_SCHEMA}
    assert "DOGESTONIA_SCHEMA_ID" in names
    assert "DOGESTONIA_SCHEMA_VERSION" in names


def test_load_config_optional_schema_keys() -> None:
    empty = load_config_from_env({"APP_PROFILE": "demo"})
    assert empty.dogestonia_schema_id is None
    assert empty.dogestonia_schema_version is None
    filled = load_config_from_env(
        {
            "APP_PROFILE": "demo",
            "DOGESTONIA_SCHEMA_ID": "uus_veerenni_civic",
            "DOGESTONIA_SCHEMA_VERSION": "v3",
        }
    )
    assert filled.dogestonia_schema_id == "uus_veerenni_civic"
    assert filled.dogestonia_schema_version == "v3"


def test_example_env_documents_s1() -> None:
    text = _EXAMPLE.read_text(encoding="utf-8")
    assert "DOGESTONIA_SCHEMA_ID=" in text
    assert "DOGESTONIA_SCHEMA_VERSION=" in text
    assert "ThreadKey.node" in text or "node = ID" in text or "node=ID" in text or "ID only" in text
