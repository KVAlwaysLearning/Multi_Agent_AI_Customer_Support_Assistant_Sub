"""
BUCKET: Billing Agent.
Handles: payment issues, subscriptions, invoices, refunds.
Inherits all real wiring (RAG + LLM) from BaseAgent. Override `handle()`
later if billing needs custom logic beyond generic RAG+LLM
(e.g. calling a real billing/subscription API).
"""
from agents.base_agent import BaseAgent


class BillingAgent(BaseAgent):
    name = "billing"
    system_prompt = (
        "You are the Billing support agent for TechMart Electronics. "
        "You handle payments, subscriptions, invoices, and refunds. "
        "Be precise about policy details and never invent refund amounts or dates."
    )
