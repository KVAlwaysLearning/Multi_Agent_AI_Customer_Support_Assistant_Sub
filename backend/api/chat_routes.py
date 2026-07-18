"""
This is the integration point. Every module from the blueprint gets
called here, in order, and every call is recorded in the Trace -
this endpoint IS the verification mechanism for "is everything wired
correctly", independent of whether any individual bucket's logic is real yet.
"""
import time
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from models.schemas import ChatRequest, ChatResponse, Message, ConversationHistory, ConversationSummary
from core.trace import Trace
from agents.intent_detection import detect_intent
from agents.router import route
from agents.aggregator import aggregate
from agents.billing import BillingAgent
from agents.technical import TechnicalAgent
from agents.product import ProductAgent
from agents.complaint import ComplaintAgent
from agents.faq import FAQAgent
from database import mongo
from api.auth_routes import get_current_user

router_api = APIRouter(tags=["chat"])

AGENT_REGISTRY = {
    "billing": BillingAgent(),
    "technical": TechnicalAgent(),
    "product": ProductAgent(),
    "complaint": ComplaintAgent(),
    "faq": FAQAgent(),
}


@router_api.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest, user_email: str = Depends(get_current_user)):
    if not mongo.is_owner_or_new(req.session_id, user_email):
        raise HTTPException(status_code=403, detail="This chat belongs to another account.")

    trace = Trace(session_id=req.session_id, message=req.message)

    # 1. Save user message
    mongo.append_message(req.session_id, role="user", text=req.message, user_email=user_email)
    trace.log("memory:save_user_message", {"session_id": req.session_id})

    # 2. Intent detection
    intent_result = detect_intent(req.message, trace)

    # 3. Routing
    decision = route(intent_result, trace)

    # 4. Invoke agent(s) with conversation history
    past_messages = mongo.get_messages(req.session_id)
    recent_history = past_messages[-6:] if len(past_messages) > 6 else past_messages

    agent_responses = []
    for agent_name in decision.agents:
        agent = AGENT_REGISTRY.get(agent_name)
        if agent is None:
            trace.log("error", {"missing_agent": agent_name})
            continue
        agent_responses.append(agent.handle(req.message, trace, history=recent_history))

    if not agent_responses:
        # Should not happen, but guarantees /chat never silently returns nothing
        agent_responses = [AGENT_REGISTRY["faq"].handle(req.message, trace)]

    # 5. Aggregate
    final_text = aggregate(agent_responses, trace)

    # 6. Save AI response
    mongo.append_message(
        req.session_id, role="ai", text=final_text,
        agent_used=",".join(decision.agents), user_email=user_email,
    )
    trace.log("memory:save_ai_message", {"session_id": req.session_id})

    return ChatResponse(
        response=final_text,
        agents_used=decision.agents,
        trace=trace.as_dict(),
    )


@router_api.get("/conversations", response_model=List[ConversationSummary])
def list_conversations(user_email: str = Depends(get_current_user)):
    """Sidebar data: every conversation this logged-in user has, across devices."""
    return mongo.list_conversations_for_user(user_email)


@router_api.get("/conversations/{session_id}", response_model=ConversationHistory)
def get_conversation(session_id: str, user_email: str = Depends(get_current_user)):
    if not mongo.is_owner_or_new(session_id, user_email):
        raise HTTPException(status_code=403, detail="This chat belongs to another account.")

    raw = mongo.get_messages(session_id)
    messages = [
        Message(role=m["role"], text=m["text"], agent_used=m.get("agent_used"), timestamp=m["timestamp"])
        for m in raw
    ]
    return ConversationHistory(session_id=session_id, messages=messages)
