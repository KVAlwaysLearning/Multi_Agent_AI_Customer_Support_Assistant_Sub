"""
Single point of contact for all LLM calls. Every agent calls `call_llm()`
instead of touching Groq directly, so swapping providers later only
means editing this one file.

STUB MODE: if GROQ_API_KEY is not set, this returns a clearly-labelled
placeholder string instead of failing or calling the real API. This is the
intentional "blank bucket" for the LLM piece - the wiring is real and
verifiable, the actual model call is deferred until you add a key.
"""
import logging
from core.config import settings

logger = logging.getLogger("llm")

try:
    from openai import OpenAI  # Groq exposes an OpenAI-compatible API
    _client = OpenAI(api_key=settings.GROQ_API_KEY, base_url=settings.GROQ_BASE_URL) if settings.GROQ_API_KEY else None
except ImportError:
    _client = None


def is_stub_mode() -> bool:
    return not bool(settings.GROQ_API_KEY)


def call_llm(system_prompt: str, user_prompt: str, agent_name: str = "unknown") -> str:
    """
    Returns the LLM's text response. In stub mode, returns a fixed,
    clearly-labelled placeholder so downstream code (and you, manually
    verifying the trace) can tell at a glance that no real call was made.
    """
    if is_stub_mode():
        logger.info(f"[STUB LLM] agent={agent_name} | would have called Groq with prompt len={len(user_prompt)}")
        return (
            f"[STUB RESPONSE from {agent_name}] "
            f"Groq API key not set yet - this is a placeholder. "
            f"Add GROQ_API_KEY to .env to get a real answer here."
        )

    try:
        completion = _client.chat.completions.create(
            model=settings.GROQ_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.3,
            max_tokens=500,
        )
        return completion.choices[0].message.content
    except Exception as e:
        logger.error(f"[LLM ERROR] agent={agent_name} | {e}")
        return f"[LLM ERROR from {agent_name}] {e}"
