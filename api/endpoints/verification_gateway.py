import uuid
from typing import Any

from fastapi import APIRouter, BackgroundTasks, Request
from pydantic import BaseModel, Field

from api.middleware.rate_limit import limiter
from api.webhooks.alerts import send_webhook


router = APIRouter()


class VerificationRequest(BaseModel):
    claim_id: str = Field(..., description="Unique identifier for the claim or observation.")
    evidence: list[dict[str, Any]] = Field(..., description="Evidence packets for verification.")
    requester: str = Field(..., description="Agent requesting verification.")
    webhook_url: str | None = Field(default=None, description="Optional webhook for async updates.")


class VerificationResponse(BaseModel):
    verification_id: str
    claim_id: str
    status: str
    verdict: str


@router.post("/confirm", response_model=VerificationResponse)
@limiter.limit("15/minute")
async def confirm_verification(
    request: Request, payload: VerificationRequest, background_tasks: BackgroundTasks
) -> VerificationResponse:
    verification_id = str(uuid.uuid4())

    response = VerificationResponse(
        verification_id=verification_id,
        claim_id=payload.claim_id,
        status="in_review",
        verdict="pending",
    )

    if payload.webhook_url:
        background_tasks.add_task(
            send_webhook,
            payload.webhook_url,
            response.model_dump(),
        )

    return response
