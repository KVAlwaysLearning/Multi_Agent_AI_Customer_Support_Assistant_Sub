"""
Database layer with Mongo + in-memory fallback.
"""
import time
import logging
from core.config import settings

logger = logging.getLogger("database")

_in_memory_users = {}
_in_memory_conversations = {}  # session_id -> {"user_email":..., "messages":[...], "updated_at":...}
_mongo_client = None
_db = None

if settings.MONGO_URI:
    try:
        from pymongo import MongoClient
        _mongo_client = MongoClient(
            settings.MONGO_URI,
            tls=True,
            tlsAllowInvalidCertificates=True,
            serverSelectionTimeoutMS=10000,
        )
        _db = _mongo_client[settings.MONGO_DB_NAME]
        _db.command("ping")
        logger.info("[DB] Connected to MongoDB.")
    except Exception as e:
        logger.error(f"[DB] Mongo failed, using in-memory: {e}")
        _db = None
else:
    logger.info("[DB] No MONGO_URI - using in-memory store.")


def is_using_mongo():
    return _db is not None


def create_user(email: str, hashed_password: str, name: str) -> dict:
    user = {"email": email, "hashed_password": hashed_password,
            "name": name, "created_at": time.time()}
    if is_using_mongo():
        _db.users.insert_one(user)
    else:
        _in_memory_users[email] = user
    return user


def get_user_by_email(email: str):
    if is_using_mongo():
        return _db.users.find_one({"email": email})
    return _in_memory_users.get(email)


def append_message(session_id: str, role: str, text: str,
                    agent_used: str = None, user_email: str = None) -> None:
    message = {"role": role, "text": text,
               "agent_used": agent_used, "timestamp": time.time()}
    now = time.time()
    if is_using_mongo():
        _db.conversations.update_one(
            {"session_id": session_id},
            {
                "$push": {"messages": message},
                "$set": {"updated_at": now},
                "$setOnInsert": {"session_id": session_id, "user_email": user_email},
            },
            upsert=True,
        )
    else:
        conv = _in_memory_conversations.setdefault(
            session_id, {"user_email": user_email, "messages": [], "updated_at": now}
        )
        conv["messages"].append(message)
        conv["updated_at"] = now


def get_messages(session_id: str) -> list:
    if is_using_mongo():
        doc = _db.conversations.find_one({"session_id": session_id})
        return doc["messages"] if doc else []
    conv = _in_memory_conversations.get(session_id)
    return conv["messages"] if conv else []


def is_owner_or_new(session_id: str, user_email: str) -> bool:
    """True if the session doesn't exist yet (nobody owns it), or if it
    belongs to this user. False if it belongs to someone else."""
    if is_using_mongo():
        doc = _db.conversations.find_one({"session_id": session_id}, {"user_email": 1})
        return doc is None or doc.get("user_email") == user_email
    conv = _in_memory_conversations.get(session_id)
    return conv is None or conv.get("user_email") == user_email


def list_conversations_for_user(user_email: str) -> list:
    """Summary list for the sidebar: one entry per conversation this user owns."""
    def _summarize(session_id, msgs, updated_at):
        first_user_msg = next((m["text"] for m in msgs if m["role"] == "user"), "New conversation")
        title = first_user_msg[:40] + ("..." if len(first_user_msg) > 40 else "")
        return {
            "session_id": session_id,
            "title": title,
            "updated_at": updated_at,
            "message_count": len(msgs),
        }

    if is_using_mongo():
        docs = _db.conversations.find(
            {"user_email": user_email},
            {"_id": 0, "session_id": 1, "messages": 1, "updated_at": 1},
        ).sort("updated_at", -1)
        return [_summarize(d["session_id"], d.get("messages", []), d.get("updated_at", 0)) for d in docs]

    result = [
        _summarize(session_id, conv.get("messages", []), conv.get("updated_at", 0))
        for session_id, conv in _in_memory_conversations.items()
        if conv.get("user_email") == user_email
    ]
    result.sort(key=lambda c: c["updated_at"], reverse=True)
    return result


def get_all_conversations() -> list:
    if is_using_mongo():
        return list(_db.conversations.find({}, {"_id": 0}))
    return [
        {"session_id": sid, "user_email": conv.get("user_email"), "messages": conv["messages"]}
        for sid, conv in _in_memory_conversations.items()
    ]


def get_stats() -> dict:
    if is_using_mongo():
        total = _db.conversations.count_documents({})
        pipeline = [
            {"$unwind": "$messages"},
            {"$match": {"messages.role": "ai", "messages.agent_used": {"$ne": None}}},
            {"$group": {"_id": "$messages.agent_used", "count": {"$sum": 1}}}
        ]
        agent_usage = {doc["_id"]: doc["count"]
                       for doc in _db.conversations.aggregate(pipeline)}
        return {"total_conversations": total, "agent_usage": agent_usage}
    total = len(_in_memory_conversations)
    agent_usage = {}
    for conv in _in_memory_conversations.values():
        for m in conv["messages"]:
            if m.get("agent_used"):
                for a in m["agent_used"].split(","):
                    agent_usage[a.strip()] = agent_usage.get(a.strip(), 0) + 1
    return {"total_conversations": total, "agent_usage": agent_usage}
