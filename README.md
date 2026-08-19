# RAG Document Backend

A FastAPI backend with two APIs: a Document Ingestion API (upload PDFs/TXT files, chunk, embed, store) and a Conversational RAG API (chat with your documents, with memory and interview booking).

## Tech Stack

- **Framework:** FastAPI (fully async)
- **Database:** PostgreSQL (via SQLAlchemy 2.0 async + Alembic migrations)
- **Vector DB:** Qdrant
- **Chat Memory:** Redis
- **LLM & Embeddings:** Google Gemini (`gemini-embedding-001`, `gemini-3.6-flash`)
- **Package Manager:** uv

## Architecture

**Document Ingestion Flow:**
```
Upload file → Extract text (pypdf/plain read) → Chunk text (2 strategies)
→ Generate embeddings (Gemini) → Store vectors (Qdrant) → Save metadata (Postgres)
```

**Conversational RAG Flow:**
```
User message → Check booking intent (LLM) → If not booking:
Embed query → Search similar chunks (Qdrant) → Build prompt manually
→ Call LLM → Save turn to Redis → Return response
```

No LangChain `RetrievalQAChain` is used anywhere — the retrieval, prompt construction, and generation steps are all written manually in `app/services/rag.py`.

## Project Structure

```
app/
├── core/          # config, database connection
├── models/        # SQLAlchemy DB models (Document, Booking)
├── schemas/       # Pydantic request/response models
├── routers/       # API endpoints (documents, chat)
└── services/      # business logic (extraction, chunking, embeddings, RAG, memory)
```

## Setup

### 1. Prerequisites
- Python 3.12+
- [uv](https://docs.astral.sh/uv/) installed
- Docker + Docker Compose
- A free Gemini API key from [aistudio.google.com](https://aistudio.google.com/apikey)

### 2. Clone and install dependencies
```bash
git clone https://github.com/thapasujan/fastapi-rag-ingestion-service.git
cd fastapi-rag-ingestion-service
uv sync
```

### 3. Configure environment
```bash
cp .env.example .env
```
Open `.env` and paste in your Gemini API key.

### 4. Start infrastructure (Postgres, Redis, Qdrant)
```bash
docker compose up -d
```

### 5. Run database migrations
```bash
uv run alembic upgrade head
```

### 6. Start the server
```bash
uv run uvicorn main:app --reload
```

### 7. Open the interactive API docs
```
http://localhost:8000/docs
```

## API Endpoints

- `POST http://localhost:8000/documents/upload` — upload and process a document
- `POST http://localhost:8000/chat` — chat with your documents (multi-turn + booking)
- `GET  http://localhost:8000/documents` — list all uploaded documents
- `GET  http://localhost:8000/health` — health check


### Document Ingestion

**`POST /documents/upload`**
Upload a `.pdf` or `.txt` file. Query param `strategy` selects the chunking method: `fixed_size` (default) or `paragraph`.

Response:
```json
{
  "id": "uuid",
  "filename": "resume.pdf",
  "file_type": "pdf",
  "message": "File processed: 19 chunks created using 'fixed_size' strategy."
}
```

**`GET /documents`**
Lists all ingested documents with their metadata.

### Conversational RAG

**`POST /chat`**
Send a message with a `session_id` to maintain conversation history across turns.

Request:
```json
{
  "session_id": "user-123",
  "message": "What skills are mentioned in the document?"
}
```

Response:
```json
{
  "session_id": "user-123",
  "response": "Based on the document, the skills include..."
}
```

Sending follow-up messages with the same `session_id` lets the assistant understand references to earlier turns (e.g. "which of those are backend related?").

**Interview booking** is handled automatically within the same `/chat` endpoint — if a message expresses intent to book an interview and includes name, email, date, and time, the booking is detected by the LLM, extracted, and saved to the database. If any field is missing, the assistant asks for it.

## Design Decisions

- **Chunking strategies:** `fixed_size` splits text into overlapping character windows (good for uniform chunk sizes); `paragraph` splits on natural paragraph boundaries and merges small ones together (better semantic coherence).
- **Vector DB:** Qdrant was chosen because it runs free and locally via Docker, with no rate limits or account setup required.
- **Embeddings/LLM:** Gemini was used instead of OpenAI to avoid paid API costs, while still supporting both embeddings and chat generation from one provider.
- **Async throughout:** All I/O — file reads, DB queries, HTTP calls to Gemini/Qdrant/Redis — is async, so the app can handle concurrent requests efficiently.
- **No chain libraries:** Retrieval, prompt construction, and generation are all implemented explicitly in `app/services/rag.py`, per the task's constraint against `RetrievalQAChain`.

## Constraints Satisfied

- ✅ No FAISS or Chroma (Qdrant used instead)
- ✅ No RetrievalQAChain or LangChain chain abstractions
- ✅ No UI — API-only, testable via Swagger/Postman
- ✅ Clean modular structure (routers/services/models/schemas/core)
- ✅ Type hints throughout, verified with `mypy`

## Known Limitations

- No automated test suite (time-constrained build)
- No authentication/rate limiting (out of scope for this task)
- Uploaded files are stored on local disk, not cloud storage