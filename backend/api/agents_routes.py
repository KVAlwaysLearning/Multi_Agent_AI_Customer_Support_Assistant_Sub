"""
Exposes which agents are live, so the dashboard doesn't have to hardcode
a list that can drift out of sync with the actual AGENT_REGISTRY.
"""
from fastapi import APIRouter

router = APIRouter(tags=["agents"])

# Keep this in sync with AGENT_REGISTRY in api/chat_routes.py
AGENTS_INFO = [
    {"name": "billing", "label": "Billing Agent", "description": "Payments, invoices, subscriptions", "status": "active"},
    {"name": "technical", "label": "Technical Agent", "description": "Login issues, errors, installation", "status": "active"},
    {"name": "product", "label": "Product Agent", "description": "Features, pricing, comparisons", "status": "active"},
    {"name": "complaint", "label": "Complaint Agent", "description": "Escalations, dissatisfaction", "status": "active"},
    {"name": "faq", "label": "FAQ Agent", "description": "Policies, shipping, warranty", "status": "active"},
]


@router.get("/agents")
def list_agents():
    return {"total_active": len(AGENTS_INFO), "agents": AGENTS_INFO}
