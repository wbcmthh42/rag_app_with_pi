interface NewConversationButtonProps {
  disabled?: boolean
  onReset: () => Promise<void> | void
}

export default function NewConversationButton({ disabled = false, onReset }: NewConversationButtonProps) {
  return (
    <button className="secondary-button" type="button" disabled={disabled} onClick={() => void onReset()}>
      New conversation
    </button>
  )
}
