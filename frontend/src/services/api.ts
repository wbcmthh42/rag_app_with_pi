import type { ApiErrorPayload, QueryResponse, SessionResponse } from '../types/chat'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000/api/v1'

export class ApiError extends Error {
  payload: ApiErrorPayload

  constructor(payload: ApiErrorPayload) {
    super(payload.message)
    this.payload = payload
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      'Content-Type': 'application/json',
      ...(init?.headers ?? {}),
    },
    ...init,
  })

  if (!response.ok) {
    const payload = (await response.json()) as ApiErrorPayload
    throw new ApiError(payload)
  }

  if (response.status === 204) {
    return undefined as T
  }

  return (await response.json()) as T
}

export function createSession(): Promise<SessionResponse> {
  return request<SessionResponse>('/chat/sessions', { method: 'POST' })
}

export function submitQuery(sessionId: string, question: string): Promise<QueryResponse> {
  return request<QueryResponse>('/chat/query', {
    method: 'POST',
    body: JSON.stringify({ session_id: sessionId, question }),
  })
}

export function resetSession(sessionId: string): Promise<void> {
  return request<void>(`/chat/sessions/${sessionId}`, { method: 'DELETE' })
}
