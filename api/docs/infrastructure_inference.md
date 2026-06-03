# Infrastructure Inference API

- **Route**: `POST /api/v1/infrastructure/inference`
- **Purpose**: Derive infrastructure states from operational signals and hypotheses.
- **Auth**: `X-Agent-Token` header required.
- **Rate limit**: 15/minute.

## Request
- `signals` (array<object>)
- `hypotheses` (array<string>, optional)
- `webhook_url` (string, optional) – async updates

## Response
- `inference_id` (string)
- `summary` (string)
- `confidence` (number)

## Notes
- Validated against `schemas/infrastructure_inference.json`.
