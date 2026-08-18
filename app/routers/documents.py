import os
import uuid
from pathlib import Path

from fastapi import APIRouter, UploadFile, File, HTTPException

from app.core.config import get_settings
from app.schemas.document import DocumentUploadResponse

from app.services.extraction import extract_text

from app.services.chunking import ChunkingStrategyName, get_chunker

router = APIRouter(prefix="/documents", tags=["documents"])

settings = get_settings()

ALLOWED_EXTENSIONS = {".pdf", ".txt"}


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    strategy: ChunkingStrategyName = ChunkingStrategyName.FIXED_SIZE,
) -> DocumentUploadResponse:
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Only .pdf and .txt files are allowed")

    os.makedirs(settings.upload_dir, exist_ok=True)

    doc_id = uuid.uuid4()
    save_path = Path(settings.upload_dir) / f"{doc_id}{ext}"

    contents = await file.read()
    with open(save_path, "wb") as f:
        f.write(contents)

    try:
        extracted_text = await extract_text(str(save_path), ext.lstrip("."))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    chunker = get_chunker(strategy)
    chunks = chunker.chunk(extracted_text)

    print(f"Extracted {len(extracted_text)} chars, split into {len(chunks)} chunks using '{strategy.value}'")

    return DocumentUploadResponse(
        id=doc_id,
        filename=file.filename,
        file_type=ext.lstrip("."),
        message=f"File processed: {len(chunks)} chunks created using '{strategy}' strategy.",
    )