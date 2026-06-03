# Pattern Detection API

- **Route**: `POST /api/v1/patterns/detection`
- **Purpose**: Detect recurring analytical patterns from submitted signals and record into the pattern history database.
- **Auth**: `X-Agent-Token` header required.
- **Rate limit**: 20/minute.

## Request
- `pattern_type` (string) – classifier key
- `signals` (array<object>) – `{ id, value, timestamp? }`
- `context` (object, optional) – guiding metadata
- `webhook_url` (string, optional) – receive async updates

## Response
- `detection_id` (string)
- `matches` (array<object>) – match metadata per signal
- `status` (string) – initial processing state

## Notes
- Validated against `schemas/pattern_detection.json`.
- Persists detection event into the pattern history integration stub at `services/history.py`.
