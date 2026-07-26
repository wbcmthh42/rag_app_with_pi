import type { EvidenceItem } from '../../../types/chat'

interface EvidenceListProps {
  evidence: EvidenceItem[]
}

export default function EvidenceList({ evidence }: EvidenceListProps) {
  if (!evidence.length) return null

  return (
    <ul className="evidence-list">
      {evidence.map((item, index) => (
        <li className="evidence-item" key={`${item.page_number}-${index}`}>
          <strong>Page {item.page_number}</strong>
          <div>{item.snippet_text}</div>
        </li>
      ))}
    </ul>
  )
}
