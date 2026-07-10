"""
Intent Detection Agent - uses Llama via Groq for real classification.
Falls back to keyword matching if LLM fails.
"""
import json
import logging
from models.schemas import IntentResult, IntentLabel
from core.llm import call_llm
from core.trace import Trace

logger = logging.getLogger("intent")

KEYWORD_MAP = {
    IntentLabel.billing: ["bill", "payment", "subscription", "invoice",
                          "charge", "charged", "pay", "paid"],
    IntentLabel.refund: ["refund", "money back", "cancel order", "return"],
    IntentLabel.technical: ["login", "password", "error", "bug", "install",
                            "crash", "not working", "locked", "access"],
    IntentLabel.product: ["price", "feature", "compare", "available",
                          "pricing", "cost", "plan", "upgrade"],
    IntentLabel.complaint: ["complaint", "angry", "disappointed",
                            "unacceptable", "frustrated", "terrible", "worst"],
    IntentLabel.faq: ["policy", "hours", "contact", "shipping",
                      "warranty", "how do i", "what is"],
}

SYSTEM_PROMPT = """You are an intent classifier for a customer support system.
Classify the customer message into exactly one of these intents:
- billing: payment issues, invoices, subscriptions, charges
- refund: refund requests, returns, money back
- technical: login problems, errors, installation, bugs, access issues
- product: product features, pricing, comparisons, availability
- complaint: complaints, dissatisfaction, angry customers
- faq: general questions, policies, shipping, warranty, contact info

Respond with ONLY a JSON object like this:
{"intent": "billing", "confidence": 0.95}

No other text. Just the JSON."""


def detect_intent(query: str, trace: Trace) -> IntentResult:
    # Try LLM classification first
    try:
        raw = call_llm(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=f"Customer message: {query}",
            agent_name="intent_detection"
        )
        # Parse JSON response
        raw = raw.strip()
        if raw.startswith("{"):
            parsed = json.loads(raw)
            intent_str = parsed.get("intent", "faq")
            confidence = float(parsed.get("confidence", 0.7))
            intent = IntentLabel(intent_str)
            result = IntentResult(intent=intent, confidence=confidence,
                                  raw_query=query)
            trace.log("intent_detection", {
                "intent": intent.value,
                "confidence": confidence,
                "method": "llm"
            })
            return result
    except Exception as e:
        logger.warning(f"LLM intent failed, using keywords: {e}")

    # Keyword fallback
    lowered = query.lower()
    matched = IntentLabel.faq
    confidence = 0.4
    for label, keywords in KEYWORD_MAP.items():
        if any(kw in lowered for kw in keywords):
            matched = label
            confidence = 0.65
            break

    result = IntentResult(intent=matched, confidence=confidence,
                          raw_query=query)
    trace.log("intent_detection", {
        "intent": matched.value,
        "confidence": confidence,
        "method": "keyword_fallback"
    })
    return result
