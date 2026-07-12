"""
Real implementation - embeddings and FAISS don't depend on Groq either,
so this is fully functional once you run `python rag/ingest.py` with PDFs
in /knowledge_base. Until that's run, vectorstore is just empty (returns
no chunks) rather than erroring, so /chat is still verifiable without a KB.
"""
import os
import json
import logging
import numpy as np

logger = logging.getLogger("rag.vectorstore")

_model = None  # lazy-loaded, sentence-transformers is a heavier import


def get_embedding_model():
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        from core.config import settings
        model_name = settings.EMBEDDING_MODEL
        logger.info(f"[RAG] Loading embedding model: {model_name}")
        _model = SentenceTransformer(model_name, cache_folder="/tmp/models")
    return _model


def embed_texts(texts: list[str]) -> np.ndarray:
    model = get_embedding_model()
    return np.array(model.encode(texts, show_progress_bar=False), dtype="float32")


class VectorStore:
    def __init__(self, store_dir: str):
        self.store_dir = store_dir
        self.index_path = os.path.join(store_dir, "index.faiss")
        self.meta_path = os.path.join(store_dir, "meta.json")
        self.index = None
        self.metadata = []  # list of {text, source_document} aligned to index rows

    def build(self, chunks: list[dict]):
        import faiss
        if not chunks:
            logger.warning("[RAG] No chunks provided - vectorstore will be empty.")
            self.index = None
            self.metadata = []
            return

        texts = [c["text"] for c in chunks]
        vectors = embed_texts(texts)
        dim = vectors.shape[1]
        index = faiss.IndexFlatL2(dim)
        index.add(vectors)
        self.index = index
        self.metadata = chunks

    def save(self):
        import faiss
        os.makedirs(self.store_dir, exist_ok=True)
        if self.index is not None:
            faiss.write_index(self.index, self.index_path)
            with open(self.meta_path, "w") as f:
                json.dump(self.metadata, f)
            logger.info(f"[RAG] Saved vectorstore to {self.store_dir} ({len(self.metadata)} chunks)")

    def load(self):
        from core.config import settings
        if getattr(settings, 'DISABLE_EMBEDDINGS', False):
            logger.info("[RAG] Embeddings disabled.")
            self.index = None
            self.metadata = []
            return
        import faiss
        if os.path.exists(self.index_path) and os.path.exists(self.meta_path):
            self.index = faiss.read_index(self.index_path)
            with open(self.meta_path) as f:
                self.metadata = json.load(f)
            logger.info(f"[RAG] Loaded vectorstore ({len(self.metadata)} chunks)")
        else:
            logger.info("[RAG] No vectorstore found - retrieval returns empty.")
            self.index = None
            self.metadata = []

    def search(self, query: str, top_k: int = 3) -> list[dict]:
        if self.index is None or not self.metadata:
            return []
        # Lazy load embedding model only when searching
        q_vector = embed_texts([query])
        distances, indices = self.index.search(q_vector, top_k)
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx == -1 or idx >= len(self.metadata):
                continue
            meta = self.metadata[idx]
            results.append({
                "text": meta["text"],
                "source_document": meta["source_document"],
                "score": float(dist)
            })
        return results
