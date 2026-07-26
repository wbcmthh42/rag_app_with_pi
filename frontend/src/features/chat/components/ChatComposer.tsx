import { FormEvent, useState } from 'react'

interface ChatComposerProps {
  disabled?: boolean
  onSubmit: (question: string) => Promise<void> | void
}

export default function ChatComposer({ disabled = false, onSubmit }: ChatComposerProps) {
  const [question, setQuestion] = useState('')
  const [error, setError] = useState<string | null>(null)

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    const trimmed = question.trim()
    if (!trimmed) {
      setError('Please enter a meaningful question before submitting.')
      return
    }

    setError(null)
    await onSubmit(trimmed)
    setQuestion('')
  }

  return (
    <form className="composer" onSubmit={handleSubmit}>
      <textarea
        value={question}
        disabled={disabled}
        onChange={(event) => {
          setQuestion(event.target.value)
          if (error) setError(null)
        }}
        placeholder="Ask a question about the Barbie PDF..."
      />
      <div className="composer-footer">
        <div>{error ? <span style={{ color: '#b91c1c' }}>{error}</span> : <span>Answers stay grounded in the Barbie PDF.</span>}</div>
        <div className="composer-actions">
          <button className="primary-button" type="submit" disabled={disabled}>
            {disabled ? 'Working…' : 'Ask'}
          </button>
        </div>
      </div>
    </form>
  )
}
