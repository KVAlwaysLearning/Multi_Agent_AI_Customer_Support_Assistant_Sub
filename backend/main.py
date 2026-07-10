from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.config import settings
from core.llm import is_stub_mode
from api.chat_routes import router_api
from api.auth_routes import router as auth_router

app = FastAPI(title=settings.APP_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_ORIGIN, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(router_api)


@app.get("/")
def root():
    return {
        "app": settings.APP_NAME,
        "status": "running",
        "llm_stub_mode": is_stub_mode(),
        "note": "llm_stub_mode=true means GROQ_API_KEY is not set yet - agents return placeholder text.",
    }


@app.get("/health")
def health():
    return {"status": "ok"}
