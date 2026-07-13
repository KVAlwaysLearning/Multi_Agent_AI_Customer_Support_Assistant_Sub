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

    def handle(self, query: str, trace: Trace, history: list = None) -> AgentResponse:
        # Build conversation context from history
        history_text = ""
        if history:
            history_text = "\n\nPrevious conversation:\n"
            for msg in history[-6:]:  # last 6 messages
                role = "Customer" if msg["role"] == "user" else "Agent"
                history_text += f"{role}: {msg['text']}\n"

        # RAG retrieval
        chunks = retrieve(query, trace=trace, agent_name=self.name)
        context_text = "\n".join(
            f"- {c.text} (source: {c.source_document})" for c in chunks
        ) or "No matching documents found."

        # Build prompt with history
        user_prompt = f"{history_text}\nCustomer question: {query}\n\nRelevant company info:\n{context_text}\n\nAnswer the customer."

        answer = call_llm(
            system_prompt=self.system_prompt,
            user_prompt=user_prompt,
            agent_name=self.name,
        )

        response = AgentResponse(
            agent_name=self.name,
            answer=answer,
            used_chunks=chunks,
            confidence=0.5
        )
        trace.log(f"agent:{self.name}", {"chunks_retrieved": len(chunks)})
        return response
