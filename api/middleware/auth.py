import os
from fastapi import Header, HTTPException, status


def verify_agent_token(x_agent_token: str | None = Header(default=None)) -> None:
    """
    Minimal token-based authentication for agents.
    Expects the X-Agent-Token header to match AGENT_API_KEY env var.
    """
    expected_token = os.getenv("AGENT_API_KEY")
    if not expected_token:
        # Fail closed if no key configured.
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication not configured for this node",
        )
    if x_agent_token != expected_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing X-Agent-Token",
        )
