# Data Model — Conversational Barbie PDF Assistant

## 1. DocumentSource
Represents the single PDF knowledge source used by the application.

### Fields
- `document_id`: stable identifier for the loaded source
- `source_path`: absolute repository path to `data/barbie.pdf`
- `display_name`: user-facing document name
- `checksum`: content hash used to detect when re-indexing is required
- `page_count`: total number of PDF pages
- `ingestion_status`: `pending | ready | failed`
- `last_indexed_at`: timestamp of most recent successful indexing

### Validation Rules
- `source_path` must point to the configured PDF file.
- `checksum` must change when the underlying PDF changes.
- `ingestion_status = ready` requires at least one chunk to exist.
- `ingestion_status = failed` requires an error reason to be logged.

### Relationships
- One `DocumentSource` has many `DocumentChunk` records.

### State Transitions
- `pending -> ready` after successful extraction, chunking, and indexing.
- `pending -> failed` if the PDF cannot be read or indexed.
- `failed -> pending` when a re-ingestion attempt starts.
- `ready -> pending` when the PDF changes and re-indexing is triggered.

## 2. DocumentChunk
Represents a retrievable segment of PDF content.

### Fields
- `chunk_id`: unique identifier for the chunk
- `document_id`: parent document reference
- `page_number`: source PDF page number
- `chunk_index`: ordinal within the page or extraction sequence
- `text`: extracted chunk content
- `token_count`: approximate token count for retrieval tuning
- `embedding_ref`: pointer or key for the stored embedding vector

### Validation Rules
- `text` must be non-empty after normalization.
- `page_number` must be within the document page range.
- `(document_id, page_number, chunk_index)` must be unique.
- `embedding_ref` must exist for indexed chunks.

### Relationships
- Many `DocumentChunk` records belong to one `DocumentSource`.
- One `DocumentChunk` can appear in many `RetrievedEvidence` items.

## 3. ConversationSession
Represents an anonymous user conversation with session-scoped memory only.

### Fields
- `session_id`: opaque unique session identifier
- `created_at`: session creation timestamp
- `last_activity_at`: timestamp of last accepted request
- `status`: `active | expired | reset`
- `question_count`: number of questions submitted during the session
- `client_fingerprint`: non-personal identifier used only for abuse protection heuristics

### Validation Rules
- `session_id` must be unique.
- `status = active` requires activity within the configured idle timeout.
- `question_count` increments only for accepted question submissions.
- Session data must be removed or invalidated on expiry or reset.

### Relationships
- One `ConversationSession` has many `MessageTurn` records.
- One `ConversationSession` can have many `RateLimitEvent` records.

### State Transitions
- `active -> expired` after inactivity timeout or backend restart.
- `active -> reset` when the user starts a new conversation.
- `reset -> active` only through creation of a new session identifier.

## 4. MessageTurn
Represents one user question or assistant answer in a conversation.

### Fields
- `turn_id`: unique identifier for the turn
- `session_id`: parent session reference
- `role`: `user | assistant`
- `content`: question text or answer text
- `created_at`: creation timestamp
- `response_status`: `accepted | answered | insufficient_evidence | error | rate_limited`
- `latency_ms`: end-to-end processing duration for assistant turns

### Validation Rules
- User turns must contain non-empty question content.
- Assistant turns with `answered` status must reference at least one evidence item.
- Assistant turns with `insufficient_evidence` must not claim unsupported facts.
- `latency_ms` is required for completed assistant turns.

### Relationships
- Many `MessageTurn` records belong to one `ConversationSession`.
- One assistant `MessageTurn` can have many `RetrievedEvidence` items.

## 5. RetrievedEvidence
Represents a document passage returned to justify an answer.

### Fields
- `evidence_id`: unique identifier for the evidence item
- `turn_id`: assistant turn reference
- `chunk_id`: source chunk reference
- `page_number`: cited PDF page number
- `snippet_text`: visible excerpt shown to the user
- `rank`: ordering among cited evidence items
- `retrieval_score`: normalized relevance score

### Validation Rules
- `snippet_text` must be non-empty.
- `page_number` must match the source chunk page.
- `rank` must be unique within an assistant turn.
- At least one `RetrievedEvidence` item is required for an `answered` assistant turn.

### Relationships
- Many `RetrievedEvidence` items belong to one assistant `MessageTurn`.
- Many `RetrievedEvidence` items can reference the same `DocumentChunk`.

## 6. RateLimitEvent
Represents a temporary abuse-protection event for anonymous traffic.

### Fields
- `event_id`: unique identifier for the throttle event
- `session_id`: optional related session reference
- `client_fingerprint`: client or IP-derived throttle key
- `triggered_at`: timestamp when the limit was exceeded
- `window_seconds`: length of the applied window
- `retry_after_seconds`: user-visible retry duration
- `reason`: short reason such as `per_ip_limit` or `per_session_limit`

### Validation Rules
- `retry_after_seconds` must be greater than zero.
- `reason` must map to a supported limiting rule.
- `client_fingerprint` must not store raw sensitive personal data beyond what is necessary for request protection.

### Relationships
- A `RateLimitEvent` can be associated with one `ConversationSession`.

## Relationship Summary
- `DocumentSource 1 -> N DocumentChunk`
- `ConversationSession 1 -> N MessageTurn`
- `MessageTurn 1 -> N RetrievedEvidence`
- `DocumentChunk 1 -> N RetrievedEvidence`
- `ConversationSession 1 -> N RateLimitEvent`
