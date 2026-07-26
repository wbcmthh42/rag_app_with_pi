import { useEffect, useMemo, useState } from 'react'

import ChatComposer from './components/ChatComposer'
import ChatStatusBanner from './components/ChatStatusBanner'
import EvidenceList from './components/EvidenceList'
import NewConversationButton from './components/NewConversationButton'
import { ApiError, createSession, resetSession, submitQuery } from '../../services/api'
import type { ChatMessage } from '../../types/chat'

function messageId() {
  return `msg-${crypto.randomUUID()}`
}

export default function ChatPage() {
  const [sessionId, setSessionId] = useState<string | null>(null)
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [banner, setBanner] = useState<{ tone: 'info' | 'error' | 'success'; message: string } | null>({
    tone: 'info',
    message: 'Starting an anonymous session…',
  })

  useEffect(() => {
    void initializeSession()
  }, [])

  async function initializeSession(message = 'Anonymous session ready. Ask about the Barbie PDF.') {
    try {
      const session = await createSession()
      setSessionId(session.session_id)
      setBanner({ tone: 'success', message })
      return session.session_id
    } catch (error) {
      setBanner({ tone: 'error', message: toUserMessage(error) })
      return null
    }
  }

  async function handleSubmit(question: string) {
    if (!sessionId) {
      setBanner({ tone: 'error', message: 'The session is not ready yet. Please try again.' })
      return
    }

    const userMessage: ChatMessage = { id: messageId(), role: 'user', content: question }
    setMessages((current) => [...current, userMessage])
    setIsLoading(true)
    setBanner({ tone: 'info', message: 'Searching the Barbie PDF and preparing an answer…' })

    try {
      await submitQuestionWithRecovery(sessionId, question)
    } catch (error) {
      setBanner({ tone: 'error', message: toUserMessage(error) })
    } finally {
      setIsLoading(false)
    }
  }

  async function submitQuestionWithRecovery(activeSessionId: string, question: string) {
    try {
      const response = await submitQuery(activeSessionId, question)
      appendAssistantMessage(response.answer, response.evidence, response.processing_ms)
      if (response.status === 'insufficient_evidence') {
        setBanner({ tone: 'info', message: 'The PDF did not contain enough evidence for a confident answer.' })
      } else {
        setBanner({ tone: 'success', message: `Answer ready in ${response.processing_ms} ms.` })
      }
      return
    } catch (error) {
      if (error instanceof ApiError && isRecoverableSessionError(error)) {
        const newSessionId = await initializeSession('Your session expired, so a new conversation was started. Retrying your question…')
        if (!newSessionId) {
          throw error
        }

        const retryResponse = await submitQuery(newSessionId, question)
        appendAssistantMessage(retryResponse.answer, retryResponse.evidence, retryResponse.processing_ms)
        if (retryResponse.status === 'insufficient_evidence') {
          setBanner({ tone: 'info', message: 'A new session was started, but the PDF still did not contain enough evidence for a confident answer.' })
        } else {
          setBanner({ tone: 'success', message: `Your previous session expired, but the question was retried successfully in ${retryResponse.processing_ms} ms.` })
        }
        return
      }

      throw error
    }
  }

  function appendAssistantMessage(content: string, evidence: ChatMessage['evidence'], processingMs: number) {
    const assistantMessage: ChatMessage = {
      id: messageId(),
      role: 'assistant',
      content,
      evidence,
      processingMs,
    }
    setMessages((current) => [...current, assistantMessage])
  }

  async function handleReset() {
    if (sessionId) {
      try {
        await resetSession(sessionId)
      } catch {
        // ignore reset errors before creating a fresh session
      }
    }
    setMessages([])
    setSessionId(null)
    setBanner({ tone: 'info', message: 'Starting a fresh anonymous conversation…' })
    await initializeSession()
  }

  const subtitle = useMemo(
    () => 'Ask questions, inspect evidence snippets with page references, and continue the conversation within this session.',
    [],
  )

  return (
    <div className="chat-shell">
      <div className="chat-card">
        <div className="chat-header">
          <div>
            <h1 className="chat-title">Conversational Barbie PDF Assistant</h1>
            <p className="chat-subtitle">{subtitle}</p>
          </div>
          <NewConversationButton disabled={isLoading} onReset={handleReset} />
        </div>

        {banner ? <ChatStatusBanner tone={banner.tone} message={banner.message} /> : null}

        <div className="message-list">
          {messages.length === 0 ? (
            <div className="message assistant">
              <div className="message-meta">Assistant</div>
              <div>Ask a question about the Barbie PDF to get started.</div>
            </div>
          ) : null}
          {messages.map((message) => (
            <div className={`message ${message.role}`} key={message.id}>
              <div className="message-meta">
                {message.role === 'user' ? 'You' : 'Assistant'}
                {message.processingMs ? ` • ${message.processingMs} ms` : ''}
              </div>
              <div>{message.content}</div>
              {message.role === 'assistant' ? <EvidenceList evidence={message.evidence ?? []} /> : null}
            </div>
          ))}
        </div>

        <ChatComposer disabled={isLoading || !sessionId} onSubmit={handleSubmit} />
      </div>
    </div>
  )
}

function toUserMessage(error: unknown): string {
  if (error instanceof ApiError) {
    if (error.payload.error_code === 'rate_limited' && error.payload.retry_after_seconds) {
      return `Too many requests. Try again in ${error.payload.retry_after_seconds} seconds.`
    }
    if (error.payload.error_code === 'document_unavailable') {
      return 'The Barbie PDF is unavailable or unreadable right now.'
    }
    if (isRecoverableSessionError(error)) {
      return 'Your session expired or was reset. Please try your question again.'
    }
    return error.payload.message
  }

  return 'Something went wrong while contacting the assistant.'
}

function isRecoverableSessionError(error: ApiError) {
  return error.payload.error_code === 'session_not_found' || error.payload.error_code === 'session_expired'
}
