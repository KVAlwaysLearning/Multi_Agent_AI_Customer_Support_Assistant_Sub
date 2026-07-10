"""
Database layer with Mongo + in-memory fallback.
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
                   agent_used: str = None) -> None:
    message = {"role": role, "text": text,
               "agent_used": agent_used, "timestamp": time.time()}
    if is_using_mongo():
        _db.conversations.update_one(
            {"session_id": session_id},
            {"$push": {"messages": message},
             "$setOnInsert": {"session_id": session_id}},
            upsert=True,
        )
    else:
        _in_memory_conversations.setdefault(session_id, []).append(message)


def get_messages(session_id: str) -> list:
    if is_using_mongo():
        doc = _db.conversations.find_one({"session_id": session_id})
        return doc["messages"] if doc else []
    return _in_memory_conversations.get(session_id, [])


def get_all_conversations() -> list:
    if is_using_mongo():
        return list(_db.conversations.find({}, {"_id": 0}))
    return list(_in_memory_conversations.items())


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
    for msgs in _in_memory_conversations.values():
        for m in msgs:
            if m.get("agent_used"):
                for a in m["agent_used"].split(","):
                    agent_usage[a.strip()] = agent_usage.get(a.strip(), 0) + 1
    return {"total_conversations": total, "agent_usage": agent_usage}
