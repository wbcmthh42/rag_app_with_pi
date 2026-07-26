from __future__ import annotations

from functools import lru_cache

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.responses import JSONResponse

from app.api.schemas.chat import ErrorResponse, QueryRequest, QueryResponse, SessionResponse
from app.core.config import Settings, get_settings
from app.services.chat_service import (
    ChatService,
    DocumentUnavailableError,
    LLMInvocationError,
    RateLimitExceededError,
    SessionExpiredError,
    SessionNotFoundError,
    build_chat_service,
)

router = APIRouter(tags=["chat"])


@lru_cache(maxsize=1)
def get_chat_service() -> ChatService:
    return build_chat_service(get_settings())


def client_key_from_request(request: Request) -> str:
    host = request.client.host if request.client else "anonymous"
    return f"ip:{host}"


@router.get("/health")
def health(service: ChatService = Depends(get_chat_service)) -> dict[str, str]:
    health_status = service.health()
    return {"status": health_status.status, "document_status": health_status.document_status}


@router.post("/chat/sessions", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
def create_session(service: ChatService = Depends(get_chat_service)) -> SessionResponse:
    return service.create_session()


@router.delete("/chat/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_session(session_id: str, service: ChatService = Depends(get_chat_service)) -> Response:
    try:
        service.reset_session(session_id)
    except SessionNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ErrorResponse(error_code="session_not_found", message="Session not found.").model_dump(),
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/chat/query", response_model=QueryResponse)
def submit_query(
    payload: QueryRequest,
    request: Request,
    service: ChatService = Depends(get_chat_service),
) -> QueryResponse:
    try:
        return service.ask(payload.session_id, payload.question, client_key_from_request(request))
    except DocumentUnavailableError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ErrorResponse(error_code="document_unavailable", message=str(exc)).model_dump(),
        )
    except SessionExpiredError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ErrorResponse(error_code="session_expired", message="Session expired. Start a new conversation.").model_dump(),
        )
    except SessionNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ErrorResponse(error_code="session_not_found", message="Session not found.").model_dump(),
        )
    except RateLimitExceededError as exc:
        error = ErrorResponse(
            error_code="rate_limited",
            message="Too many requests. Please try again later.",
            retry_after_seconds=exc.retry_after_seconds,
        )
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            headers={"Retry-After": str(exc.retry_after_seconds)},
            content=error.model_dump(),
        )
    except LLMInvocationError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=ErrorResponse(error_code="internal_error", message=exc.user_message).model_dump(),
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorResponse(error_code="invalid_request", message=str(exc)).model_dump(),
        )
