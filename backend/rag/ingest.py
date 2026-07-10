"""
Run this once (and again any time the knowledge base PDFs change):

    cd backend
    python rag/ingest.py

It loads every PDF in /knowledge_base, chunks it, embeds it, and saves
a FAISS index to VECTORSTORE_DIR. Until you run this, retrieval just
returns empty results (see vectorstore.py) - the pipeline still runs
and is verifiable, it just won't have real company info to use yet.
"""
import logging
from rag.chunking import load_and_chunk_knowledge_base
from rag.vectorstore import VectorStore
from core.config import settings

logging.basicConfig(level=logging.INFO)


def main():
    chunks = load_and_chunk_knowledge_base()
    print(f"Loaded {len(chunks)} chunks from {settings.KNOWLEDGE_BASE_DIR}")
    store = VectorStore(settings.VECTORSTORE_DIR)
    store.build(chunks)
    store.save()
    print("Ingestion complete.")


if __name__ == "__main__":
    main()
