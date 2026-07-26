from __future__ import annotations

import json
import math
import re
from dataclasses import dataclass
from pathlib import Path

from langchain_openai import AzureOpenAIEmbeddings, OpenAIEmbeddings

from app.core.config import Settings


@dataclass
class DocumentChunk:
    chunk_id: str
    page_number: int
    text: str
    token_count: int
    embedding: list[float] | None = None


@dataclass
class DocumentMetadata:
    document_id: str
    display_name: str
    source_path: str
    checksum: str
    page_count: int
    ingestion_status: str
    last_indexed_at: str | None = None
    error: str | None = None
    retrieval_mode: str = "keyword"


class DocumentUnavailableError(Exception):
    pass


class VectorStore:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.settings.vectorstore_dir.mkdir(parents=True, exist_ok=True)

    def _read_json(self, path: Path) -> dict | list:
        if not path.exists():
            raise DocumentUnavailableError(f"Missing index artifact: {path.name}")
        return json.loads(path.read_text())

    def load_metadata(self) -> DocumentMetadata:
        data = self._read_json(self.settings.metadata_path)
        metadata = DocumentMetadata(**data)
        if metadata.ingestion_status != "ready":
            raise DocumentUnavailableError(metadata.error or "Document index is not ready.")
        return metadata

    def load_chunks(self) -> list[DocumentChunk]:
        raw_chunks = self._read_json(self.settings.chunks_path)
        return [DocumentChunk(**chunk) for chunk in raw_chunks]

    def get_document_status(self) -> str:
        if not self.settings.metadata_path.exists():
            return "pending"
        try:
            data = json.loads(self.settings.metadata_path.read_text())
        except json.JSONDecodeError:
            return "failed"
        return data.get("ingestion_status", "pending")

    def is_ready(self) -> bool:
        return self.get_document_status() == "ready" and self.settings.chunks_path.exists()

    def retrieve(self, query: str, top_k: int = 4) -> list[dict[str, object]]:
        metadata = self.load_metadata()
        chunks = self.load_chunks()
        if metadata.retrieval_mode == "embeddings" and any(chunk.embedding for chunk in chunks):
            return self._retrieve_by_embeddings(query, chunks, top_k)
        return self._retrieve_by_keywords(query, chunks, top_k)

    def _retrieve_by_embeddings(self, query: str, chunks: list[DocumentChunk], top_k: int) -> list[dict[str, object]]:
        embedder = self._build_embeddings_client()
        query_vector = embedder.embed_query(query)
        scored_chunks: list[tuple[float, DocumentChunk]] = []
        for chunk in chunks:
            if not chunk.embedding:
                continue
            score = self._cosine_similarity(query_vector, chunk.embedding)
            if score <= 0:
                continue
            scored_chunks.append((score, chunk))

        scored_chunks.sort(key=lambda item: item[0], reverse=True)
        return [
            {
                "chunk_id": chunk.chunk_id,
                "page_number": chunk.page_number,
                "text": chunk.text,
                "retrieval_score": round(score, 4),
            }
            for score, chunk in scored_chunks[:top_k]
        ]

    def _retrieve_by_keywords(self, query: str, chunks: list[DocumentChunk], top_k: int) -> list[dict[str, object]]:
        query_terms = self._normalize(query)
        if not query_terms:
            return []

        scored_chunks: list[tuple[float, DocumentChunk]] = []
        for chunk in chunks:
            chunk_terms = self._normalize(chunk.text)
            overlap = len(query_terms.intersection(chunk_terms))
            if overlap == 0:
                continue
            score = overlap / math.sqrt(max(1, len(chunk_terms)))
            scored_chunks.append((score, chunk))

        scored_chunks.sort(key=lambda item: item[0], reverse=True)
        return [
            {
                "chunk_id": chunk.chunk_id,
                "page_number": chunk.page_number,
                "text": chunk.text,
                "retrieval_score": round(score, 4),
            }
            for score, chunk in scored_chunks[:top_k]
        ]

    def _build_embeddings_client(self):
        if self.settings.llm_provider.lower() == "azure":
            deployment = self.settings.azure_embedding_deployment or self.settings.embedding_model
            return AzureOpenAIEmbeddings(
                api_key=self.settings.model_api_key,
                azure_endpoint=self.settings.azure_endpoint,
                api_version=self.settings.azure_api_version,
                azure_deployment=deployment,
                model=self.settings.embedding_model,
            )

        return OpenAIEmbeddings(
            api_key=self.settings.model_api_key,
            base_url=self.settings.model_base_url,
            model=self.settings.embedding_model,
        )

    @staticmethod
    def _cosine_similarity(vector_a: list[float], vector_b: list[float]) -> float:
        dot_product = sum(a * b for a, b in zip(vector_a, vector_b, strict=False))
        norm_a = math.sqrt(sum(a * a for a in vector_a))
        norm_b = math.sqrt(sum(b * b for b in vector_b))
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot_product / (norm_a * norm_b)

    @staticmethod
    def _normalize(text: str) -> set[str]:
        return {token for token in re.findall(r"[a-zA-Z0-9']+", text.lower()) if len(token) > 2}
