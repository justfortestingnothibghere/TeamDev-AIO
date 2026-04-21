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


from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from app.core.database import get_db

class BanMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path.startswith("/admin"):
            return await call_next(request)

        ip = request.client.host
        db = get_db()

        if db is not None:
            banned = await db.banned_ips.find_one({"ip": ip, "active": True})
            if banned:
                return JSONResponse(
                    status_code=403,
                    content={
                        "error": "ip_banned",
                        "reason": banned.get("reason", "Policy violation"),
                        "msg": "Your IP has been banned. Contact support. @TeamDevXBots"
                    }
                )

        return await call_next(request)
