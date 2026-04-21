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

import os
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime

MONGO_URI = os.getenv("MONGO_URI", "ADD INVOIRMENTS VARIABLE")
DB_NAME = os.getenv("DB_NAME", "teamdev_aio")

client: AsyncIOMotorClient = None
db = None

async def init_db():
    global client, db
    client = AsyncIOMotorClient(MONGO_URI)
    db = client[DB_NAME]
    await _ensure_indexes()
    await _seed_admin()

async def _ensure_indexes():
    await db.api_keys.create_index("key", unique=True)
    await db.api_keys.create_index("owner")
    await db.banned_ips.create_index("ip", unique=True)
    await db.request_logs.create_index("ts")
    await db.request_logs.create_index("ip")
    await db.request_logs.create_index("api_key")
    await db.rate_configs.create_index("scope", unique=True)
    await db.admins.create_index("username", unique=True)
    await db.settings.create_index("key", unique=True)

async def _seed_admin():
    from app.core.security import hash_password
    existing = await db.admins.find_one({"username": "admin"})
    if not existing:
        await db.admins.insert_one({
            "username": "admin",
            "password": hash_password("TeamDev@2026"),
            "created_at": datetime.utcnow()
        })
    await db.settings.update_one(
        {"key": "api_enforcement"},
        {"$setOnInsert": {"key": "api_enforcement", "value": True}},
        upsert=True
    )

async def get_setting(key: str, default=None):
    doc = await db.settings.find_one({"key": key})
    if doc:
        return doc["value"]
    return default

async def set_setting(key: str, value):
    await db.settings.update_one(
        {"key": key},
        {"$set": {"key": key, "value": value}},
        upsert=True
    )

def get_db():
    return db
