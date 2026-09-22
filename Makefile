.PHONY: serve dev check-env test test-live test-e2e-domain

# Default local PORT=8001 (gateway uses 8000).
# serve/dev load .env when present. asgi_app lands in STORY-THREADS-00-03.

serve:
	@if [ -f ./.env ]; then set -a && . ./.env && set +a; fi; \
	python3 -m uvicorn --app-dir src core.api.asgi_app:app \
	  --host 127.0.0.1 --port $${PORT:-8001}

dev:
	@if [ -f ./.env ]; then set -a && . ./.env && set +a; fi; \
	python3 -m uvicorn --app-dir src core.api.asgi_app:app \
	  --host 127.0.0.1 --port $${PORT:-8001} --reload --reload-dir src

check-env:
	@if [ -f ./.env ]; then set -a && . ./.env && set +a; fi; \
	echo "APP_PROFILE         = $${APP_PROFILE:-<not set>}" && \
	echo "DB_BACKEND          = $${DB_BACKEND:-<not set>}" && \
	echo "PORT                = $${PORT:-8001}" && \
	echo "SUPABASE_URL        = $${SUPABASE_URL:-<not set>}" && \
	echo "SERVICE_API_TOKEN   = $${SERVICE_API_TOKEN:-<not set>}" && \
	echo "IDENTITY_BASE_URL   = $${IDENTITY_BASE_URL:-<not set>}" && \
	echo "GATEWAY_BASE_URL    = $${GATEWAY_BASE_URL:-<not set>}"

# Offline pytest (excludes reserved live_integration + domain_e2e).
test:
	python3 -m pytest tests/ -q -m "not live_integration and not domain_e2e"

# Live PostgREST (TC-05). Skip only if SUPABASE_URL / SUPABASE_SERVICE_ROLE absent.
test-live:
	@if [ -f ./.env ]; then set -a && . ./.env && set +a; fi; \
	python3 -m pytest tests/ -q -m live_integration

# Domain e2e Me+GW+DB (TC-07). Skip only if required env absent. Out-of-CI.
test-e2e-domain:
	@if [ -f ./.env ]; then set -a && . ./.env && set +a; fi; \
	python3 -m pytest tests/ -q -m domain_e2e
