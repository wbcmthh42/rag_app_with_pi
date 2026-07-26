# Phase 0 Research — Conversational Barbie PDF Assistant

## Decision 1: Use Python 3.11 for the backend and TypeScript 5.x for the frontend
- **Decision**: Implement the backend in Python 3.11 and the frontend in TypeScript 5.x.
- **Rationale**: Python provides the strongest ecosystem fit for LangGraph, LangChain, PDF ingestion, and retrieval pipelines. TypeScript improves UI reliability and API contract alignment for a public-facing frontend.
- **Alternatives considered**:
  - JavaScript-only full stack — rejected because LangGraph and document-processing ergonomics are stronger in Python.
  - Python-only server-rendered UI — rejected because the requested slick frontend experience benefits from a dedicated client app.

## Decision 2: Use FastAPI as the public backend interface and LangGraph as the orchestration layer
- **Decision**: Expose a REST API through FastAPI and implement the retrieval-and-answer workflow as a LangGraph graph.
- **Rationale**: FastAPI gives a clean contract surface for the frontend, while LangGraph is well-suited for multi-step retrieval, answer synthesis, follow-up handling, and future extensibility.
- **Alternatives considered**:
  - Plain FastAPI service functions without graph orchestration — rejected because conversational retrieval workflows and future branching logic are easier to evolve in a graph structure.
  - GraphQL — rejected because the interaction model is command-style chat, which fits a simpler REST contract.

## Decision 3: Build the frontend with React + Vite
- **Decision**: Use React with Vite for the browser client.
- **Rationale**: React supports responsive conversational UI patterns, and Vite provides a lightweight setup suitable for a small-to-medium single-page application.
- **Alternatives considered**:
  - Next.js — rejected because server-side rendering is unnecessary for this MVP and would add deployment complexity.
  - Plain HTML/JavaScript — rejected because maintaining a polished, stateful chat UI would be harder over time.

## Decision 4: Use offline PDF ingestion with page-aware chunking and a persisted local Chroma vector index
- **Decision**: Extract text from `data/barbie.pdf`, chunk it with page metadata, generate embeddings, and persist the vector index locally in the backend data directory using Chroma.
- **Rationale**: The app is intentionally scoped to one static PDF, so an offline index keeps query-time latency low and simplifies repeatable deployments. Page metadata directly supports the citation requirement.
- **Alternatives considered**:
  - Re-parse the PDF on every request — rejected due to slower responses and unnecessary repeated work.
  - FAISS — rejected because it is a good option but offers less convenient local persistence out of the box for this MVP.
  - Remote hosted vector database — rejected because it adds infrastructure overhead without clear need for a single-document MVP.

## Decision 5: Keep anonymous conversation memory in an in-memory session store with expiration
- **Decision**: Maintain follow-up context in a backend-managed in-memory session store keyed by session ID, with expiration based on inactivity.
- **Rationale**: This matches the clarified requirement for session-only memory and avoids persisting anonymous user history across refreshes or later visits.
- **Alternatives considered**:
  - Persisting sessions in a database — rejected because the spec explicitly excludes cross-session persistence in the initial release.
  - Browser-only memory — rejected because the backend still needs prior turns to drive contextual retrieval and answer generation.
  - Redis — rejected for the MVP because it introduces extra infrastructure before scale requires it.

## Decision 6: Apply lightweight anonymous-user abuse protection with per-IP and per-session limits
- **Decision**: Enforce basic request throttling using per-IP and per-session counters, returning a clear temporary backoff message when limits are exceeded.
- **Rationale**: The app is public and anonymous, so some abuse protection is required to protect availability without adding sign-in friction.
- **Alternatives considered**:
  - No rate limiting — rejected because it leaves the public app vulnerable to trivial abuse.
  - Mandatory authentication — rejected because it conflicts with the clarified anonymous access requirement.
  - Global shutdown during high load — rejected because it degrades experience for all users rather than isolating abusive traffic.

## Decision 7: Return answer payloads with evidence snippets and page references
- **Decision**: Each successful answer response will include supporting evidence snippets and page numbers in the API payload.
- **Rationale**: This directly satisfies the trust and verifiability requirements and makes the contract testable.
- **Alternatives considered**:
  - Page numbers only — rejected because users would need to manually hunt for the relevant passage.
  - Raw citations hidden from users — rejected because the spec requires visible supporting evidence.

## Decision 8: Use a hybrid test strategy across unit, integration, contract, and browser end-to-end tests
- **Decision**: Validate ingestion, retrieval, graph behavior, API contracts, and the primary chat flow with layered automated tests.
- **Rationale**: The feature spans a browser UI, a public API, document retrieval, and session behavior. A single testing layer would miss important failures.
- **Alternatives considered**:
  - Unit tests only — rejected because contract mismatches and UX regressions would go undetected.
  - End-to-end tests only — rejected because failures would be harder to localize and slower to debug.

## Decision 9: Use an environment-configured OpenAI-compatible chat and embedding provider for the initial implementation
- **Decision**: Integrate the backend with an OpenAI-compatible provider through LangChain abstractions for both chat completion and embedding generation.
- **Rationale**: This keeps implementation velocity high, aligns with mature LangChain integrations, and preserves the option to swap providers later behind a narrow adapter boundary.
- **Alternatives considered**:
  - Local-only models — rejected for the initial MVP because setup complexity and performance variance are higher.
  - Provider-specific coupling everywhere — rejected because it would make later changes harder.
