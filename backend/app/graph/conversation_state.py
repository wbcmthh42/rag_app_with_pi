from __future__ import annotations

from typing import Literal, TypedDict


class RetrievedChunk(TypedDict):
    chunk_id: str
    page_number: int
    text: str
    retrieval_score: float


class ConversationState(TypedDict, total=False):
    session_id: str
    question: str
    history: list[dict[str, str]]
    retrieved_chunks: list[RetrievedChunk]
    answer: str
    status: Literal["answered", "insufficient_evidence"]
    evidence: list[dict[str, object]]
    processing_ms: int
