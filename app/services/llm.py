from google import genai

from app.core.config import get_settings

settings = get_settings()

_client = genai.Client(api_key=settings.gemini_api_key)


async def generate_response(prompt: str) -> str:
    """Call the Gemini chat model to generate a response to the given prompt."""
    result = await _client.aio.models.generate_content(
        model=settings.chat_model,
        contents=prompt,
    )
    return result.text or ""