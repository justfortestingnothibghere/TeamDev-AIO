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

import re
import requests
import logging

logger = logging.getLogger("hcity")

_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Referer": "https://www.hentaicity.com",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

def fetch(url: str) -> tuple:
    logger.info(f"[hcity] fetch called with url={url}")

    if not url.startswith("http"):
        logger.warning("[hcity] invalid_url")
        return None, "invalid_url"

    try:
        logger.info("[hcity] sending GET request...")
        r = requests.get(url, headers=_HEADERS, timeout=20)
        logger.info(f"[hcity] response status={r.status_code}, content-length={len(r.text)}")

        if r.status_code != 200:
            logger.error(f"[hcity] non-200 status: {r.status_code}")
            return None, f"http_{r.status_code}"

        html = r.text

        logger.debug(f"[hcity] html snippet (first 500 chars): {html[:500]}")

        title = ""
        m = re.search(r"<title>(.*?)</title>", html)
        if m:
            title = m.group(1).strip()
            logger.info(f"[hcity] title found: {title}")
        else:
            logger.warning("[hcity] no <title> tag found")

        thumbnail = ""
        m = re.search(r'property="og:image" content="([^"]+)"', html)
        if m:
            thumbnail = m.group(1)
            logger.info(f"[hcity] thumbnail found: {thumbnail}")
        else:
            logger.warning("[hcity] no og:image found")

        trailer = ""
        m = re.search(r'https://[^"]+\.mp4', html)
        if m:
            trailer = m.group(0)
            logger.info(f"[hcity] trailer/mp4 found: {trailer}")
        else:
            logger.warning("[hcity] no .mp4 url found in html")

        m3u8 = ""
        m = re.search(r'https://[^"]+\.m3u8[^"]*', html)
        if m:
            m3u8 = m.group(0)
            logger.info(f"[hcity] m3u8 found: {m3u8}")
        else:
            logger.warning("[hcity] no .m3u8 url found in html — dumping all script tags for inspection")

            scripts = re.findall(r'<script[^>]*>(.*?)</script>', html, re.DOTALL)
            for i, s in enumerate(scripts):
                if any(kw in s for kw in ["source", "file", "stream", "video", "player", "m3u8", "mp4", "hls"]):
                    logger.warning(f"[hcity] script[{i}] (relevant): {s[:800]}")
            return None, "stream_not_found"

        return {
            "title": title,
            "thumbnail": thumbnail,
            "trailer": trailer,
            "m3u8": m3u8,
        }, None

    except Exception as e:
        logger.exception(f"[hcity] exception: {e}")
        return None, str(e)
