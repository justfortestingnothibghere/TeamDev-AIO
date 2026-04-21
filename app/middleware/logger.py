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
from datetime import datetime
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from app.core.database import get_db

class RequestLoggerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.time()
        response = await call_next(request)
        elapsed = round((time.time() - start) * 1000, 2)

        if request.url.path.startswith("/static"):
            return response

        db = get_db()
        if db is not None:
            api_key = request.headers.get("X-API-Key") or request.query_params.get("api_key")
            await db.request_logs.insert_one({
                "ip": request.client.host,
                "method": request.method,
                "path": request.url.path,
                "query": str(request.url.query),
                "status": response.status_code,
                "ms": elapsed,
                "api_key": api_key,
                "ts": datetime.utcnow()
            })

        return response
