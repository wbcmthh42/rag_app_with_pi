from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from langchain_openai import AzureOpenAIEmbeddings, OpenAIEmbeddings
from pypdf import PdfReader

from app.core.config import Settings, get_settings


MAX_CHUNK_CHARS = 900
OVERLAP_CHARS = 120


def build_embeddings_client(settings: Settings):
    if settings.llm_provider.lower() == "azure":
        deployment = settings.azure_embedding_deployment or settings.embedding_model
        if not settings.azure_endpoint:
            raise ValueError("AZURE_OPENAI_ENDPOINT must be set when LLM_PROVIDER=azure.")
        return AzureOpenAIEmbeddings(
            api_key=settings.model_api_key,
            azure_endpoint=settings.azure_endpoint,
            api_version=settings.azure_api_version,
            azure_deployment=deployment,
            model=settings.embedding_model,
        )

    return OpenAIEmbeddings(
        api_key=settings.model_api_key,
        base_url=settings.model_base_url,
        model=settings.embedding_model,
    )


def chunk_text(text: str) -> list[str]:
    normalized = " ".join(text.split())
    if not normalized:
        return []

    chunks: list[str] = []
    start = 0
    while start < len(normalized):
        end = min(len(normalized), start + MAX_CHUNK_CHARS)
        chunk = normalized[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end == len(normalized):
            break
        start = max(end - OVERLAP_CHARS, start + 1)
    return chunks


def build_index() -> None:
    settings = get_settings()
    settings.vectorstore_dir.mkdir(parents=True, exist_ok=True)

    metadata_path = settings.metadata_path
    chunks_path = settings.chunks_path

    try:
        pdf_path = Path(settings.pdf_source_path)
        reader = PdfReader(str(pdf_path))
        document_bytes = pdf_path.read_bytes()
        checksum = hashlib.sha256(document_bytes).hexdigest()

        chunk_records: list[dict[str, object]] = []
        for page_number, page in enumerate(reader.pages, start=1):
            page_text = page.extract_text() or ""
            for chunk_index, text in enumerate(chunk_text(page_text), start=1):
                chunk_records.append(
                    {
                        "chunk_id": f"chunk-{uuid4()}",
                        "page_number": page_number,
                        "text": text,
                        "token_count": len(text.split()),
                    }
                )

        retrieval_mode = "keyword"
        if chunk_records and settings.model_api_key and settings.model_api_key != "replace-me":
            embedder = build_embeddings_client(settings)
            vectors = embedder.embed_documents([str(chunk["text"]) for chunk in chunk_records])
            for chunk, vector in zip(chunk_records, vectors, strict=False):
                chunk["embedding"] = vector
            retrieval_mode = "embeddings"
        else:
            for chunk in chunk_records:
                chunk["embedding"] = None

        metadata = {
            "document_id": "barbie-pdf",
            "display_name": pdf_path.name,
            "source_path": str(pdf_path),
            "checksum": checksum,
            "page_count": len(reader.pages),
            "ingestion_status": "ready" if chunk_records else "failed",
            "last_indexed_at": datetime.now(UTC).isoformat(),
            "error": None if chunk_records else "No extractable text found in PDF.",
            "retrieval_mode": retrieval_mode,
        }

        metadata_path.write_text(json.dumps(metadata, indent=2))
        chunks_path.write_text(json.dumps(chunk_records, indent=2))
    except Exception as exc:  # pragma: no cover
        metadata = {
            "document_id": "barbie-pdf",
            "display_name": Path(settings.pdf_source_path).name,
            "source_path": str(settings.pdf_source_path),
            "checksum": "",
            "page_count": 0,
            "ingestion_status": "failed",
            "last_indexed_at": datetime.now(UTC).isoformat(),
            "error": str(exc),
        }
        metadata_path.write_text(json.dumps(metadata, indent=2))
        chunks_path.write_text(json.dumps([], indent=2))
        raise


if __name__ == "__main__":
    build_index()
