"""
BUCKET: Product Agent.
Handles: features, pricing, comparisons, availability.
"""
from agents.base_agent import BaseAgent


class ProductAgent(BaseAgent):
    name = "product"
    system_prompt = (
        "You are the Product Information agent for TechMart Electronics. "
        "You handle questions about features, pricing, comparisons, and availability. "
        "Never invent prices or specs that aren't in the provided context."
    )
