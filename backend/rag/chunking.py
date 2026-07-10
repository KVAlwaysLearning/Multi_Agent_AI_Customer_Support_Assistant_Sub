"""
Real implementation (not a bucket) - loading and chunking PDFs doesn't
depend on Groq, so there's no reason to stub it.
"""
import os
import logging
from pypdf import PdfReader
from core.config import settings

logger = logging.getLogger("rag.chunking")

CHUNK_SIZE = 500       # characters per chunk
CHUNK_OVERLAP = 80


def load_pdf_text(filepath: str) -> str:
    reader = PdfReader(filepath)
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end].strip())
        start += chunk_size - overlap
    return [c for c in chunks if c]


def load_and_chunk_knowledge_base(kb_dir: str = None) -> list[dict]:
    """Returns list of {text, source_document} ready for embedding."""
    kb_dir = kb_dir or settings.KNOWLEDGE_BASE_DIR
    all_chunks = []
    if not os.path.isdir(kb_dir):
        logger.warning(f"[RAG] Knowledge base dir not found: {kb_dir}")
        return all_chunks

    for fname in os.listdir(kb_dir):
        if not fname.lower().endswith(".pdf"):
            continue
        path = os.path.join(kb_dir, fname)
        try:
            text = load_pdf_text(path)
            chunks = chunk_text(text)
            for c in chunks:
                all_chunks.append({"text": c, "source_document": fname})
            logger.info(f"[RAG] Loaded {fname}: {len(chunks)} chunks")
        except Exception as e:
            logger.error(f"[RAG] Failed to load {fname}: {e}")
    return all_chunks
