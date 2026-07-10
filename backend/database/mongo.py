"""
Real Mongo wiring, but falls back to an in-memory dict if MONGO_URI is
unset. This means the whole app runs and is verifiable on day one
without needing a Mongo Atlas cluster yet - swap in MONGO_URI later
and nothing else changes.
"""
import time
import logging
from core.config import settings

logger = logging.getLogger("database")

_in_memory_users = {}
_in_memory_conversations = {}

_mongo_client = None
_db = None

if settings.MONGO_URI:
    try:
        from pymongo import MongoClient
        _mongo_client = MongoClient(settings.MONGO_URI)
        _db = _mongo_client[settings.MONGO_DB_NAME]
        logger.info("[DB] Connected to MongoDB.")
    except Exception as e:
        logger.error(f"[DB] Failed to connect to Mongo, falling back to in-memory store: {e}")
        _db = None
else:
    logger.info("[DB] MONGO_URI not set - using in-memory store (data resets on restart).")


def is_using_mongo() -> bool:
    return _db is not None


# ---------- Users ----------
def create_user(email: str, hashed_password: str, name: str) -> dict:
    user = {"email": email, "hashed_password": hashed_password, "name": name, "created_at": time.time()}
    if is_using_mongo():
        _db.users.insert_one(user)
    else:
        _in_memory_users[email] = user
    return user


def get_user_by_email(email: str) -> dict | None:
    if is_using_mongo():
        return _db.users.find_one({"email": email})
    return _in_memory_users.get(email)


# ---------- Conversations ----------
def append_message(session_id: str, role: str, text: str, agent_used: str | None = None) -> None:
    message = {"role": role, "text": text, "agent_used": agent_used, "timestamp": time.time()}
    if is_using_mongo():
        _db.conversations.update_one(
            {"session_id": session_id},
            {"$push": {"messages": message}, "$setOnInsert": {"session_id": session_id}},
            upsert=True,
        )
    else:
        _in_memory_conversations.setdefault(session_id, []).append(message)


def get_messages(session_id: str) -> list:
    if is_using_mongo():
        doc = _db.conversations.find_one({"session_id": session_id})
        return doc["messages"] if doc else []
    return _in_memory_conversations.get(session_id, [])
