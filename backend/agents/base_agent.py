"""
Every specialized agent inherits this. Having one shared base class is
what guarantees all 5 agents have an identical interface - this is the
single biggest integration-risk reducer for this module: the router and
aggregator never need to know which concrete agent they're talking to.
"""
from models.schemas import AgentResponse
from core.llm import call_llm
from rag.retriever import retrieve
from core.trace import Trace


class BaseAgent:
    name: str = "base"
    system_prompt: str = "You are a helpful customer support agent."

    def handle(self, query: str, trace: Trace) -> AgentResponse:
        # --- BUCKET START: real agents will likely override more of this,
        # e.g. custom retrieval filtering, multi-step reasoning, etc.
        # This base implementation is real RAG + real LLM wiring with
        # generic behavior, so it's runnable for every agent out of the box.
        chunks = retrieve(query, trace=trace, agent_name=self.name)
        context_text = "\n".join(f"- {c.text} (source: {c.source_document})" for c in chunks) or "No matching documents found."

        answer = call_llm(
            system_prompt=self.system_prompt,
            user_prompt=f"Customer question: {query}\n\nRelevant company info:\n{context_text}\n\nAnswer the customer.",
            agent_name=self.name,
        )
        # --- BUCKET END ---

        response = AgentResponse(agent_name=self.name, answer=answer, used_chunks=chunks, confidence=0.5)
        trace.log(f"agent:{self.name}", {"chunks_retrieved": len(chunks)})
        return response
