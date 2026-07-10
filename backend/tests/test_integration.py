"""
INTEGRATION VERIFICATION SUITE.

This is the concrete answer to "how do we check everything is wired
correctly before writing detailed feature code." It does not check
whether any agent's ANSWER is good (that needs a real LLM key) - it
checks that every request flows through every required stage, calls
the right function, and produces a structurally valid response.

Run with:
    cd backend
    pytest tests/test_integration.py -v

Or run the standalone trace-print script below for a human-readable view.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def _chat(session_id: str, message: str):
    resp = client.post("/chat", json={"session_id": session_id, "message": message})
    assert resp.status_code == 200, resp.text
    return resp.json()


def test_root_reports_stub_mode():
    resp = client.get("/")
    assert resp.status_code == 200
    assert "llm_stub_mode" in resp.json()


def test_billing_query_routes_to_billing_agent():
    data = _chat("test-session-1", "I was charged twice on my invoice this month.")
    assert "billing" in data["agents_used"]
    stages = [s["stage"] for s in data["trace"]["steps"]]
    assert "intent_detection" in stages
    assert "agent_router" in stages
    assert "agent:billing" in stages
    assert "aggregator" in stages


def test_technical_query_routes_to_technical_agent():
    data = _chat("test-session-2", "I can't log in, it keeps giving me an error.")
    assert "technical" in data["agents_used"]


def test_multi_agent_case_from_project_doc():
    data = _chat("test-session-3", "I paid yesterday but Premium is still locked.")
    assert set(data["agents_used"]) == {"billing", "technical"}
    stages = [s["stage"] for s in data["trace"]["steps"]]
    assert "agent:billing" in stages
    assert "agent:technical" in stages
    assert "aggregator" in stages


def test_unrecognized_query_falls_back_to_faq():
    data = _chat("test-session-4", "asdkjasdkj random gibberish text")
    assert "faq" in data["agents_used"]


def test_conversation_memory_persists():
    _chat("test-session-5", "What's your refund policy?")
    resp = client.get("/conversations/test-session-5")
    assert resp.status_code == 200
    history = resp.json()
    assert len(history["messages"]) == 2  # user + ai
    assert history["messages"][0]["role"] == "user"
    assert history["messages"][1]["role"] == "ai"


def test_every_stage_fires_for_a_full_request():
    """The single most important test: does input reach every required stage."""
    data = _chat("test-session-6", "How much does shipping cost?")
    stages = [s["stage"] for s in data["trace"]["steps"]]
    required_stage_prefixes = [
        "memory:save_user_message",
        "intent_detection",
        "agent_router",
        "retrieval:",
        "agent:",
        "aggregator",
        "memory:save_ai_message",
    ]
    for prefix in required_stage_prefixes:
        assert any(s.startswith(prefix) for s in stages), f"Missing stage: {prefix}\nGot: {stages}"
