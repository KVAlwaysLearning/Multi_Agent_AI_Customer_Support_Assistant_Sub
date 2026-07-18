"""
Every module boundary in this system speaks one of these schemas.
This is intentional: if a module's input/output doesn't match these,
FastAPI/Pydantic raises immediately instead of silently passing bad
data downstream - this is the main mechanism for catching integration
bugs early (see Trace for the runtime view of the same thing).
"""
from pydantic import BaseModel
from typing import List, Optional
from enum import Enum


class IntentLabel(str, Enum):
    billing = "billing"
    refund = "refund"
    technical = "technical"
    product = "product"
    complaint = "complaint"
    faq = "faq"


class IntentResult(BaseModel):
    intent: IntentLabel
    confidence: float
    raw_query: str


class RouterDecision(BaseModel):
    agents: List[str]  # one or more agent names to invoke
    reason: str


class RetrievedChunk(BaseModel):
    text: str
    source_document: str
    score: float


class AgentResponse(BaseModel):
    agent_name: str
    answer: str
    used_chunks: List[RetrievedChunk] = []
    confidence: float = 0.0


class ChatRequest(BaseModel):
    session_id: str
    message: str


class ChatResponse(BaseModel):
    response: str
    agents_used: List[str]
    trace: dict  # full pipeline trace, see core/trace.py


class Message(BaseModel):
    role: str  # "user" | "ai"
    text: str
    agent_used: Optional[str] = None
    timestamp: float


class ConversationHistory(BaseModel):
    session_id: str
    messages: List[Message]


class ConversationSummary(BaseModel):
    session_id: str
    title: str
    updated_at: float
    message_count: int


class RegisterRequest(BaseModel):
    email: str
    password: str
    name: str


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
