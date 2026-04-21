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

from fastapi import Header, Query, HTTPException, Depends, Request
from datetime import datetime
from app.core.database import get_db, get_setting

async def require_api_key(
    request: Request,
    x_api_key: str = Header(None, alias="X-API-Key"),
    api: str = Query(None),
    api_key: str = Query(None),
):
    db = get_db()
    enforcement = await get_setting("api_enforcement", True)

    key = x_api_key or api or api_key

    if not enforcement:
        if key:
            record = await db.api_keys.find_one({"key": key})
            if record and record.get("enabled", True):
                await db.api_keys.update_one(
                    {"key": key},
                    {"$inc": {"usage_count": 1}, "$set": {"last_used": datetime.utcnow()}}
                )
                return record
        return {"key": None, "owner": "anonymous", "enabled": True, "usage_count": 0}

    if not key:
        raise HTTPException(
            status_code=401,
            detail={"error": "missing_api_key", "msg": "Pass ?api=YOUR_KEY or X-API-Key header"}
        )

    record = await db.api_keys.find_one({"key": key})

    if not record:
        raise HTTPException(status_code=401, detail={"error": "invalid_api_key"})

    if not record.get("enabled", True):
        raise HTTPException(status_code=403, detail={"error": "api_key_disabled"})

    expiry = record.get("expires_at")
    if expiry and datetime.utcnow() > expiry:
        raise HTTPException(status_code=403, detail={"error": "api_key_expired"})

    await db.api_keys.update_one(
        {"key": key},
        {"$inc": {"usage_count": 1}, "$set": {"last_used": datetime.utcnow()}}
    )

    return record
