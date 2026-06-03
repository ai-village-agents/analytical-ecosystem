from fastapi import APIRouter, Request

from api.middleware.rate_limit import limiter


router = APIRouter()


@router.get("/status")
@limiter.limit("15/minute")
async def get_registry_status(request: Request) -> dict:
    # TODO: connect to registry service and return live state snapshot.
    return {
        "registry": "online",
        "synced": True,
        "agents_registered": 0,
        "version": "0.1.0",
    }
