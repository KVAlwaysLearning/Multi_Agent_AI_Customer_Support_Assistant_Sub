"""
Centralized settings. Everything reads from env vars so local/dev/prod
behave the same way, only the .env differs.

NOTE: GROQ_API_KEY is intentionally allowed to be empty. When it's empty,
the LLM client (core/llm.py) runs in STUB MODE and returns a fixed string
instead of calling Groq, so the whole pipeline is runnable and verifiable
before you add a real key.
"""
import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # --- App ---
    APP_NAME: str = "Multi-Agent AI Customer Support Assistant"
    ENV: str = os.getenv("ENV", "development")
    FRONTEND_ORIGIN: str = os.getenv("FRONTEND_ORIGIN", "http://localhost:3000")

    # --- Auth ---
    JWT_SECRET: str = os.getenv("JWT_SECRET", "dev-secret-change-me")
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60 * 24

    # --- Database ---
    MONGO_URI: str = os.getenv("MONGO_URI", "")  # empty -> falls back to in-memory store
    MONGO_DB_NAME: str = os.getenv("MONGO_DB_NAME", "customer_support_ai")

    # --- LLM (Groq, hosts Llama 3) ---
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")  # empty -> stub mode, fill in later
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
    GROQ_BASE_URL: str = "https://api.groq.com/openai/v1"

    # --- RAG ---
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    DISABLE_EMBEDDINGS: bool = os.getenv("DISABLE_EMBEDDINGS", "false").lower() == "true"
    VECTORSTORE_DIR: str = os.getenv("VECTORSTORE_DIR", "./vectorstore_data")
    KNOWLEDGE_BASE_DIR: str = os.getenv("KNOWLEDGE_BASE_DIR", "../knowledge_base")
    RETRIEVAL_TOP_K: int = int(os.getenv("RETRIEVAL_TOP_K", "3"))

    class Config:
        env_file = ".env"


settings = Settings()
