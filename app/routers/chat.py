from fastapi import APIRouter, Depends

from app.schemas.chat import ChatRequest, ChatDebugResponse, RetrievedChunk, RetrievedChunk, ChatResponse
from app.services.embeddings import embed_texts
from app.services.vector_store import search_similar
from app.services.embeddings import embed_query
from app.services.rag import answer_query

from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.models.booking import Booking

router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("", response_model=ChatResponse)
async def chat(payload: ChatRequest, db: AsyncSession = Depends(get_db)) -> ChatResponse:
    response_text, booking_info = await answer_query(payload.session_id, payload.message)

    if booking_info.is_booking_request and not booking_info.missing_fields:
        booking = Booking(
            name=booking_info.name,
            email=booking_info.email,
            interview_date=booking_info.date,
            interview_time=booking_info.time,
        )
        db.add(booking)
        await db.commit()
        print(f"Booking saved: {booking_info.name} - {booking_info.email}")

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

