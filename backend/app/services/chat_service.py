from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter
from typing import Any
import re

from langchain_openai import AzureChatOpenAI, ChatOpenAI
from openai import APIConnectionError, APITimeoutError, AuthenticationError, BadRequestError, NotFoundError, RateLimitError

from app.api.schemas.chat import EvidenceItem, QueryResponse, SessionResponse
from app.core.config import Settings
from app.graph.rag_graph import build_rag_graph
from app.observability.logging import get_logger
from app.retrieval.vector_store import DocumentUnavailableError, VectorStore
from app.services.session_store import SessionExpiredError, SessionNotFoundError, SessionStore
from app.services.rate_limiter import RateLimiter

logger = get_logger(__name__)


class RateLimitExceededError(Exception):
    def __init__(self, retry_after_seconds: int) -> None:
        self.retry_after_seconds = retry_after_seconds
        super().__init__("Too many requests. Please try again later.")


class LLMInvocationError(Exception):
    def __init__(self, user_message: str) -> None:
        self.user_message = user_message
        super().__init__(user_message)


@dataclass
class HealthStatus:
    status: str
    document_status: str


class ChatService:
    def __init__(
        self,
        settings: Settings,
        session_store: SessionStore,
        rate_limiter: RateLimiter,
        vector_store: VectorStore,
    ) -> None:
        self.settings = settings
        self.session_store = session_store
        self.rate_limiter = rate_limiter
        self.vector_store = vector_store
        self._graph = build_rag_graph(self._retrieve, self._answer_question)

    def health(self) -> HealthStatus:
        return HealthStatus(status="ok", document_status=self.vector_store.get_document_status())

    def create_session(self) -> SessionResponse:
        session = self.session_store.create_session()
        return SessionResponse(session_id=session.session_id, expires_in_seconds=self.session_store.expires_in_seconds())

    def reset_session(self, session_id: str) -> None:
        self.session_store.reset_session(session_id)

    def ask(self, session_id: str, question: str, client_key: str) -> QueryResponse:
        self._check_rate_limit(client_key, session_id)
        session = self.session_store.get_session(session_id)

        started = perf_counter()
        self.session_store.append_turn(session_id, "user", question)
        result = self._graph.invoke(
            {
                "session_id": session_id,
                "question": question,
                "history": list(session.history),
            }
        )
        processing_ms = max(int((perf_counter() - started) * 1000), int(result.get("processing_ms", 0)))

        self.session_store.append_turn(session_id, "assistant", result["answer"])
        logger.info("Processed question", extra={"session_id": session_id, "status": result["status"], "processing_ms": processing_ms})
        return QueryResponse(
            session_id=session_id,
            status=result["status"],
            answer=result["answer"],
            evidence=[EvidenceItem(**item) for item in result.get("evidence", [])],
            processing_ms=processing_ms,
        )

    def _check_rate_limit(self, client_key: str, session_id: str) -> None:
        for key in {client_key, f"session:{session_id}"}:
            result = self.rate_limiter.check(key)
            if not result.allowed:
                raise RateLimitExceededError(result.retry_after_seconds)

    def _retrieve(self, question: str) -> list[dict[str, Any]]:
        return self.vector_store.retrieve(question, top_k=self.settings.top_k_results)

    def _answer_question(
        self,
        question: str,
        history: list[dict[str, str]],
        retrieved_chunks: list[dict[str, Any]],
    ) -> tuple[str, str]:
        if self._is_smalltalk(question):
            return self._answer_smalltalk(question, history), "answered"

        if not retrieved_chunks:
            return (
                "I couldn’t find enough evidence in the Barbie PDF to answer that confidently.",
                "insufficient_evidence",
            )

        context = "\n\n".join(
            f"Page {chunk['page_number']}: {chunk['text']}" for chunk in retrieved_chunks
        )
        history_text = "\n".join(f"{item['role']}: {item['content']}" for item in history[-6:])

        if self.settings.model_api_key and self.settings.model_api_key != "replace-me":
            llm = self._build_llm_client()
            prompt = (
                "You are answering questions only from the provided Barbie PDF context. "
                "If the answer is not supported, say so clearly.\n\n"
                f"Conversation history:\n{history_text or 'None'}\n\n"
                f"Context:\n{context}\n\n"
                f"Question: {question}"
            )
            try:
                response = llm.invoke(prompt)
            except AuthenticationError as exc:
                provider = "Azure OpenAI" if self.settings.llm_provider.lower() == "azure" else "the model provider"
                raise LLMInvocationError(f"Authentication with {provider} failed. Check your API key.") from exc
            except NotFoundError as exc:
                if self.settings.llm_provider.lower() == "azure":
                    raise LLMInvocationError("Azure OpenAI deployment was not found. Check AZURE_CHAT_DEPLOYMENT.") from exc
                raise LLMInvocationError("The configured model deployment was not found.") from exc
            except BadRequestError as exc:
                if self.settings.llm_provider.lower() == "azure":
                    raise LLMInvocationError("Azure OpenAI rejected the request. Check AZURE_API_VERSION, deployment names, and model compatibility.") from exc
                raise LLMInvocationError("The model provider rejected the request. Check the model configuration.") from exc
            except (APIConnectionError, APITimeoutError) as exc:
                if self.settings.llm_provider.lower() == "azure":
                    raise LLMInvocationError("Azure OpenAI could not be reached. Check AZURE_OPENAI_ENDPOINT and network access.") from exc
                raise LLMInvocationError("The model provider could not be reached. Please try again later.") from exc
            except RateLimitError as exc:
                if self.settings.llm_provider.lower() == "azure":
                    raise LLMInvocationError("Azure OpenAI rate limit reached. Please try again shortly.") from exc
                raise LLMInvocationError("The model provider rate limit was reached. Please try again shortly.") from exc
            except Exception as exc:
                if self.settings.llm_provider.lower() == "azure":
                    raise LLMInvocationError("Azure OpenAI request failed unexpectedly. Verify your Azure endpoint, API version, and deployment settings.") from exc
                raise LLMInvocationError("The model provider failed unexpectedly. Please verify the backend model configuration.") from exc
            return str(response.content).strip(), "answered"

        top_chunk = retrieved_chunks[0]
        answer = (
            f"Based on the Barbie PDF, here is the most relevant passage I found: "
            f"{top_chunk['text'][:320].strip()}"
        )
        return answer, "answered"

    def _is_smalltalk(self, question: str) -> bool:
        normalized = re.sub(r"\s+", " ", question.strip().lower())
        return normalized in {
            "hi",
            "hello",
            "hey",
            "yo",
            "hiya",
            "good morning",
            "good afternoon",
            "good evening",
            "thanks",
            "thank you",
            "thx",
            "who are you",
            "what can you do",
            "help",
        }

    def _answer_smalltalk(self, question: str, history: list[dict[str, str]]) -> str:
        history_text = "\n".join(f"{item['role']}: {item['content']}" for item in history[-6:])
        if self.settings.model_api_key and self.settings.model_api_key != "replace-me":
            llm = self._build_llm_client()
            prompt = (
                "You are a friendly conversational assistant for a Barbie PDF question-answering app. "
                "Respond naturally to greetings or lightweight small-talk, but keep the reply brief and steer the user back toward asking about the Barbie PDF.\n\n"
                f"Conversation history:\n{history_text or 'None'}\n\n"
                f"User message: {question}"
            )
            try:
                response = llm.invoke(prompt)
                return str(response.content).strip()
            except Exception:
                pass

        normalized = re.sub(r"\s+", " ", question.strip().lower())
        if normalized in {"thanks", "thank you", "thx"}:
            return "You’re welcome! Ask me anything about the Barbie PDF."
        return "Hi! Ask me anything about the Barbie PDF, and I’ll answer using the document."

    def _build_llm_client(self):
        if self.settings.llm_provider.lower() == "azure":
            deployment = self.settings.azure_chat_deployment or self.settings.chat_model
            if not self.settings.azure_endpoint:
                raise LLMInvocationError("AZURE_OPENAI_ENDPOINT must be set when LLM_PROVIDER=azure.")
            return AzureChatOpenAI(
                api_key=self.settings.model_api_key,
                azure_endpoint=self.settings.azure_endpoint,
                api_version=self.settings.azure_api_version,
                azure_deployment=deployment,
                temperature=0,
            )

        return ChatOpenAI(
            api_key=self.settings.model_api_key,
            base_url=self.settings.model_base_url,
            model=self.settings.chat_model,
            temperature=0,
        )


def build_chat_service(settings: Settings) -> ChatService:
    return ChatService(
        settings=settings,
        session_store=SessionStore(ttl_minutes=settings.session_ttl_minutes),
        rate_limiter=RateLimiter(
            requests_per_minute=settings.rate_limit_requests_per_minute,
            burst=settings.rate_limit_burst,
        ),
        vector_store=VectorStore(settings),
    )


__all__ = [
    "ChatService",
    "HealthStatus",
    "RateLimitExceededError",
    "LLMInvocationError",
    "DocumentUnavailableError",
    "SessionNotFoundError",
    "SessionExpiredError",
    "build_chat_service",
]
