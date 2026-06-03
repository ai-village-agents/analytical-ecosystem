from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from api.endpoints import (
    infrastructure_inference,
    pattern_detection,
    registry_status,
    velocity_calculation,
    verification_gateway,
)
from api.middleware.auth import verify_agent_token
from api.middleware.rate_limit import limiter


app = FastAPI(
    title="Analytical Ecosystem API",
    version="0.1.0",
    description="Cross-framework API for standardized multi-agent analytical coordination.",
    dependencies=[Depends(verify_agent_token)],
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(pattern_detection.router, prefix="/api/v1/patterns", tags=["patterns"])
app.include_router(verification_gateway.router, prefix="/api/v1/verification", tags=["verification"])
app.include_router(registry_status.router, prefix="/api/v1/registry", tags=["registry"])
app.include_router(velocity_calculation.router, prefix="/api/v1/velocity", tags=["velocity"])
app.include_router(
    infrastructure_inference.router, prefix="/api/v1/infrastructure", tags=["infrastructure"]
)


@app.get("/health")
def healthcheck() -> dict:
    return {"status": "ok"}
