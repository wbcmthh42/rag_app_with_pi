from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator


class SessionResponse(BaseModel):
    session_id: str
    expires_in_seconds: int = Field(gt=0)


class QueryRequest(BaseModel):
    session_id: str
    question: str = Field(min_length=1)

    @field_validator("question")
    @classmethod
    def validate_question(cls, value: str) -> str:
        trimmed = value.strip()
        if not trimmed:
            raise ValueError("Please enter a meaningful question.")
        return trimmed


class EvidenceItem(BaseModel):
    page_number: int = Field(ge=1)
    snippet_text: str
    retrieval_score: float | None = Field(default=None, ge=0, le=1)


class QueryResponse(BaseModel):
    session_id: str
    status: Literal["answered", "insufficient_evidence"]
    answer: str
    evidence: list[EvidenceItem]
    processing_ms: int = Field(ge=0)


class ErrorResponse(BaseModel):
    error_code: Literal[
        "invalid_request",
        "session_not_found",
        "session_expired",
        "document_unavailable",
        "rate_limited",
        "internal_error",
    ]
    message: str
    retry_after_seconds: int | None = Field(default=None, ge=1)
