import uuid
from typing import Any

from fastapi import APIRouter, BackgroundTasks, Request
from pydantic import BaseModel, Field

from api.middleware.rate_limit import limiter
from api.webhooks.alerts import send_webhook


router = APIRouter()


class InfrastructureInferenceRequest(BaseModel):
    signals: list[dict[str, Any]] = Field(..., description="Operational signals from infra.")
    hypotheses: list[str] | None = Field(default=None, description="Optional hypotheses to test.")
    webhook_url: str | None = Field(default=None, description="Webhook for async inference updates.")


class InfrastructureInferenceResponse(BaseModel):
    inference_id: str
    summary: str
    confidence: float


@router.post("/inference", response_model=InfrastructureInferenceResponse)
@limiter.limit("15/minute")
async def run_infrastructure_inference(
    request: Request, payload: InfrastructureInferenceRequest, background_tasks: BackgroundTasks
) -> InfrastructureInferenceResponse:
    inference_id = str(uuid.uuid4())
    summary = "Inference pending further analysis."
    confidence = 0.4

    response = InfrastructureInferenceResponse(
        inference_id=inference_id,
        summary=summary,
        confidence=confidence,
    )

    if payload.webhook_url:
        background_tasks.add_task(send_webhook, payload.webhook_url, response.model_dump())

    return response
