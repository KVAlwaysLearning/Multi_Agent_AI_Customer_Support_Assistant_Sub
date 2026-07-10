"""
Run this to build the FAISS index from knowledge_base files.
Supports both .pdf and .txt files.

    cd backend
    python rag/ingest.py
"""
import logging
import os
import sys

logging.basicConfig(level=logging.INFO)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def load_txt(filepath: str) -> str:
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 80) -> list:
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end].strip())
        start += chunk_size - overlap
    return [c for c in chunks if len(c) > 50]


def main():
    from rag.vectorstore import VectorStore
    from core.config import settings

    kb_dir = settings.KNOWLEDGE_BASE_DIR
    if not os.path.isdir(kb_dir):
        print(f"Knowledge base dir not found: {kb_dir}")
        return

    all_chunks = []
    for fname in os.listdir(kb_dir):
        path = os.path.join(kb_dir, fname)
        text = ""
        if fname.lower().endswith(".pdf"):
            from pypdf import PdfReader
            reader = PdfReader(path)
            text = "\n".join(p.extract_text() or "" for p in reader.pages)
        elif fname.lower().endswith(".txt"):
            text = load_txt(path)
        else:
            continue

        chunks = chunk_text(text)
        for c in chunks:
            all_chunks.append({"text": c, "source_document": fname})
        print(f"Loaded {fname}: {len(chunks)} chunks")

    print(f"\nTotal chunks: {len(all_chunks)}")
    store = VectorStore(settings.VECTORSTORE_DIR)
    store.build(all_chunks)
    store.save()
    print("✅ Ingestion complete.")


if __name__ == "__main__":
    main()
