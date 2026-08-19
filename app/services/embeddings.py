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
    if result.embeddings is None:
        raise ValueError("Embedding API returned no embeddings")
    return [e.values for e in result.embeddings if e.values is not None]


async def embed_query(text: str) -> list[float]:
    result = await _client.aio.models.embed_content(
        model=settings.embedding_model,
        contents=[text],
        config=EmbedContentConfig(
            task_type="RETRIEVAL_QUERY",
            output_dimensionality=EMBEDDING_DIM,
        ),
    )
    if result.embeddings is None or result.embeddings[0].values is None:
        raise ValueError("Embedding API returned no embedding for query")
    return result.embeddings[0].values