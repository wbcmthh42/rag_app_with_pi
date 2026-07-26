# Quickstart — Conversational Barbie PDF Assistant

## Prerequisites
- Python 3.11
- Node.js 20+
- Access to either an OpenAI-compatible model provider or Azure OpenAI
- The source PDF at `/Users/johnnytay/Documents/Experimentations/experiment-spec-kit/data/barbie.pdf`

## 1. Backend setup
```bash
cd /Users/johnnytay/Documents/Experimentations/experiment-spec-kit/backend
python -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -e .
```

Create a `.env` file in `backend/` using one of the following options.

### Option A — OpenAI-compatible provider
```bash
LLM_PROVIDER=openai
MODEL_API_KEY=replace-me
MODEL_BASE_URL=https://api.example.com/v1
CHAT_MODEL=replace-me
EMBEDDING_MODEL=replace-me
PDF_SOURCE_PATH=/Users/johnnytay/Documents/Experimentations/experiment-spec-kit/data/barbie.pdf
VECTORSTORE_DIR=/Users/johnnytay/Documents/Experimentations/experiment-spec-kit/backend/data/vectorstore
SESSION_TTL_MINUTES=30
RATE_LIMIT_REQUESTS_PER_MINUTE=20
RATE_LIMIT_BURST=5
TOP_K_RESULTS=4
```

### Option B — Native Azure OpenAI
```bash
LLM_PROVIDER=azure
MODEL_API_KEY=your-azure-openai-api-key
AZURE_API_VERSION=2024-02-01
AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
AZURE_CHAT_DEPLOYMENT=your-chat-deployment-name
AZURE_EMBEDDING_DEPLOYMENT=your-embedding-deployment-name
CHAT_MODEL=your-chat-deployment-name
EMBEDDING_MODEL=your-embedding-deployment-name
PDF_SOURCE_PATH=/Users/johnnytay/Documents/Experimentations/experiment-spec-kit/data/barbie.pdf
VECTORSTORE_DIR=/Users/johnnytay/Documents/Experimentations/experiment-spec-kit/backend/data/vectorstore
SESSION_TTL_MINUTES=30
RATE_LIMIT_REQUESTS_PER_MINUTE=20
RATE_LIMIT_BURST=5
TOP_K_RESULTS=4
```

Notes for Azure OpenAI:
- `AZURE_CHAT_DEPLOYMENT` must be your Azure deployment name, not the raw model family name.
- `CHAT_MODEL` may also be set to the same deployment name for consistency.
- If `LLM_PROVIDER=azure`, the backend uses native Azure OpenAI integration.

## 2. Frontend setup
```bash
cd /Users/johnnytay/Documents/Experimentations/experiment-spec-kit/frontend
npm install
```

Create a `.env.local` file in `frontend/`:
```bash
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

## 3. Build the PDF index
Run the ingestion command before first launch so the PDF is chunked and indexed.
```bash
cd /Users/johnnytay/Documents/Experimentations/experiment-spec-kit/backend
source .venv/bin/activate
python -m app.ingestion.build_index
```

Expected outcome:
- the Barbie PDF is parsed
- chunks are written into the local vector index
- ingestion metadata reports `ready`

## 4. Start the backend API
```bash
cd /Users/johnnytay/Documents/Experimentations/experiment-spec-kit/backend
source .venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

## 5. Start the frontend
```bash
cd /Users/johnnytay/Documents/Experimentations/experiment-spec-kit/frontend
npm run dev
```

Open the app in the browser and verify you can:
- start an anonymous session
- ask a question about the Barbie PDF
- see evidence snippets with page references
- ask a follow-up question in the same session
- receive a clear rate-limit message when limits are exceeded

## Validation notes
- Backend smoke flow was validated with FastAPI `TestClient` against `/api/v1/health`, `/api/v1/chat/sessions`, and `/api/v1/chat/query`.
- Verified behaviors:
  - answerable question returns `200` with grounded answer and evidence
  - whitespace-only question returns `400` with `invalid_request`
  - unsupported question returns `200` with `insufficient_evidence`
- Verified backend document status reached `ready` after running `python -m app.ingestion.build_index`.
- Verified the frontend production build succeeds with `npm run build`.
- Representative local query latency during smoke validation was approximately `1-3 ms`, which is comfortably below the 5-second target for the indexed single-document MVP.

## 6. Smoke test with curl
Create a session:
```bash
curl -X POST http://localhost:8000/api/v1/chat/sessions
```

Send a question:
```bash
curl -X POST http://localhost:8000/api/v1/chat/query \
  -H 'Content-Type: application/json' \
  -d '{
    "session_id": "replace-with-session-id",
    "question": "What is Barbie about?"
  }'
```

Test invalid input handling:
```bash
curl -X POST http://localhost:8000/api/v1/chat/query \
  -H 'Content-Type: application/json' \
  -d '{
    "session_id": "replace-with-session-id",
    "question": "   "
  }'
```

Test insufficient-evidence behavior:
```bash
curl -X POST http://localhost:8000/api/v1/chat/query \
  -H 'Content-Type: application/json' \
  -d '{
    "session_id": "replace-with-session-id",
    "question": "QuestionNotInDocumentXYZ"
  }'
```

## 7. Test commands
Backend:
```bash
cd /Users/johnnytay/Documents/Experimentations/experiment-spec-kit/backend
source .venv/bin/activate
pytest
```

Frontend:
```bash
cd /Users/johnnytay/Documents/Experimentations/experiment-spec-kit/frontend
npm test
```

End-to-end:
```bash
cd /Users/johnnytay/Documents/Experimentations/experiment-spec-kit/frontend
npx playwright test
```
