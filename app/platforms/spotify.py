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

# This Will Not Work On Railway Deploy The Project On Your VPS 

import asyncio
from concurrent.futures import ThreadPoolExecutor
from camoufox.sync_api import Camoufox

_executor = ThreadPoolExecutor(max_workers=3)

def _is_valid_spotify(url: str) -> bool:
    return "open.spotify.com/track/" in url

def _sync_fetch(url: str) -> tuple:
    try:
        with Camoufox(headless=True, geoip=True) as browser:
            page = browser.new_page()

            page.goto("https://spotidown.app/", timeout=60000)

            page.fill('input[name="url"]', url)
            page.click('#send')

            page.wait_for_selector('form[name="submitspurl"]', timeout=60000)

            title = ""
            artist = ""
            thumbnail = ""
            try:
                title = page.locator("h3").first.inner_text()
            except Exception:
                pass
            try:
                artist = page.text_content(".music-info p") or ""
            except Exception:
                pass
            try:
                thumbnail = page.get_attribute(".music-info img", "src") or ""
            except Exception:
                pass

            page.click('form[name="submitspurl"] button')

            page.wait_for_selector('a[href*="rapid.spotidown"]', timeout=60000)

            download_url = page.get_attribute('a[href*="rapid.spotidown"]', 'href')

            if not download_url:
                return None, "download_link_not_found"

            return {
                "download_url": download_url,
                "title": title.strip(),
                "artist": artist.strip(),
                "thumbnail": thumbnail.strip(),
            }, None

    except Exception as e:
        return None, str(e)

async def fetch(url: str) -> tuple:
    if not _is_valid_spotify(url):
        return None, "invalid_spotify_url"

    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(_executor, _sync_fetch, url)
