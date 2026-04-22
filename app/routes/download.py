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


from fastapi import APIRouter, Depends, HTTPException, Query
from app.core.deps import require_api_key
from app.platforms import aio, phub, hcity, xham, spotify, terabox

router = APIRouter(tags=["Download"])

@router.get("/dl")
async def dl(
    url: str = Query(..., description="Media URL"),
    api: str = Query(None, description="API key"),
    key_record=Depends(require_api_key)
):
    if not url.startswith("http"):
        raise HTTPException(status_code=400, detail={"error": "invalid_url"})

    data, err = aio.fetch(url)
    if err:
        code = 503 if err == "retry_required" else 422
        raise HTTPException(status_code=code, detail={"error": err})

    return {
        "success": True,
        "source": data.get("source"),
        "title": data.get("title"),
        "author": data.get("author"),
        "thumbnail": data.get("thumbnail"),
        "duration": data.get("duration"),
        "medias": data.get("medias", []),
        "type": data.get("type"),
        "stats": data.get("stats"),
    }

@router.get("/phub")
async def phub_dl(
    url: str = Query(..., description="PornHub video URL"),
    api: str = Query(None, description="API key"),
    key_record=Depends(require_api_key)
):
    if not url.startswith("http"):
        raise HTTPException(status_code=400, detail={"error": "invalid_url"})

    data, err = phub.get_info(url)
    if err:
        raise HTTPException(status_code=422, detail={"error": err})

    return {
        "success": True,
        "source": "pornhub",
        "title": data.get("title"),
        "thumbnail": data.get("thumbnail"),
        "duration": data.get("duration"),
        "formats": data.get("formats", []),
    }

@router.get("/hcity")
async def hcity_dl(
    url: str = Query(..., description="HentaiCity video URL"),
    api: str = Query(None, description="API key"),
    key_record=Depends(require_api_key)
):
    if not url.startswith("http"):
        raise HTTPException(status_code=400, detail={"error": "invalid_url"})

    data, err = hcity.fetch(url)
    if err:
        raise HTTPException(status_code=422, detail={"error": err})

    return {
        "success": True,
        "source": "hentaicity",
        "title": data.get("title"),
        "thumbnail": data.get("thumbnail"),
        "trailer": data.get("trailer"),
        "m3u8": data.get("m3u8"),
    }

@router.get("/xham")
async def xham_dl(
    url: str = Query(..., description="XHamster video URL"),
    api: str = Query(None, description="API key"),
    key_record=Depends(require_api_key)
):
    if not url.startswith("http"):
        raise HTTPException(status_code=400, detail={"error": "invalid_url"})

    data, err = xham.extract(url)
    if err:
        raise HTTPException(status_code=422, detail={"error": err})

    return {
        "success": True,
        "source": "xhamster",
        "type": data.get("type"),
        "streams": data.get("streams", {}),
    }

@router.get("/xham/search")
async def xham_search(
    q: str = Query(..., description="Search query"),
    api: str = Query(None, description="API key"),
    key_record=Depends(require_api_key)
):
    results, err = xham.search(q)
    if err:
        raise HTTPException(status_code=422, detail={"error": err})

    return {
        "success": True,
        "source": "xhamster",
        "query": q,
        "results": results,
    }

@router.get("/s")
async def spotify_dl(
    url: str = Query(..., description="Spotify track URL"),
    api: str = Query(None, description="API key"),
    key_record=Depends(require_api_key)
):
    if not url.startswith("http"):
        raise HTTPException(status_code=400, detail={"error": "invalid_url"})

    data, err = await spotify.fetch(url)
    if err:
        raise HTTPException(status_code=422, detail={"error": err})

    return {
        "success": True,
        "source": "spotify",
        "title": data.get("title"),
        "artist": data.get("artist"),
        "thumbnail": data.get("thumbnail"),
        "download_url": data.get("download_url"),
    }

@router.get("/tb")
async def terabox_dl(
    url: str = Query(..., description="TeraBox share URL"),
    api_key: str = Query(None, description="API key (optional)"),
    key_record=Depends(require_api_key)
):
    """
    Fetch TeraBox file info.
    Usage: /api/v1/tb?url=https://1024terabox.com/s/xxx&api_key=td...
    """
    if not url.startswith("http"):
        raise HTTPException(status_code=400, detail={"error": "invalid_url"})

    data, err = await terabox.fetch(url)
    if err:
        if err == "no_terabox_api_keys":
            raise HTTPException(status_code=503, detail={"error": err, "msg": "No TeraBox API keys configured. Add them in the admin panel."})
        if err == "terabox_rate_limited":
            raise HTTPException(status_code=429, detail={"error": err, "msg": "All TeraBox API keys are rate-limited. Try again later."})
        raise HTTPException(status_code=422, detail={"error": err})

    return {
        "success": True,
        "source": "terabox",
        "total_files": data.get("total_files"),
        "list": data.get("list", []),
        "free_credits_remaining": data.get("free_credits_remaining"),
    }
  
