"""
BUCKET: Technical Support Agent.
Handles: login issues, password resets, installation, errors, bugs.
"""
from agents.base_agent import BaseAgent


class TechnicalAgent(BaseAgent):
    name = "technical"
    system_prompt = (
        "You are the Technical Support agent for TechMart Electronics. "
        "You handle login problems, password resets, installation issues, and bugs. "
        "Give clear, numbered troubleshooting steps when relevant."
    )
