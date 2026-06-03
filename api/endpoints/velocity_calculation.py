from fastapi import APIRouter, BackgroundTasks, Request
from pydantic import BaseModel, Field

from api.middleware.rate_limit import limiter


router = APIRouter()


class VelocityCalculationRequest(BaseModel):
    positions: list[float] = Field(..., description="Sequence of positional measurements.")
    timestamps: list[float] = Field(..., description="Timestamps corresponding to positions.")


class VelocityCalculationResponse(BaseModel):
    average_velocity: float
    deltas: list[float]


@router.post("/calculate", response_model=VelocityCalculationResponse)
@limiter.limit("15/minute")
async def calculate_velocity(
    request: Request, payload: VelocityCalculationRequest, background_tasks: BackgroundTasks
) -> VelocityCalculationResponse:
    if len(payload.positions) < 2 or len(payload.positions) != len(payload.timestamps):
        return VelocityCalculationResponse(average_velocity=0.0, deltas=[])

    deltas: list[float] = []
    for idx in range(1, len(payload.positions)):
        delta_pos = payload.positions[idx] - payload.positions[idx - 1]
        delta_time = payload.timestamps[idx] - payload.timestamps[idx - 1]
        if delta_time == 0:
            deltas.append(0.0)
        else:
            deltas.append(delta_pos / delta_time)

    avg = sum(deltas) / len(deltas) if deltas else 0.0
    return VelocityCalculationResponse(average_velocity=avg, deltas=deltas)
