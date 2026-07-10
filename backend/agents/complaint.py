"""
BUCKET: Complaint Agent.
Handles: complaints, escalation, customer dissatisfaction.
NOTE: confidence/severity scoring here is the placeholder most worth
revisiting first, since it feeds the (separately bucketed) escalation flow.
"""
from agents.base_agent import BaseAgent


class ComplaintAgent(BaseAgent):
    name = "complaint"
    system_prompt = (
        "You are the Complaints agent for TechMart Electronics. "
        "Acknowledge the customer's frustration genuinely, then explain next steps. "
        "If the issue sounds severe or unresolved, say it will be escalated to a human agent."
    )
