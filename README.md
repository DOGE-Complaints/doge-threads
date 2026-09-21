# doge-threads

Python 3.11 + FastAPI service shell for entity threads. Default local port **8001** (does not collide with gateway 8000).

## Local

1. Copy `example.env` → `.env` (do not commit secrets).
2. `make serve` or `make dev` — uvicorn `--app-dir src core.api.asgi_app:app` (app modules land in later stories).
3. `make check-env` — print REQ0 env subset.
4. `make test` — reserved until smoke/CI story (`STORY-THREADS-00-06`).

## Layout

Repo skeleton only: `pyproject.toml`, `pyrightconfig.json`, `requirements.txt`, `Makefile`, `railpack.json`, `example.env`, this README, `.gitignore`. Application `src/core/**` is out of this story.
