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


from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from jose import JWTError
from app.core.database import get_db, get_setting, set_setting
from app.core.security import generate_api_key, decode_token, hash_password

router = APIRouter(tags=["Admin"])
templates = Jinja2Templates(directory="templates")

async def require_admin(request: Request):
    token = request.cookies.get("td_token") or request.headers.get("Authorization", "").replace("Bearer ", "")
    if not token:
        raise HTTPException(status_code=401, detail="not_authenticated")
    try:
        payload = decode_token(token)
        if payload.get("role") != "admin":
            raise HTTPException(status_code=403, detail="forbidden")
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="invalid_token")

@router.get("/", response_class=HTMLResponse)
async def admin_panel(request: Request):
    token = request.cookies.get("td_token")
    if not token:
        return RedirectResponse("/admin/login")
    try:
        decode_token(token)
    except Exception:
        return RedirectResponse("/admin/login")
    return templates.TemplateResponse("admin.html", {"request": request})

@router.get("/login", response_class=HTMLResponse)
async def admin_login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/logout")
async def logout():
    r = RedirectResponse("/admin/login", status_code=302)
    r.delete_cookie("td_token")
    return r

class CreateKeyRequest(BaseModel):
    owner: str
    label: Optional[str] = ""
    requests_per_window: Optional[int] = 60
    window_seconds: Optional[int] = 60
    expires_at: Optional[str] = None

@router.get("/api/keys")
async def list_keys(admin=Depends(require_admin)):
    db = get_db()
    keys = await db.api_keys.find().sort("created_at", -1).to_list(200)
    for k in keys:
        k["_id"] = str(k["_id"])
        if k.get("expires_at"):
            k["expires_at"] = k["expires_at"].isoformat()
        if k.get("last_used"):
            k["last_used"] = k["last_used"].isoformat()
        if k.get("created_at"):
            k["created_at"] = k["created_at"].isoformat()
    return {"keys": keys}

@router.post("/api/keys")
async def create_key(body: CreateKeyRequest, admin=Depends(require_admin)):
    db = get_db()
    key = generate_api_key()
    expires = None
    if body.expires_at:
        expires = datetime.fromisoformat(body.expires_at)

    doc = {
        "key": key,
        "owner": body.owner,
        "label": body.label,
        "enabled": True,
        "usage_count": 0,
        "requests_per_window": body.requests_per_window,
        "window_seconds": body.window_seconds,
        "expires_at": expires,
        "last_used": None,
        "created_at": datetime.utcnow()
    }
    await db.api_keys.insert_one(doc)

    await db.rate_configs.update_one(
        {"scope": f"key:{key}"},
        {"$set": {"requests": body.requests_per_window, "window": body.window_seconds}},
        upsert=True
    )

    return {"success": True, "key": key, "owner": body.owner}

@router.patch("/api/keys/{key}/toggle")
async def toggle_key(key: str, admin=Depends(require_admin)):
    db = get_db()
    rec = await db.api_keys.find_one({"key": key})
    if not rec:
        raise HTTPException(status_code=404, detail="key_not_found")
    new_state = not rec.get("enabled", True)
    await db.api_keys.update_one({"key": key}, {"$set": {"enabled": new_state}})
    return {"key": key, "enabled": new_state}

@router.delete("/api/keys/{key}")
async def delete_key(key: str, admin=Depends(require_admin)):
    db = get_db()
    await db.api_keys.delete_one({"key": key})
    await db.rate_configs.delete_one({"scope": f"key:{key}"})
    return {"deleted": True}

class BanRequest(BaseModel):
    ip: str
    reason: Optional[str] = "Policy violation"

@router.get("/api/bans")
async def list_bans(admin=Depends(require_admin)):
    db = get_db()
    bans = await db.banned_ips.find().sort("banned_at", -1).to_list(500)
    for b in bans:
        b["_id"] = str(b["_id"])
        if b.get("banned_at"):
            b["banned_at"] = b["banned_at"].isoformat()
    return {"bans": bans}

@router.post("/api/bans")
async def ban_ip(body: BanRequest, admin=Depends(require_admin)):
    db = get_db()
    await db.banned_ips.update_one(
        {"ip": body.ip},
        {"$set": {"ip": body.ip, "reason": body.reason, "active": True, "banned_at": datetime.utcnow()}},
        upsert=True
    )
    return {"banned": True, "ip": body.ip}

@router.delete("/api/bans/{ip}")
async def unban_ip(ip: str, admin=Depends(require_admin)):
    db = get_db()
    await db.banned_ips.update_one({"ip": ip}, {"$set": {"active": False}})
    return {"unbanned": True, "ip": ip}

class RateConfigRequest(BaseModel):
    scope: str
    requests: int
    window: int

@router.get("/api/rate-configs")
async def list_rate_configs(admin=Depends(require_admin)):
    db = get_db()
    cfgs = await db.rate_configs.find().to_list(200)
    for c in cfgs:
        c["_id"] = str(c["_id"])
    return {"configs": cfgs}

@router.post("/api/rate-configs")
async def upsert_rate_config(body: RateConfigRequest, admin=Depends(require_admin)):
    db = get_db()
    await db.rate_configs.update_one(
        {"scope": body.scope},
        {"$set": {"requests": body.requests, "window": body.window}},
        upsert=True
    )
    return {"success": True, "scope": body.scope}

@router.delete("/api/rate-configs/{scope:path}")
async def delete_rate_config(scope: str, admin=Depends(require_admin)):
    db = get_db()
    await db.rate_configs.delete_one({"scope": scope})
    return {"deleted": True}

@router.get("/api/analytics")
async def analytics(admin=Depends(require_admin)):
    db = get_db()

    total_keys = await db.api_keys.count_documents({})
    active_keys = await db.api_keys.count_documents({"enabled": True})
    total_bans = await db.banned_ips.count_documents({"active": True})
    total_requests = await db.request_logs.count_documents({})

    pipeline_status = [
        {"$group": {"_id": "$status", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    status_dist = await db.request_logs.aggregate(pipeline_status).to_list(20)

    pipeline_top_keys = [
        {"$match": {"api_key": {"$ne": None}}},
        {"$group": {"_id": "$api_key", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 10}
    ]
    top_keys = await db.request_logs.aggregate(pipeline_top_keys).to_list(10)

    pipeline_top_ips = [
        {"$group": {"_id": "$ip", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 10}
    ]
    top_ips = await db.request_logs.aggregate(pipeline_top_ips).to_list(10)

    pipeline_hourly = [
        {"$group": {
            "_id": {
                "hour": {"$hour": "$ts"},
                "day": {"$dayOfMonth": "$ts"}
            },
            "count": {"$sum": 1}
        }},
        {"$sort": {"_id.day": 1, "_id.hour": 1}},
        {"$limit": 48}
    ]
    hourly = await db.request_logs.aggregate(pipeline_hourly).to_list(48)

    recent_logs = await db.request_logs.find().sort("ts", -1).limit(50).to_list(50)
    for log in recent_logs:
        log["_id"] = str(log["_id"])
        if log.get("ts"):
            log["ts"] = log["ts"].isoformat()

    return {
        "summary": {
            "total_keys": total_keys,
            "active_keys": active_keys,
            "total_bans": total_bans,
            "total_requests": total_requests
        },
        "status_distribution": [{"status": s["_id"], "count": s["count"]} for s in status_dist],
        "top_keys": [{"key": k["_id"], "count": k["count"]} for k in top_keys],
        "top_ips": [{"ip": i["_id"], "count": i["count"]} for i in top_ips],
        "hourly_traffic": [{"hour": h["_id"]["hour"], "count": h["count"]} for h in hourly],
        "recent_logs": recent_logs
    }

@router.post("/api/change-password")
async def change_password(request: Request, admin=Depends(require_admin)):
    body = await request.json()
    new_pw = body.get("password", "")
    if len(new_pw) < 8:
        raise HTTPException(status_code=400, detail="password_too_short")
    db = get_db()
    await db.admins.update_one(
        {"username": admin["sub"]},
        {"$set": {"password": hash_password(new_pw)}}
    )
    return {"success": True}

@router.get("/api/settings")
async def get_settings(admin=Depends(require_admin)):
    enforcement = await get_setting("api_enforcement", True)
    return {
        "api_enforcement": enforcement,
    }

@router.post("/api/settings/enforcement")
async def toggle_enforcement(request: Request, admin=Depends(require_admin)):
    body = await request.json()
    enabled = bool(body.get("enabled", True))
    await set_setting("api_enforcement", enabled)
    return {"api_enforcement": enabled}


# ── TeraBox API Key Management ────────────────────────────────────────────────

class TeraboxKeyRequest(BaseModel):
    api_key: str
    label: Optional[str] = ""

@router.get("/api/terabox-keys")
async def list_terabox_keys(admin=Depends(require_admin)):
    db = get_db()
    keys = await db.terabox_keys.find().sort("created_at", -1).to_list(200)
    for k in keys:
        k["_id"] = str(k["_id"])
        if k.get("created_at"):
            k["created_at"] = k["created_at"].isoformat()
        if k.get("last_used"):
            k["last_used"] = k["last_used"].isoformat()
        raw = k.get("api_key", "")
        k["api_key_masked"] = raw[:8] + "..." + raw[-4:] if len(raw) > 12 else raw
    return {"keys": keys}

@router.post("/api/terabox-keys")
async def add_terabox_key(body: TeraboxKeyRequest, admin=Depends(require_admin)):
    db = get_db()
    existing = await db.terabox_keys.find_one({"api_key": body.api_key})
    if existing:
        raise HTTPException(status_code=409, detail="key_already_exists")
    doc = {
        "api_key": body.api_key,
        "label": body.label,
        "enabled": True,
        "usage_count": 0,
        "last_used": None,
        "created_at": datetime.utcnow(),
    }
    await db.terabox_keys.insert_one(doc)
    return {"success": True, "label": body.label}

@router.patch("/api/terabox-keys/{key_id}/toggle")
async def toggle_terabox_key(key_id: str, admin=Depends(require_admin)):
    from bson import ObjectId
    db = get_db()
    rec = await db.terabox_keys.find_one({"_id": ObjectId(key_id)})
    if not rec:
        raise HTTPException(status_code=404, detail="key_not_found")
    new_state = not rec.get("enabled", True)
    await db.terabox_keys.update_one({"_id": ObjectId(key_id)}, {"$set": {"enabled": new_state}})
    return {"enabled": new_state}

@router.delete("/api/terabox-keys/{key_id}")
async def delete_terabox_key(key_id: str, admin=Depends(require_admin)):
    from bson import ObjectId
    db = get_db()
    await db.terabox_keys.delete_one({"_id": ObjectId(key_id)})
    return {"deleted": True}
