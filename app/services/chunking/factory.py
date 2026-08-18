from enum import Enum

from app.services.chunking.base import ChunkingStrategy
from app.services.chunking.fixed_size import FixedSizeChunker
from app.services.chunking.paragraph import ParagraphChunker


class ChunkingStrategyName(str, Enum):
    FIXED_SIZE = "fixed_size"
    PARAGRAPH = "paragraph"


def get_chunker(strategy: ChunkingStrategyName) -> ChunkingStrategy:
    """Factory function - returns the right chunker instance by name."""
    if strategy == ChunkingStrategyName.FIXED_SIZE:
        return FixedSizeChunker(chunk_size=500, overlap=50)
    elif strategy == ChunkingStrategyName.PARAGRAPH:
        return ParagraphChunker(max_chunk_size=800)
    raise ValueError(f"Unknown chunking strategy: {strategy}")