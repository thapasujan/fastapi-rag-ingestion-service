import asyncio
from pathlib import Path

from pypdf import PdfReader


def _extract_pdf_text_sync(file_path: str) -> str:

    reader = PdfReader(file_path)
    text_parts = [page.extract_text() or "" for page in reader.pages]
    return "\n".join(text_parts)


def _extract_txt_text_sync(file_path: str) -> str:
    """Sync plain text file reading."""
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


async def extract_text(file_path: str, file_type: str) -> str:
    loop = asyncio.get_running_loop()

    if file_type == "pdf":
        text = await loop.run_in_executor(None, _extract_pdf_text_sync, file_path)
    elif file_type == "txt":
        text = await loop.run_in_executor(None, _extract_txt_text_sync, file_path)
    else:
        raise ValueError(f"Unsupported file type: {file_type}")

    if not text.strip():
        raise ValueError("No extractable text found in the file")

    return text