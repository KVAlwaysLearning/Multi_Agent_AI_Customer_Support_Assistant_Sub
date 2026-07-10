"""
BUCKET: Intent Detection Agent.

Wiring is real: this function is genuinely called by the chat pipeline,
genuinely returns a typed IntentResult, and genuinely calls the LLM layer.
The CLASSIFICATION LOGIC inside is a placeholder - a simple keyword match -
so the function is verifiable end-to-end before you write the real
classifier (rule-based, Banking77-trained model, or LLM-prompted).

To verify: send queries containing "refund", "password", "price", etc.
and confirm the trace shows the expected intent coming out.
"""
from models.schemas import IntentResult, IntentLabel
from core.llm import call_llm
from core.trace import Trace

KEYWORD_MAP = {
    IntentLabel.billing: ["bill", "payment", "subscription", "invoice", "charge"],
    IntentLabel.refund: ["refund", "money back", "cancel order"],
    IntentLabel.technical: ["login", "password", "error", "bug", "install", "crash"],
    IntentLabel.product: ["price", "feature", "compare", "available", "pricing"],
    IntentLabel.complaint: ["complaint", "angry", "disappointed", "unacceptable", "frustrated"],
    IntentLabel.faq: ["policy", "hours", "contact", "shipping", "warranty"],
}


def detect_intent(query: str, trace: Trace) -> IntentResult:
    # --- BUCKET START: replace this block with real classification logic ---
    lowered = query.lower()
    matched = IntentLabel.faq  # default fallback bucket
    confidence = 0.3
    for label, keywords in KEYWORD_MAP.items():
        if any(kw in lowered for kw in keywords):
            matched = label
            confidence = 0.6
            break

    # Demonstrates the LLM wiring is connected too (stub mode until GROQ_API_KEY is set)
    _ = call_llm(
        system_prompt="You are an intent classifier. (placeholder - not used to decide yet)",
        user_prompt=query,
        agent_name="intent_detection",
    )
    # --- BUCKET END ---

    result = IntentResult(intent=matched, confidence=confidence, raw_query=query)
    trace.log("intent_detection", {"intent": matched.value, "confidence": confidence})
    return result
