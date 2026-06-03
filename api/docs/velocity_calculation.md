# Velocity Calculation Service

- **Route**: `POST /api/v1/velocity/calculate`
- **Purpose**: Normalize velocity computation across analytical agents.
- **Auth**: `X-Agent-Token` header required.
- **Rate limit**: 30/minute.

## Request
- `positions` (array<number>)
- `timestamps` (array<number>) – must align with positions

## Response
- `average_velocity` (number)
- `deltas` (array<number>) – per-step velocities

## Notes
- Validated against `schemas/velocity_calculation.json`.
