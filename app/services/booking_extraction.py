import json

from app.services.llm import generate_response
from app.schemas.booking import BookingExtraction

EXTRACTION_PROMPT_TEMPLATE = """You are analyzing a user message to detect if they want to book an interview.

Determine if the message expresses intent to book/schedule an interview. If so, extract
whatever booking details (name, email, date, time) are present in the message and the
recent conversation.

Conversation so far:
{history}

Latest message: {message}

Respond with ONLY a valid JSON object, no other text, no markdown fences, in this exact shape:
{{
  "is_booking_request": true or false,
  "name": "extracted name or null",
  "email": "extracted email or null",
  "date": "extracted date or null",
  "time": "extracted time or null",
  "missing_fields": ["list of field names still missing, e.g. email, date"]
}}

If is_booking_request is false, set all other fields to null and missing_fields to an empty list."""


async def extract_booking_intent(message: str, history: list[dict[str, str]]) -> BookingExtraction:
    """
    Analyze the user's message and conversation history to determine if they want to book an interview.
    """
    history_text = "\n".join(f"{turn['role']}: {turn['content']}" for turn in history)
    prompt = EXTRACTION_PROMPT_TEMPLATE.format(history=history_text, message=message)

    raw_response = await generate_response(prompt)

    cleaned = raw_response.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()

    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError:
        return BookingExtraction(is_booking_request=False)

    return BookingExtraction(**data)