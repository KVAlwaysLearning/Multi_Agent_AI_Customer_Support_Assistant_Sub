"""
Combines multiple agent responses into one final answer (needed for the
multi-agent case, e.g. billing + technical). Real implementation - simple
concatenation logic is fine as a default and easy to upgrade to an
LLM-based "synthesize one coherent answer" pass later.
"""
from models.schemas import AgentResponse
from core.trace import Trace


def aggregate(responses: list[AgentResponse], trace: Trace) -> str:
    if len(responses) == 1:
        final = responses[0].answer
    else:
        parts = [f"[{r.agent_name.upper()}]: {r.answer}" for r in responses]
        final = "\n\n".join(parts)

    trace.log("aggregator", {"agents_combined": [r.agent_name for r in responses]})
    return final
