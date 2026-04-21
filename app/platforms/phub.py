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
import yt_dlp
import logging

logger = logging.getLogger("phub")

def get_info(url: str, proxy_url: str = None) -> dict:
    logger.info(f"[phub] get_info called with url={url}")

    original_url = url
    url = re.sub(r'pornhub\.com', 'pornhub.org', url)
    if url != original_url:
        logger.info(f"[phub] rewrote URL to .org mirror: {url}")

    ydl_opts = {
        'quiet': False,
        'verbose': True,
        'extract_flat': False,
        'nocheckcertificate': True,
        'logger': _YtdlpLogger(),
    }
    if proxy_url:
        ydl_opts['proxy'] = proxy_url
        logger.info(f"[phub] using proxy: {proxy_url}")

    try:
        logger.info("[phub] starting yt-dlp extraction...")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            data = ydl.extract_info(url, download=False)

            if not data:
                logger.error("[phub] yt-dlp returned no data")
                return None, "extraction_failed"

            logger.info(f"[phub] extraction success: title={data.get('title')}, formats={len(data.get('formats', []))}")

            formats = []
            for fmt in data.get('formats', []):
                if fmt.get('height') and fmt.get('url'):
                    formats.append({
                        'height': fmt.get('height'),
                        'url': fmt.get('url'),
                        'ext': fmt.get('ext', 'mp4'),
                        'format_id': fmt.get('format_id'),
                    })
                    logger.debug(f"[phub] format: {fmt.get('format_id')} {fmt.get('height')}p")

            if not formats:
                logger.warning("[phub] no usable formats found (no height+url combos)")

            return {
                'title': data.get('title', 'Video'),
                'thumbnail': data.get('thumbnail'),
                'duration': data.get('duration'),
                'formats': formats,
            }, None

    except yt_dlp.utils.DownloadError as e:
        logger.error(f"[phub] yt-dlp DownloadError: {e}")
        return None, str(e)
    except Exception as e:
        logger.exception(f"[phub] unexpected exception: {e}")
        return None, str(e)

class _YtdlpLogger:
    
    def debug(self, msg):
        if msg.startswith('[debug]'):
            logger.debug(f"[phub][yt-dlp] {msg}")
        else:
            logger.info(f"[phub][yt-dlp] {msg}")

    def info(self, msg):
        logger.info(f"[phub][yt-dlp] {msg}")

    def warning(self, msg):
        logger.warning(f"[phub][yt-dlp] {msg}")

    def error(self, msg):
        logger.error(f"[phub][yt-dlp] {msg}")
