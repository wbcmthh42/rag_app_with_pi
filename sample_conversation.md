# Sample Conversation: Zero-Shot Spec-Kit Workflow for This RAG App

This file shows a **minimal back-and-forth**, **copy-paste-friendly** workflow for building this app with Spec-Kit.

Reference:
- Pi Spec-Kit package: https://pi.dev/packages/@the-agency/pi-spec-kit?page=46

Goal: create a **public-facing agentic RAG web app** over `data/barbie.pdf` using:
- **LangGraph**
- **FastAPI** backend
- **React/Vite** frontend
- **Azure OpenAI** for chat + embeddings
- **uv** for Python dependency management
- **pinned Python package versions** in `pyproject.toml`
- **anonymous sessions**
- **page-referenced evidence**
- **session-only memory**
- **basic rate limiting**
- **LLM-powered greetings/small-talk**

---

## Recommended One-Time Repo Prerequisites

Before running the Spec-Kit commands, make sure:

1. The repo is a git repo:
```bash
git init
```

2. `.specify/` is initialized:
```text
/speckit-init
```

3. Make an initial commit **before** some workflows that depend on git branch/HEAD state:
```bash
git add .
git commit -m "Initialize spec-kit workspace"
```

4. Start feature work from a feature branch like:
```bash
git checkout -b 001-agentic-rag-app
```

---

# 1) One-time setup per repo

## Command
```text
/speckit-init
```

## User instruction to provide
Use exactly this if needed:

```text
Initialize .specify for this repository and update AGENTS.md with the Spec-Kit section.
```

## Expected result
- `.specify/` created
- `AGENTS.md` updated

---

# 2) Write the spec for a new feature

## Command
```text
/speckit-specify
```

## User instruction to provide
Use this **exact prompt** to reduce ambiguity and avoid too much clarification later:

```text
Build a public-facing agentic RAG web app over the PDF at /Users/johnnytay/Documents/Experimentations/experiment-spec-kit/data/barbie.pdf.

The app must have:
- a React/Vite frontend
- a FastAPI backend
- LangGraph orchestration for retrieval + answer flow
- Azure OpenAI for chat generation and embeddings
- uv for Python dependency management
- pinned Python package versions in pyproject.toml
- a uv.lock file generated during implementation
- anonymous public access with no sign-in
- session-only conversation memory
- no cross-session persistence
- support for follow-up questions within the same active session
- a “new conversation” action that resets prior context
- visible source evidence for each answer, including snippet text and page references
- clear insufficient-evidence behavior instead of hallucination
- user-friendly loading and error states
- rejection of empty or whitespace-only questions
- basic per-user rate limiting with a clear “try again later” message
- LLM-powered greeting and small-talk support (for example: “Hi”, “Hello”, “What can you do?”), while still steering users back to questions about the Barbie PDF
- scope limited to this single PDF only; no document upload, multi-document search, user accounts, or personalization

Success criteria:
- at least 90% of questions with answers clearly present in the PDF should return correct grounded answers
- at least 95% of answered questions should include visible supporting evidence with page references
- users should receive an answer or a clear failure message within 5 seconds for 95% of representative questions
- unsupported questions must return an insufficient-evidence style response instead of fabricated answers

Assume these defaults unless there is a hard blocker:
- browser-based app
- Linux-hosted backend
- moderate public traffic
- Azure OpenAI deployment names will be configured through backend environment variables
- retrieval should use embeddings, not only keyword overlap
```

## Why this works
This prompt already answers the most common clarification questions:
- who can access it
- whether sign-in is required
- how memory works
- whether source evidence is needed
- whether rate limiting is required
- whether greetings should work
- what is out of scope
- what success looks like

---

# 3) Analyze the spec and resolve ambiguities

## Command
```text
/speckit-clarify
```

## User instruction to provide
Use this:

```text
Assume the spec is intended to be implementation-ready. Only ask a clarification question if it materially changes scope, UX, security, data flow, or testing. Otherwise keep the defaults already stated in the spec.
```

## If you want to minimize interaction even further
Use this instead:

```text
Use the spec as the source of truth and avoid asking follow-up questions unless something is truly blocking correctness. Keep these defaults fixed:
- public anonymous access
- no sign-in
- session-only memory
- no cross-session persistence
- snippet text plus page references
- basic rate limiting
- Azure OpenAI for chat and embeddings
- single PDF only
- LLM should handle greetings and small-talk
```

## Goal
Ideally `/speckit-clarify` should return with either:
- no critical ambiguities, or
- very few questions

---

# 4) Create the technical plan

## Command
```text
/speckit-plan
```

## User instruction to provide
Use this:

```text
Create the implementation plan for this feature using:
- Python 3.11 backend managed with uv
- pinned Python dependencies in pyproject.toml and a generated uv.lock
- FastAPI
- LangGraph
- React + Vite frontend
- Azure OpenAI for chat generation and embeddings
- local persisted vector index for the single PDF
- anonymous in-memory session store with expiry
- basic per-IP and per-session rate limiting
- API contracts for session creation, query submission, health, and conversation reset
- frontend and backend separated into frontend/ and backend/
```

## Goal
This reduces plan-time guesswork about:
- language/runtime
- project structure
- model provider
- storage style
- frontend stack

---

# 5) Break the plan down into tasks

## Command
```text
/speckit-tasks
```

## User instruction to provide
Use this:

```text
Generate an executable tasks.md organized by user story for this app. Include tasks for:
- backend setup with uv
- pinned Python dependencies in pyproject.toml
- generation of uv.lock
- frontend setup
- Azure OpenAI configuration support
- embedding-based indexing of the Barbie PDF
- vector similarity retrieval
- LangGraph answer flow
- FastAPI session/query/reset endpoints
- anonymous session memory
- rate limiting
- evidence snippet + page reference rendering
- LLM-powered greeting/small-talk handling
- user-friendly error and loading states
- quickstart validation

Keep the task list implementation-ready with exact file paths.
```

## Goal
Make sure tasks explicitly include:
- Azure chat support
- Azure embeddings support
- greeting/small-talk support
- frontend error handling
- quickstart verification

---

# 6) Consistency check before coding

## Command
```text
/speckit-analyze
```

## User instruction to provide
Use this:

```text
Run a consistency and coverage analysis across spec.md, plan.md, and tasks.md. Focus on missing task coverage for non-functional requirements, Azure configuration, embeddings retrieval, greeting/small-talk behavior, error handling, and latency validation.
```

## Goal
Catch issues like:
- missing Azure support tasks
- missing empty-input handling
- missing latency validation
- missing retrieval coverage
- task/spec mismatch

---

# 7) Execute the tasks

## Command
```text
/speckit-implement
```

## User instruction to provide
Use this:

```text
Implement the full feature phase by phase from tasks.md. Keep the architecture aligned with the plan. Use Azure OpenAI for chat and embeddings, use uv for Python dependency management, pin Python package versions in pyproject.toml, generate uv.lock, keep session memory anonymous and session-scoped, preserve single-PDF scope, ensure greeting/small-talk is LLM-driven while document questions use RAG retrieval, and add a root README.md that documents setup, usage, and architecture with at least one Mermaid diagram.
```

## Optional stronger version
If you want the implementation instruction to be even more explicit, use:

```text
Implement all tasks in tasks.md. Requirements that must not be dropped:
- React/Vite frontend
- FastAPI backend
- LangGraph orchestration
- Azure OpenAI native support
- uv-managed Python dependencies
- pinned Python versions in pyproject.toml
- generated uv.lock
- embedding-based retrieval over data/barbie.pdf
- source evidence with snippet text and page references
- anonymous public access
- session-only conversation memory
- no cross-session persistence
- new conversation reset
- rejection of empty input
- basic rate limiting
- LLM-generated greeting/small-talk support
- user-friendly error handling
- quickstart validation
```

---

# Recommended Minimal End-to-End Command Sequence

Use this exact sequence for the cleanest run:

```text
/speckit-init
```

```text
/speckit-specify
```
Paste the long spec prompt from section 2.

```text
/speckit-clarify
```
Paste the prompt from section 3.

```text
/speckit-plan
```
Paste the prompt from section 4.

```text
/speckit-tasks
```
Paste the prompt from section 5.

```text
/speckit-analyze
```
Paste the prompt from section 6.

```text
/speckit-implement
```
Paste the prompt from section 7.

---

# Ultra-Compact Version

If you want the shortest possible user instructions for each command:

## `/speckit-specify`
```text
Create a public anonymous agentic RAG app over data/barbie.pdf with React/Vite frontend, FastAPI backend, LangGraph orchestration, Azure OpenAI chat + embeddings, session-only memory, evidence snippets with page references, rate limiting, empty-input rejection, new conversation reset, and LLM-powered greetings/small-talk.
```

## `/speckit-clarify`
```text
Use the spec defaults unless a clarification is truly blocking correctness.
```

## `/speckit-plan`
```text
Plan this using Python 3.11 managed with uv, pinned dependencies in pyproject.toml plus uv.lock, FastAPI, LangGraph, React/Vite, Azure OpenAI, local vector index, and separated frontend/backend structure.
```

## `/speckit-tasks`
```text
Generate implementation-ready tasks for uv setup, pinned pyproject.toml dependencies, uv.lock generation, Azure chat + embeddings, vector retrieval, LangGraph flow, FastAPI APIs, frontend chat UX, evidence rendering, rate limiting, session memory, and greeting/small-talk support.
```

## `/speckit-analyze`
```text
Check for missing coverage across Azure config, embeddings retrieval, greeting support, latency validation, and error handling.
```

## `/speckit-implement`
```text
Implement the full app from tasks.md with uv-managed Python dependencies, pinned pyproject.toml versions, a generated uv.lock, Azure-powered chat and embeddings, single-PDF RAG, anonymous session memory, LLM-driven greetings, and a README.md with a Mermaid architecture or flow diagram.
```

---

# Notes

- If the repo has no commits yet, make an initial git commit before workflows that depend on branch/HEAD state.
- Keep real secrets only in `backend/.env`, never in `backend/.env.example`.
- If you want truly low back-and-forth, put all critical defaults into the initial `/speckit-specify` prompt.
- The more precise the `/speckit-specify` prompt is, the less `/speckit-clarify` will need to ask.
- If you want documentation generated as part of the zero-shot flow, explicitly mention it in `/speckit-implement` (for example: create a root README.md with setup, usage, and Mermaid diagrams).
