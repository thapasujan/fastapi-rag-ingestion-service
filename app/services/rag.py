from app.services.embeddings import embed_query
from app.services.vector_store import search_similar
from app.services.llm import generate_response
from app.services.memory import get_history, append_turn
from app.services.booking_extraction import extract_booking_intent
from app.schemas.booking import BookingExtraction


def _build_prompt(message: str, chunks: list[dict], history: list[dict[str, str]]) -> str:
    context_text = "\n\n".join(f"[Source {i+1}]: {c['text']}" for i, c in enumerate(chunks))
    history_text = "\n".join(f"{turn['role'].capitalize()}: {turn['content']}" for turn in history)

    prompt = f"""You are a helpful assistant answering questions based on the provided document context.
Use the context below to answer the user's question. If the answer isn't in the context, say you don't know
- do not make up information.

Context:
{context_text}

Conversation so far:
{history_text}

User: {message}
Assistant:"""

    return prompt


async def answer_query(session_id: str, message: str) -> tuple[str, BookingExtraction]:
    """
    Full custom RAG pipeline, now also checking for booking intent.

    Returns both the chat response text and the booking extraction result,
    so the router can decide whether to save a booking record.
    """
    history = await get_history(session_id)

    booking_info = await extract_booking_intent(message, history)

    if booking_info.is_booking_request and not booking_info.missing_fields:
        response_text = (
            f"Great, I've got your interview booking details:\n"
            f"- Name: {booking_info.name}\n"
            f"- Email: {booking_info.email}\n"
            f"- Date: {booking_info.date}\n"
            f"- Time: {booking_info.time}\n\n"
            f"This has been recorded. Looking forward to speaking with you!"
        )
    elif booking_info.is_booking_request and booking_info.missing_fields:
        missing = ", ".join(booking_info.missing_fields)
        response_text = f"I'd be happy to help you book an interview. Could you please also provide: {missing}?"
    else:
        query_vector = await embed_query(message)
        chunks = await search_similar(query_vector, top_k=5)
        prompt = _build_prompt(message, chunks, history)
        response_text = await generate_response(prompt)

    await append_turn(session_id, "user", message)
    await append_turn(session_id, "assistant", response_text)

    return response_text, booking_info