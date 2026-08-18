import uuid

from qdrant_client import AsyncQdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

from app.core.config import get_settings

settings = get_settings()

_client = AsyncQdrantClient(host=settings.qdrant_host, port=settings.qdrant_port)

EMBEDDING_DIM = 768  # Gemini text-embedding-004 output dimension


async def ensure_collection() -> None:

    collections = await _client.get_collections()
    existing_names = {c.name for c in collections.collections}

    if settings.qdrant_collection_name not in existing_names:
        await _client.create_collection(
            collection_name=settings.qdrant_collection_name,
            vectors_config=VectorParams(size=EMBEDDING_DIM, distance=Distance.COSINE),
        )


async def upsert_chunks(
    document_id: uuid.UUID,
    chunks: list[str],
    vectors: list[list[float]],
) -> None:

    points = [
        PointStruct(
            id=str(uuid.uuid4()),
            vector=vector,
            payload={
                "document_id": str(document_id),
                "chunk_index": idx,
                "text": chunk,
            },
        )
        for idx, (chunk, vector) in enumerate(zip(chunks, vectors))
    ]

    await _client.upsert(collection_name=settings.qdrant_collection_name, points=points)


async def search_similar(query_vector: list[float], top_k: int = 5) -> list[dict]:

    results = await _client.query_points(
        collection_name=settings.qdrant_collection_name,
        query=query_vector,
        limit=top_k,
    )
    return [
        {"text": point.payload["text"], "document_id": point.payload["document_id"], "score": point.score}
        for point in results.points
    ]