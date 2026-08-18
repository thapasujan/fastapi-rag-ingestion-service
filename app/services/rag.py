from app.services.embeddings import embed_query
from app.services.vector_store import search_similar
from app.services.llm import generate_response
from app.services.memory import get_history, append_turn


def _build_prompt(message: str, chunks: list[dict], history: list[dict[str, str]]) -> str:
    """Build a prompt string for the LLM that includes the retrieved context and conversation history."""
    context_text = "\n\n".join(f"[Source {i+1}]: {c['text']}" for i, c in enumerate(chunks))

    history_text = "\n".join(f"{turn['role'].capitalize()}: {turn['content']}" for turn in history)

    prompt = f"""You are an AI assistant helping a user with their questions. Use the following context from retrieved documents to answer the user's question.
    If the context does not contain the answer, respond with "I don't know."

Context:
{context_text}

Conversation so far:
{history_text}

User: {message}
Assistant:"""

    return prompt


async def answer_query(session_id: str, message: str) -> str:
    """Full custom RAG pipeline: retrieve -> build prompt -> generate -> store memory."""
    query_vector = await embed_query(message)
    chunks = await search_similar(query_vector, top_k=5)

    history = await get_history(session_id)

    prompt = _build_prompt(message, chunks, history)
    response_text = await generate_response(prompt)

    await append_turn(session_id, "user", message)
    await append_turn(session_id, "assistant", response_text)

    return response_text