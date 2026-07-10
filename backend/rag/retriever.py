"""
Single retrieval entry point every agent calls. Loads the vectorstore
once (lazily) and reuses it across requests.
"""
from models.schemas import RetrievedChunk
from core.config import settings
from core.trace import Trace
from rag.vectorstore import VectorStore

_store = None


def _get_store() -> VectorStore:
    global _store
    if _store is None:
        _store = VectorStore(settings.VECTORSTORE_DIR)
        _store.load()
    return _store


def retrieve(query: str, trace: Trace, agent_name: str = "unknown", top_k: int = None) -> list[RetrievedChunk]:
    top_k = top_k or settings.RETRIEVAL_TOP_K
    store = _get_store()
    raw_results = store.search(query, top_k=top_k)
    chunks = [RetrievedChunk(**r) for r in raw_results]
    trace.log(f"retrieval:{agent_name}", {"query": query, "results_found": len(chunks)})
    return chunks
