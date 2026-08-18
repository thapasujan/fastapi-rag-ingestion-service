from google import genai
from google.genai.types import EmbedContentConfig

from app.core.config import get_settings

settings = get_settings()

_client = genai.Client(api_key=settings.gemini_api_key)

EMBEDDING_DIM = 768


async def embed_texts(texts: list[str]) -> list[list[float]]:
    
    if not texts:
        return []

    result = await _client.aio.models.embed_content(
        model=settings.embedding_model,
        contents=texts,
        config=EmbedContentConfig(
            task_type="RETRIEVAL_DOCUMENT",
            output_dimensionality=EMBEDDING_DIM,
        ),
    )
    return [embedding.values for embedding in result.embeddings]