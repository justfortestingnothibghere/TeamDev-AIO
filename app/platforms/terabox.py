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

# Read @License Don't Copy This File This Code Made Only For This Project Do Not Try To Use This Script.

import requests
from app.core.database import get_db
from datetime import datetime

_API_URL = "https://xapiverse.com/api/terabox-pro"
_HEADER_KEY = "xAPIverse-Key"


async def _get_next_key() -> str | None:
    keys = await db.terabox_keys.find({"enabled": True}).sort("usage_count", 1).to_list(100)
    if not keys:
        return None
    key = keys[0]
    # Increment usage counter
    await db.terabox_keys.update_one(
        {"_id": key["_id"]},
        {"$inc": {"usage_count": 1}, "$set": {"last_used": datetime.utcnow()}}
    )
    return key["api_key"]


async def fetch(url: str):
    api_key = await _get_next_key()
    if not api_key:
        return None, "no_terabox_api_keys"

    try:
        r = requests.post(
            _API_URL,
            json={"url": url},
            headers={
                "Content-Type": "application/json",
                _HEADER_KEY: api_key,
            },
            timeout=30,
        )
    except requests.exceptions.Timeout:
        return None, "upstream_timeout"
    except requests.exceptions.RequestException as e:
        return None, f"upstream_error: {e}"

    try:
        data = r.json()
    except Exception:
        return None, "invalid_json"

    if r.status_code == 429:
        return None, "terabox_rate_limited"

    if r.status_code >= 400:
        msg = data.get("message") or data.get("error") or "upstream_error"
        return None, msg

    if data.get("status") != "success":
        return None, data.get("message", "unknown_error")

    return data, None
