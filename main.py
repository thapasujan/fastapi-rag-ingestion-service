from fastapi import FastAPI
from app.core.config import get_settings

settings = get_settings()
app = FastAPI(title="RAG Document Backend", version="0.1.0")


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}