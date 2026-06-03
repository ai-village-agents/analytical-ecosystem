import uuid
from typing import Any

from fastapi import APIRouter, BackgroundTasks, Request
from pydantic import BaseModel, Field

from api.middleware.rate_limit import limiter
from api.services.history import record_pattern_event
from api.webhooks.alerts import send_webhook


router = APIRouter()


class Signal(BaseModel):
    id: str
    value: Any
    timestamp: str | None = None


class PatternDetectionRequest(BaseModel):
    pattern_type: str = Field(..., description="Pattern classification key.")
    signals: list[Signal] = Field(..., description="Signals to evaluate for the pattern.")
    context: dict[str, Any] | None = Field(
        default=None, description="Optional context to guide pattern detection."
    )
    webhook_url: str | None = Field(
        default=None, description="Webhook to receive async detection notifications."
    )


class PatternDetectionResponse(BaseModel):
    detection_id: str
    matches: list[dict[str, Any]]
    status: str


@router.post(
    "/detection",
    response_model=PatternDetectionResponse,
)
@limiter.limit("15/minute")
async def detect_pattern(
    request: Request, payload: PatternDetectionRequest, background_tasks: BackgroundTasks
) -> PatternDetectionResponse:
    detection_id = str(uuid.uuid4())
    matches: list[dict[str, Any]] = [
        {
            "signal_id": signal.id,
            "matched": True,
            "confidence": 0.5,
        }
        for signal in payload.signals
    ]

    record_pattern_event(
        {
            "detection_id": detection_id,
            "pattern_type": payload.pattern_type,
            "matches": matches,
        }
    )

    if payload.webhook_url:
        background_tasks.add_task(
            send_webhook,
            payload.webhook_url,
            {"detection_id": detection_id, "matches": matches, "status": "queued"},
        )

    return PatternDetectionResponse(detection_id=detection_id, matches=matches, status="queued")
