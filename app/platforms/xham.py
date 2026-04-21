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

import re
import httpx
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urlunparse

_BASE = "https://xhamster45.desi"

_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

_XHAM_DOMAINS = [
    "xhamster.com", "xhamster1.desi", "xhamster2.desi", "xhamster3.desi",
    "xhamster4.desi", "xhamster45.desi", "xhamster.desi"
]

def _normalize_url(url: str) -> str:
    parsed = urlparse(url)
    clean = urlunparse((parsed.scheme, "xhamster45.desi", parsed.path, "", "", ""))
    return clean

def _fetch(url: str) -> str:
    try:
        with httpx.Client(headers=_HEADERS, follow_redirects=True, timeout=20) as client:
            r = client.get(url)
            return r.text
    except Exception:
        return ""

def search(query: str) -> tuple:
    try:
        url = f"{_BASE}/search/{query.replace(' ', '+')}"
        html = _fetch(url)

        if not html:
            return None, "failed_to_fetch"

        soup = BeautifulSoup(html, "html.parser")
        results = []
        seen = set()

        for a in soup.find_all("a", href=True):
            href = a["href"]
            if "/videos/" in href and href not in seen:
                seen.add(href)
                img = a.find("img")
                title = img["alt"] if img and img.get("alt") else "No title"
                thumb = img.get("src") if img else None
                full_url = _BASE + href if href.startswith("/") else href
                results.append({"title": title, "url": full_url, "thumb": thumb})

        return results[:10], None

    except Exception as e:
        return None, str(e)

def extract(video_url: str) -> tuple:
    try:
        video_url = _normalize_url(video_url)
        html = _fetch(video_url)

        if not html:
            return None, "failed_to_fetch"

        m = re.search(r"https://video[^\"]+_TPL_\.av1\.mp4\.m3u8", html)

        if not m:
            return None, "stream_not_found"

        template = m.group(0)
        qualities = ["144p", "240p", "480p", "720p", "1080p"]
        streams = {q: template.replace("_TPL_", q) for q in qualities}

        return {"type": "m3u8", "streams": streams}, None

    except Exception as e:
        return None, str(e)
