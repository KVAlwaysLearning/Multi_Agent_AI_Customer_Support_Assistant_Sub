"""
BUCKET: FAQ Agent.
Handles: company policies, general questions, contact info.
This is the best agent to fully implement FIRST (per the build plan) -
it has no complex routing logic, just RAG + LLM, so it's the cleanest
end-to-end RAG validation path.
"""
from agents.base_agent import BaseAgent


class FAQAgent(BaseAgent):
    name = "faq"
    system_prompt = (
        "You are the FAQ agent for TechMart Electronics. "
        "You answer general questions about company policy, shipping, and contact info. "
        "Always base your answer on the provided context; say you're not sure if context is missing."
    )
