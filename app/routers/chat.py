from fastapi import APIRouter

from app.schemas.chat import ChatRequest, ChatDebugResponse, RetrievedChunk, RetrievedChunk, ChatResponse
from app.services.embeddings import embed_texts
from app.services.vector_store import search_similar
from app.services.embeddings import embed_query
from app.services.rag import answer_query

router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("", response_model=ChatResponse)
async def chat(payload: ChatRequest) -> ChatResponse:
    response_text = await answer_query(payload.session_id, payload.message)
    return ChatResponse(session_id=payload.session_id, response=response_text)

@router.post("/debug-retrieve", response_model=ChatDebugResponse)
async def debug_retrieve(payload: ChatRequest) -> ChatDebugResponse:
    """
    Temporary endpoint to test retrieval in isolation"""
    query_vector = await embed_query(payload.message)
    results = await search_similar(query_vector, top_k=5)

    return ChatDebugResponse(
        query=payload.message,
        retrieved_chunks=[RetrievedChunk(**r) for r in results],
    )

