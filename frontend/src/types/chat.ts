export type QueryStatus = 'answered' | 'insufficient_evidence'

export interface SessionResponse {
  session_id: string
  expires_in_seconds: number
}

export interface EvidenceItem {
  page_number: number
  snippet_text: string
  retrieval_score?: number | null
}

export interface QueryResponse {
  session_id: string
  status: QueryStatus
  answer: string
  evidence: EvidenceItem[]
  processing_ms: number
}

export interface ApiErrorPayload {
  error_code: string
  message: string
  retry_after_seconds?: number
}

export interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  evidence?: EvidenceItem[]
  processingMs?: number
}
