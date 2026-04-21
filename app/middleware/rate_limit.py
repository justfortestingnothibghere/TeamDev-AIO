"""
╔══════════════════╗
              TEAMDEV
╚══════════════════╝

[ PROJECT   ]  TeamDev AIO (All-In-One Downloader)
[ DEVELOPER ]  @MR_ARMAN_08

────────────────────

[ SUPPORT   ]  https://t.me/Team_X_Og
[ UPDATES   ]  https://t.me/TeamDevXBots
[ ABOUT US  ]  https://TeamDev.sbs

────────────────────

[ DONATE    ]  https://Pay.TeamDev.sbs

────────────────────
      FAST • POWERFUL • ALL-IN-ONE
      
"""


import time
from collections import defaultdict
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from app.core.database import get_db

_buckets: dict = defaultdict(list)

DEFAULT_RATE = {"requests": 60, "window": 60}

async def get_rate_config(scope: str) -> dict:
    db = get_db()
    if db is None:
        return DEFAULT_RATE
    cfg = await db.rate_configs.find_one({"scope": scope})
    if cfg:
        return {"requests": cfg["requests"], "window": cfg["window"]}
    global_cfg = await db.rate_configs.find_one({"scope": "global"})
    if global_cfg:
        return {"requests": global_cfg["requests"], "window": global_cfg["window"]}
    return DEFAULT_RATE

class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path.startswith("/admin") or request.url.path == "/health":
            return await call_next(request)

        ip = request.client.host
        api_key = request.headers.get("X-API-Key") or request.query_params.get("api_key")

        scope = f"key:{api_key}" if api_key else f"ip:{ip}"
        cfg = await get_rate_config(scope)

        now = time.time()
        window = cfg["window"]
        limit = cfg["requests"]

        _buckets[scope] = [t for t in _buckets[scope] if now - t < window]

        if len(_buckets[scope]) >= limit:
            retry_after = int(window - (now - _buckets[scope][0]))
            return JSONResponse(
                status_code=429,
                content={
                    "error": "rate_limit_exceeded",
                    "retry_after": retry_after,
                    "limit": limit,
                    "window": window
                },
                headers={"Retry-After": str(retry_after)}
            )

        _buckets[scope].append(now)
        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(limit)
        response.headers["X-RateLimit-Remaining"] = str(limit - len(_buckets[scope]))
        response.headers["X-RateLimit-Reset"] = str(int(now + window))
        return response
