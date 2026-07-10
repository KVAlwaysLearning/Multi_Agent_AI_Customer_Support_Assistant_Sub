"""
BUCKET: Agent Router.

Wiring is real: takes a real IntentResult, returns a real RouterDecision
naming which agent(s) to call. The ROUTING RULES are intentionally simple
placeholders. The one case worth keeping real from day one is the
multi-agent example from the project doc ("paid yesterday but still
locked" -> billing + technical), since that's the trickiest path to get
right later and is cheap to stub correctly now.
"""
from models.schemas import IntentResult, RouterDecision, IntentLabel
from core.trace import Trace

# --- BUCKET START: replace/extend this mapping with real routing logic ---
INTENT_TO_AGENT = {
    IntentLabel.billing: ["billing"],
    IntentLabel.refund: ["billing"],
    IntentLabel.technical: ["technical"],
    IntentLabel.product: ["product"],
    IntentLabel.complaint: ["complaint"],
    IntentLabel.faq: ["faq"],
}

CONFIDENCE_ESCALATION_THRESHOLD = 0.35


def route(intent_result: IntentResult, trace: Trace) -> RouterDecision:
    agents = INTENT_TO_AGENT.get(intent_result.intent, ["faq"])
    reason = f"intent={intent_result.intent.value} confidence={intent_result.confidence}"

    # Multi-agent example case from the project doc, kept as a real rule
    lowered = intent_result.raw_query.lower()
    if "paid" in lowered and ("locked" in lowered or "not working" in lowered):
        agents = ["billing", "technical"]
        reason = "multi-agent rule matched: payment + access issue"

    if intent_result.confidence < CONFIDENCE_ESCALATION_THRESHOLD:
        reason += " | low confidence, consider escalation"
    # --- BUCKET END ---

    decision = RouterDecision(agents=agents, reason=reason)
    trace.log("agent_router", {"agents": agents, "reason": reason})
    return decision
