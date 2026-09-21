.PHONY: serve dev check-env test

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

# Offline pytest (excludes reserved live_integration marker).
test:
	python3 -m pytest tests/ -q -m "not live_integration"
