# Tasks: Conversational Barbie PDF Assistant

**Input**: Design documents from `/specs/001-agentic-rag-app/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: No explicit TDD or test-first requirement was requested in the feature spec, so this task list focuses on implementation work. Validation is captured through independent test criteria, API contract alignment, and quickstart verification.

**Organization**: Tasks are grouped by user story to enable incremental delivery of the public-facing Barbie PDF assistant.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `backend/app/`, `backend/tests/`, `backend/data/`
- **Frontend**: `frontend/src/`, `frontend/tests/`
- **Feature docs**: `specs/001-agentic-rag-app/`

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Initialize the backend and frontend projects and baseline configuration files.

- [X] T001 Create the backend project manifest and dependency configuration in `backend/pyproject.toml`
- [X] T002 Create the frontend project manifest and scripts in `frontend/package.json`
- [X] T003 [P] Create the backend environment template for model, PDF, session, and rate-limit settings in `backend/.env.example`
- [X] T004 [P] Create the frontend environment template for API connectivity in `frontend/.env.example`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Build the shared application foundation that all user stories depend on.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [X] T005 Create the FastAPI application entrypoint and top-level router registration in `backend/app/main.py`
- [X] T006 [P] Implement shared backend settings and dependency helpers in `backend/app/core/config.py`
- [X] T007 [P] Define shared request and response schemas from the API contract in `backend/app/api/schemas/chat.py`
- [X] T008 [P] Implement anonymous session storage with expiry support in `backend/app/services/session_store.py`
- [X] T009 [P] Implement anonymous rate limiting with retry-after calculations in `backend/app/services/rate_limiter.py`
- [X] T010 Implement the PDF ingestion command and document metadata tracking in `backend/app/ingestion/build_index.py`
- [X] T011 Implement the persisted vector index loader and retriever abstraction in `backend/app/retrieval/vector_store.py`
- [X] T012 [P] Create the shared frontend API client for session and query requests in `frontend/src/services/api.ts`
- [X] T013 Create the root frontend application shell and chat page mount in `frontend/src/app/App.tsx`

**Checkpoint**: Foundation ready — user story implementation can begin.

---

## Phase 3: User Story 1 - Ask questions about the PDF (Priority: P1) 🎯 MVP

**Goal**: Let an anonymous public user ask a question about the Barbie PDF and receive a grounded answer or a clear insufficient-evidence response.

**Independent Test**: Start a session, submit a question answered by the Barbie PDF, and confirm the app returns a grounded answer; then submit an unsupported question and confirm the app responds with a clear insufficient-evidence message.

### Implementation for User Story 1

- [X] T014 [US1] Implement the LangGraph retrieval-and-answer workflow for grounded single-turn questions in `backend/app/graph/rag_graph.py`
- [X] T015 [US1] Implement the chat orchestration service for question handling and insufficient-evidence fallback in `backend/app/services/chat_service.py`
- [X] T016 [US1] Implement the health, session creation, and query API endpoints in `backend/app/api/routes/chat.py`
- [X] T017 [US1] Add backend validation to reject empty or whitespace-only questions in `backend/app/api/routes/chat.py`
- [X] T018 [P] [US1] Add frontend input validation and meaningful prompts for empty questions in `frontend/src/features/chat/components/ChatComposer.tsx`
- [X] T019 [US1] Implement document-unavailable and session error responses aligned to the API contract in `backend/app/api/routes/chat.py`
- [X] T020 [P] [US1] Build the chat composer and submit interaction for anonymous users in `frontend/src/features/chat/components/ChatComposer.tsx`
- [X] T021 [US1] Build the chat page flow with loading, answer, and error states in `frontend/src/features/chat/ChatPage.tsx`

**Checkpoint**: User Story 1 is functional as the MVP and can be demoed independently.

---

## Phase 4: User Story 2 - Verify answers with source evidence (Priority: P2)

**Goal**: Show users the supporting snippet text and page references used to justify each answer.

**Independent Test**: Ask a question with a known answer in the PDF and confirm the response shows supporting snippet text plus page references that match the source document.

### Implementation for User Story 2

- [X] T022 [US2] Implement page-aware evidence extraction and formatting for answered responses in `backend/app/services/evidence_formatter.py`
- [X] T023 [US2] Extend the query response schema to include serialized evidence items with page references in `backend/app/api/schemas/chat.py`
- [X] T024 [P] [US2] Build the evidence list component for snippet and page citation display in `frontend/src/features/chat/components/EvidenceList.tsx`
- [X] T025 [US2] Integrate evidence rendering into the main chat answer experience in `frontend/src/features/chat/ChatPage.tsx`

**Checkpoint**: User Stories 1 and 2 work together, and evidence can be verified independently by a reviewer.

---

## Phase 5: User Story 3 - Continue with follow-up questions (Priority: P3)

**Goal**: Preserve anonymous conversation context within the active session and allow users to start a new conversation that clears prior context.

**Independent Test**: Ask an initial question, follow with a context-dependent question in the same session, and confirm the answer reflects prior turns; then start a new conversation and confirm previous context is no longer used.

### Implementation for User Story 3

- [X] T026 [US3] Implement the conversation state model for session-scoped follow-up context in `backend/app/graph/conversation_state.py`
- [X] T027 [US3] Update chat orchestration to use session history and enforce session-only persistence rules in `backend/app/services/chat_service.py`
- [X] T028 [US3] Implement the conversation reset endpoint for starting a new session in `backend/app/api/routes/chat.py`
- [X] T029 [P] [US3] Build the new-conversation control for resetting anonymous chat state in `frontend/src/features/chat/components/NewConversationButton.tsx`
- [X] T030 [US3] Integrate follow-up and reset behavior into the chat page session flow in `frontend/src/features/chat/ChatPage.tsx`

**Checkpoint**: All user stories are functional, including follow-up questions and session reset behavior.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improve production readiness, clarity, and final validation across all user stories.

- [X] T031 [P] Add structured request logging and latency instrumentation in `backend/app/observability/logging.py`
- [X] T032 [P] Add reusable status messaging for rate limiting and document-unavailable states in `frontend/src/features/chat/components/ChatStatusBanner.tsx`
- [X] T033 Add API-layer `429` responses with `Retry-After` headers and contract-aligned error payloads in `backend/app/api/routes/chat.py`
- [X] T034 Measure representative query latency against the 5-second response target and document results in `specs/001-agentic-rag-app/quickstart.md`
- [X] T035 Validate and update the launch, smoke-test, and verification steps in `specs/001-agentic-rag-app/quickstart.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion — blocks all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational completion — establishes MVP chat flow
- **User Story 2 (Phase 4)**: Depends on User Story 1 because evidence display extends answered responses
- **User Story 3 (Phase 5)**: Depends on User Story 1 because follow-up context extends the base chat flow
- **Polish (Phase 6)**: Depends on completion of the user stories you plan to ship

### User Story Dependencies

- **US1 (P1)**: No dependency on other user stories
- **US2 (P2)**: Depends on US1 answer flow being present
- **US3 (P3)**: Depends on US1 session and query flow being present

### Within Each User Story

- Backend workflow/services before API wiring that depends on them
- Shared API contract updates before frontend rendering that consumes them
- UI components before page-level integration
- Complete the story checkpoint before moving to the next dependent story

### Parallel Opportunities

- **Setup**: T003 and T004 can run in parallel after T001 and T002 begin
- **Foundational**: T006, T007, T008, T009, and T012 can run in parallel once the project manifests exist
- **US1**: T014, T018, and T020 can run in parallel after Phase 2 completes
- **US2**: T022 and T024 can run in parallel after US1 is working
- **US3**: T026 and T029 can run in parallel after US1 is working
- **Polish**: T031 and T032 can run in parallel after core stories are complete

---

## Parallel Example: User Story 1

```bash
Task: "T014 [US1] Implement the LangGraph retrieval-and-answer workflow in backend/app/graph/rag_graph.py"
Task: "T018 [US1] Add frontend input validation in frontend/src/features/chat/components/ChatComposer.tsx"
Task: "T020 [US1] Build the chat composer in frontend/src/features/chat/components/ChatComposer.tsx"
```

## Parallel Example: User Story 2

```bash
Task: "T022 [US2] Implement evidence formatting in backend/app/services/evidence_formatter.py"
Task: "T024 [US2] Build the evidence list component in frontend/src/features/chat/components/EvidenceList.tsx"
```

## Parallel Example: User Story 3

```bash
Task: "T026 [US3] Implement conversation state in backend/app/graph/conversation_state.py"
Task: "T029 [US3] Build the new-conversation control in frontend/src/features/chat/components/NewConversationButton.tsx"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1
4. Validate the Phase 3 independent test before expanding scope
5. Demo or deploy the anonymous PDF Q&A MVP

### Incremental Delivery

1. Deliver US1 for question-answering MVP
2. Add US2 for trust and source verification
3. Add US3 for conversational follow-ups and reset behavior
4. Finish with polish tasks for observability, user messaging, latency validation, and quickstart validation

### Parallel Team Strategy

1. One developer handles backend foundation while another handles frontend foundation during Phase 2
2. After US1 lands, one developer can add backend evidence/session behavior while another adds frontend evidence/reset UI
3. Merge at story checkpoints to preserve independently testable increments

---

## Notes

- All tasks follow the required checklist format: checkbox, task ID, optional `[P]`, required `[US#]` for story tasks, and exact file path
- No explicit test tasks are listed because the feature spec did not request TDD; use each story’s independent test criteria plus `specs/001-agentic-rag-app/quickstart.md` for validation
- Keep the scope limited to the single `data/barbie.pdf` document source for this feature
- Avoid introducing accounts, multi-document upload, or cross-session memory during implementation
