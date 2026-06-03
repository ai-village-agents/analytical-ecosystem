# Verification Gateway

- **Route**: `POST /api/v1/verification/confirm`
- **Purpose**: Standardized confirmation workflow for claims using multi-agent evidence.
- **Auth**: `X-Agent-Token` header required.
- **Rate limit**: 20/minute.

## Request
- `claim_id` (string)
- `evidence` (array<object>) – evidence packets
- `requester` (string) – requesting agent id
- `webhook_url` (string, optional) – async status hooks

## Response
- `verification_id` (string)
- `claim_id` (string)
- `status` (string) – initial state `in_review`
- `verdict` (string) – initial state `pending`

## Notes
- Validated against `schemas/verification_gateway.json`.
