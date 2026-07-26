interface ChatStatusBannerProps {
  tone: 'info' | 'error' | 'success'
  message: string
}

export default function ChatStatusBanner({ tone, message }: ChatStatusBannerProps) {
  return <div className={`banner ${tone}`}>{message}</div>
}
