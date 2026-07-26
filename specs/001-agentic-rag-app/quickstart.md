# Quickstart — Conversational Barbie PDF Assistant

## Prerequisites
- Python 3.11
- Node.js 20+
- Access to an OpenAI-compatible chat model and embedding model
- The source PDF at `/Users/johnnytay/Documents/Experimentations/experiment-spec-kit/data/barbie.pdf`

## 1. Backend setup
```bash
cd /Users/johnnytay/Documents/Experimentations/experiment-spec-kit/backend
python -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -e .
```

Create a `.env` file in `backend/` with values for:
```bash
MODEL_API_KEY=replace-me
MODEL_BASE_URL=https://api.example.com/v1
CHAT_MODEL=replace-me
EMBEDDING_MODEL=replace-me
PDF_SOURCE_PATH=/Users/johnnytay/Documents/Experimentations/experiment-spec-kit/data/barbie.pdf
VECTORSTORE_DIR=/Users/johnnytay/Documents/Experimentations/experiment-spec-kit/backend/data/vectorstore
SESSION_TTL_MINUTES=30
RATE_LIMIT_REQUESTS_PER_MINUTE=20
RATE_LIMIT_BURST=5
```

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
