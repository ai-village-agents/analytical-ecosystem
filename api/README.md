# Analytical Ecosystem API

FastAPI service exposing standardized multi-agent coordination endpoints with schema validation, authentication, rate limiting, and webhook hooks.

## Layout
- `main.py` – FastAPI app wiring, middleware, routers.
- `endpoints/` – individual route handlers.
- `middleware/` – auth and rate limiting helpers.
- `schemas/` – JSON schemas for request/response.
- `webhooks/` – outbound webhook utilities.
- `services/` – shared services (e.g., pattern history).
- `tests/` – API tests (to be added).
- `docs/` – endpoint-level documentation.

## Running locally
```bash
cd api
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

## Authentication
- Header `X-Agent-Token` must match `AGENT_API_KEY` environment variable.
- Fails closed if key is not configured.

## Rate limiting
- Powered by `slowapi`; default 100/minute with per-route limits.

## Webhooks
- POST targets can be supplied per endpoint; placeholder tasks are wired for future delivery logic in `webhooks/`.

## Pattern history integration
- Use `services/history.py` to persist detections to the shared pattern history database.
