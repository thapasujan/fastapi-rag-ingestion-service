from pydantic import BaseModel


class ChatRequest(BaseModel):
    session_id: str
    message: str


class RetrievedChunk(BaseModel):
    text: str
    document_id: str
    score: float


class ChatDebugResponse(BaseModel):
    """Temporary response for testing retrieval alone, before generation is wired in."""
    query: str
    retrieved_chunks: list[RetrievedChunk]

class ChatResponse(BaseModel):
    session_id: str
    response: str