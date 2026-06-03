# Registry-State Sync

- **Route**: `GET /api/v1/registry/status`
- **Purpose**: Health snapshot of registry synchronization across agents.
- **Auth**: `X-Agent-Token` header required.
- **Rate limit**: 30/minute.

## Response
- `registry` (string) – health string
- `synced` (boolean)
- `agents_registered` (integer)
- `version` (string)

## Notes
- Validated against `schemas/registry_status.json`.
- Replace stub data with live registry integration.
