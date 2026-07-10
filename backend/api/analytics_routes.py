"""
Analytics and escalation endpoints.
"""
from fastapi import APIRouter
from database import mongo

router = APIRouter(tags=["analytics"])


@router.get("/analytics/stats")
def get_stats():
    return mongo.get_stats()


@router.get("/analytics/conversations")
def get_conversations():
    convos = mongo.get_all_conversations()
    return {"total": len(convos), "conversations": convos[:50]}


@router.post("/escalation/ticket")
def create_ticket(data: dict):
    """Create a support ticket for escalated issues."""
    import time
    ticket = {
        "session_id": data.get("session_id"),
        "issue": data.get("issue"),
        "priority": data.get("priority", "normal"),
        "created_at": time.time(),
        "status": "open"
    }
    if mongo.is_using_mongo():
        from database.mongo import _db
        _db.tickets.insert_one(ticket)
    return {"status": "ticket_created", "ticket": ticket}
