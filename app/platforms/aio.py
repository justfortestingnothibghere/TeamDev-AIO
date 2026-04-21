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

import requests as _requests

_EP = "https://downr.org/.netlify/functions"

_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Origin": "https://downr.org",
    "Referer": "https://downr.org/",
    "Accept": "application/json, text/plain, */*",
    "Content-Type": "application/json"
}

def clean_url(url: str) -> str:
    if "?" in url:
        url = url.split("?")[0]
    if not url.endswith("/"):
        url += "/"
    return url

def fetch(url: str):
    url = clean_url(url)
    s = _requests.Session()
    try:
        try:
            s.get(f"{_EP}/analytics", headers=_HEADERS, timeout=5)
        except Exception:
            pass

        r = s.post(
            f"{_EP}/nyt",
            json={"url": url},
            headers=_HEADERS,
            timeout=30
        )

        try:
            data = r.json()
        except Exception:
            return None, "invalid_json"

        if data.get("error") == "user_retry_required":
            return None, "retry_required"

        medias = data.get("medias", [])
        if not medias:
            return None, "no_media_found"

        return data, None
    finally:
        s.close()
