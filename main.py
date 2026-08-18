from fastapi import FastAPI
from app.core.config import get_settings
from app.routers import documents
from app.routers import chat

settings = get_settings()
app = FastAPI(title="RAG Document Backend", version="0.1.0")

app.include_router(documents.router)
app.include_router(chat.router)

@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}