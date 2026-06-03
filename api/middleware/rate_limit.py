from fastapi import Request
from slowapi import Limiter
from slowapi.util import get_remote_address


def limiter_key_func(request: Request) -> str:
    # Use client host as rate-limiting key; can be replaced with agent id when available.
    return get_remote_address(request)


limiter = Limiter(key_func=limiter_key_func, default_limits=["100/minute"])
