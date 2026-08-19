from fastapi import APIRouter, Depends, HTTPException

from app.schemas.chat import ChatRequest, ChatResponse
from app.services.rag import answer_query

from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.models.booking import Booking

router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("", response_model=ChatResponse)
async def chat(payload: ChatRequest, db: AsyncSession = Depends(get_db)) -> ChatResponse:
    try:
        response_text, booking_info = await answer_query(payload.session_id, payload.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate response: {str(e)}")

    if booking_info.is_booking_request and not booking_info.missing_fields:
        booking = Booking(
            name=booking_info.name,
            email=booking_info.email,
            interview_date=booking_info.date,
            interview_time=booking_info.time,
        )
        db.add(booking)
        await db.commit()

    return ChatResponse(session_id=payload.session_id, response=response_text)

