"""
Enhanced pattern detection endpoint with webhook integration.
"""

import uuid
from typing import Any

from fastapi import APIRouter, BackgroundTasks, Request
from pydantic import BaseModel, Field

from api.middleware.rate_limit import limiter
from api.services.history import record_pattern_event
from api.webhooks.alerts import alert_pattern_detected


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
    alert_agents: list[str] | None = Field(
        default=None, description="Specific agents to alert (empty for all registered)."
    )


class PatternDetectionResponse(BaseModel):
    detection_id: str
    matches: list[dict[str, Any]]
    status: str
    alert_sent: bool = False


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

    # Record to pattern history
    record_pattern_event(
        {
            "detection_id": detection_id,
            "pattern_type": payload.pattern_type,
            "matches": matches,
            "context": payload.context,
        }
    )

    # Extract context for alerts
    context = payload.context or {}
    fragment_range = context.get("fragment_range", "unknown")
    detection_agent = context.get("detection_agent", "unknown")
    
    # Calculate average confidence from matches
    confidence_sum = sum(match.get("confidence", 0.5) for match in matches)
    avg_confidence = confidence_sum / len(matches) if matches else 0.5

    # Send webhook alert if configured
    alert_sent = False
    if payload.webhook_url:
        background_tasks.add_task(
            alert_pattern_detected,
            pattern_type=payload.pattern_type,
            fragment_range=fragment_range,
            detection_agent=detection_agent,
            confidence=avg_confidence,
            additional_data={
                "detection_id": detection_id,
                "match_count": len(matches),
                "alert_agents": payload.alert_agents
            }
        )
        alert_sent = True

    return PatternDetectionResponse(
        detection_id=detection_id,
        matches=matches,
        status="queued",
        alert_sent=alert_sent
    )
