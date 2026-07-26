# Implementation Plan: Conversational Barbie PDF Assistant

**Branch**: `[001-agentic-rag-app]` | **Date**: 2026-07-26 | **Spec**: [/Users/johnnytay/Documents/Experimentations/experiment-spec-kit/specs/001-agentic-rag-app/spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-agentic-rag-app/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Build a public-facing, anonymous document question-answering web app over the Barbie PDF. The system will use a React frontend and a FastAPI backend, with LangGraph orchestrating a retrieval-augmented answer flow that returns grounded answers, supporting snippet citations with page references, session-only follow-up context, and basic anonymous-user rate limiting.

## Technical Context

**Language/Version**: Python 3.11 (backend), TypeScript 5.x (frontend)  
**Primary Dependencies**: FastAPI, LangGraph, LangChain, pypdf, Chroma, React, Vite  
**Storage**: Local persisted vector index for PDF chunks; ephemeral in-memory session state and rate-limit counters  
**Testing**: pytest, httpx, pytest-asyncio, Vitest, React Testing Library, Playwright  
**Target Platform**: Linux-hosted web backend serving modern desktop and mobile browsers  
**Project Type**: Web application (frontend + backend API)  
**Performance Goals**: Return an initial answer or clear failure message within 5 seconds for 95% of representative questions; include source evidence with page references for at least 95% of answered questions  
**Constraints**: Single PDF only, anonymous public access, session-scoped conversation memory only, no account system, no cross-session persistence, page-referenced evidence required, basic per-user rate limiting required  
**Scale/Scope**: Single-document MVP; modest public traffic target of up to 50 concurrent active sessions and up to 10,000 questions per day on a single deployed environment

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Constitution status**: PASS — `.specify/memory/constitution.md` is still an unratified template with placeholder principles, so there are no enforceable project-specific gates yet.
- **Scope gate**: PASS — design remains bounded to a single PDF knowledge source and anonymous public Q&A.
- **Validation gate**: PASS — plan includes unit, integration, contract, and end-to-end testing coverage.
- **Operational gate**: PASS — rate limiting, error handling, and observability hooks are included in the design.
- **Post-design re-check**: PASS — Phase 1 artifacts define data model, API contracts, and runbook-style quickstart guidance without introducing constitution violations.

## Project Structure

### Documentation (this feature)

```text
specs/001-agentic-rag-app/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── openapi.yaml
└── tasks.md
```

### Source Code (repository root)

```text
backend/
├── app/
│   ├── api/
│   │   ├── routes/
│   │   └── schemas/
│   ├── core/
│   ├── graph/
│   ├── ingestion/
│   ├── retrieval/
│   ├── services/
│   └── observability/
├── data/
│   └── vectorstore/
├── tests/
│   ├── contract/
│   ├── integration/
│   └── unit/
└── pyproject.toml

frontend/
├── src/
│   ├── app/
│   ├── components/
│   ├── features/chat/
│   ├── services/
│   └── types/
├── tests/
│   ├── component/
│   └── e2e/
└── package.json

data/
└── barbie.pdf
```

**Structure Decision**: Use a two-project web application structure with separate `backend/` and `frontend/` directories. This cleanly isolates LangGraph/FastAPI orchestration concerns from the browser UI while keeping contracts and test boundaries explicit for a public-facing app.

## Complexity Tracking

No constitution violations or justified complexity exceptions were identified for this plan.
