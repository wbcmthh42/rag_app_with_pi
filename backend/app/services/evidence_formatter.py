from __future__ import annotations


def build_evidence_items(retrieved_chunks: list[dict[str, object]], limit: int = 3) -> list[dict[str, object]]:
    evidence: list[dict[str, object]] = []
    for item in retrieved_chunks[:limit]:
        text = str(item.get("text", "")).strip()
        snippet = text[:240].strip()
        if len(text) > 240:
            snippet = f"{snippet}…"
        evidence.append(
            {
                "page_number": int(item.get("page_number", 1)),
                "snippet_text": snippet,
                "retrieval_score": item.get("retrieval_score"),
            }
        )
    return evidence
